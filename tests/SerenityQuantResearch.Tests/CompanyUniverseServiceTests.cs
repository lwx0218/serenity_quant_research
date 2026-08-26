using System.Data;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Serenity.Data;
using Serenity.Services;
using SerenityQuantResearch.Research.Entities;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Tests;

public sealed class CompanyUniverseServiceTests
{
    private static readonly DateTime AsOf = new(2026, 8, 25, 0, 0, 0, DateTimeKind.Utc);

    [Fact]
    public void All_20_seeded_companies_resolve_with_stable_identity_and_explicit_gaps()
    {
        using var context = TestContext.Create();
        var response = context.Service.List(context.Connection, new CompanyUniverseRequest(), AsOf);

        Assert.Equal(20, response.TotalCount);
        Assert.Equal(20, response.Companies.Count);
        Assert.Equal(20, response.Companies.Select(x => x.CompanyId).Distinct(StringComparer.Ordinal).Count());
        Assert.Equal(8, response.Companies.Count(x => x.UniverseLayer == "global_anchor"));
        Assert.Equal(12, response.Companies.Count(x => x.UniverseLayer == "a_share_focus"));
        Assert.Equal(19, response.Companies.Count(x => x.VerificationStates.SequenceEqual(["unmapped"])));

        foreach (var summary in response.Companies)
        {
            var detail = context.Service.Retrieve(context.Connection, summary.CompanyId, AsOf);
            Assert.Equal(summary.CompanyId, detail.Company.CompanyId);
            Assert.False(string.IsNullOrWhiteSpace(detail.Company.Name));
            Assert.False(string.IsNullOrWhiteSpace(detail.Company.UniverseLayer));
            Assert.False(string.IsNullOrWhiteSpace(detail.Company.CoveragePriority));
            Assert.NotEmpty(detail.ResearchGaps);
        }
    }

    [Theory]
    [InlineData("PartId", "cpo.part.host-asic.switch-die", 1)]
    [InlineData("ChainNodeId", "cpo.chain.asic", 1)]
    [InlineData("Role", "chip_vendor", 1)]
    [InlineData("Exchange", "NASDAQ", 6)]
    [InlineData("CountryRegion", "中国", 12)]
    [InlineData("UniverseLayer", "global_anchor", 8)]
    [InlineData("CoveragePriority", "core", 8)]
    [InlineData("VerificationState", "candidate", 1)]
    [InlineData("VerificationState", "unmapped", 19)]
    [InlineData("EvidenceCoverage", "unreviewed", 1)]
    [InlineData("EvidenceCoverage", "none", 19)]
    [InlineData("Freshness", "fresh", 0)]
    [InlineData("Freshness", "unknown", 20)]
    public void Filters_use_explicit_company_exposure_and_evidence_relationships(string field, string value, int expected)
    {
        using var context = TestContext.Create();
        var request = new CompanyUniverseRequest();
        typeof(CompanyUniverseRequest).GetProperty(field)!.SetValue(request, value);

        var response = context.Service.List(context.Connection, request, AsOf);
        Assert.Equal(expected, response.Companies.Count);
    }

    [Fact]
    public void Search_does_not_create_relationships_and_only_matches_identity_fields()
    {
        using var context = TestContext.Create();
        var result = context.Service.List(context.Connection, new CompanyUniverseRequest { SearchText = "300308" }, AsOf);
        var company = Assert.Single(result.Companies);
        Assert.Equal("cn.300308", company.CompanyId);
        Assert.Empty(company.Exposures);
        Assert.Equal("none", company.EvidenceCoverage);
    }

    [Theory]
    [InlineData("news", 90, "fresh")]
    [InlineData("news", 91, "review_due")]
    [InlineData("product_page", 180, "fresh")]
    [InlineData("product_page", 181, "review_due")]
    [InlineData("standard", 365, "fresh")]
    [InlineData("annual_report", 451, "review_due")]
    [InlineData("historical_financial", 2000, "historical")]
    [InlineData("", 1, "unknown")]
    public void Freshness_uses_explicit_contract_category_or_returns_unknown(string category, int ageDays, string expected)
    {
        var asOf = new DateTime(2026, 8, 25, 0, 0, 0, DateTimeKind.Utc);
        Assert.Equal(expected, CompanyUniverseService.CalculateFreshness(asOf.AddDays(-ageDays), asOf, category));
    }

    [Fact]
    public void Broadcom_candidate_and_draft_evidence_remain_visible_but_not_verified()
    {
        using var context = TestContext.Create();
        var detail = context.Service.Retrieve(context.Connection, "global.broadcom", AsOf);
        var exposure = Assert.Single(detail.Company.Exposures);
        var evidence = Assert.Single(exposure.ContextEvidence);

        Assert.Equal("candidate", exposure.VerificationState);
        Assert.False(exposure.MeetsVerifiedPolicy);
        Assert.Equal("EVD-2026-0001", evidence.EvidenceId);
        Assert.Equal(1, evidence.Version);
        Assert.Equal("draft", evidence.ReviewState);
        Assert.Equal("contextualizes", evidence.Stance);
        Assert.Empty(exposure.SupportingEvidence);
    }

    [Fact]
    public void Candidate_to_verified_is_rejected_server_side_and_does_not_mutate_seed_state()
    {
        using var context = TestContext.Create();
        var detail = context.Service.Retrieve(context.Connection, "global.broadcom", AsOf);
        var exposure = Assert.Single(detail.Company.Exposures);
        using var uow = new UnitOfWork(context.Connection);

        var request = new CompanyExposureUpdateRequest
        {
            ExposureId = exposure.ExposureId,
            CompanyId = "global.broadcom",
            PartId = exposure.Part.Id,
            ChainNodeId = exposure.ChainNode.Id,
            Role = exposure.Role,
            Relevance = exposure.Relevance,
            Confidence = exposure.Confidence,
            VerificationState = "verified",
            ScopeNote = exposure.ScopeNote
        };

        var error = Assert.Throws<ValidationError>(() => context.Service.UpdateExposure(uow, request, 1, actorIsHumanReviewer: true));
        Assert.Equal("VerifiedExposureEvidenceRequired", error.ErrorCode);
        var persisted = context.Connection.ById<CompanyExposureRow>(exposure.ExposureId);
        Assert.Equal("candidate", persisted.VerificationState);
        var seedEvidence = context.Connection.TryFirst<EvidenceRow>(q => q.SelectTableFields()
            .Where(EvidenceRow.Fields.StableId == "EVD-2026-0001"));
        Assert.Equal("draft", seedEvidence.ReviewState);
    }

    [Fact]
    public void Every_exposure_cross_navigation_target_resolves_by_stable_ID()
    {
        using var context = TestContext.Create();
        var companies = context.Service.List(context.Connection, new CompanyUniverseRequest(), AsOf).Companies;
        var partService = context.Scope.ServiceProvider.GetRequiredService<IPartResearchService>();

        foreach (var company in companies)
        {
            Assert.Equal(company.CompanyId, context.Service.Retrieve(context.Connection, company.CompanyId, AsOf).Company.CompanyId);
            foreach (var exposure in company.Exposures)
            {
                if (exposure.Part is not null)
                    Assert.Equal(exposure.Part.Id, partService.RetrieveCompleteChain(context.Connection, exposure.Part.Id).Part.Id);
                if (exposure.ChainNode is not null)
                    Assert.Equal(exposure.ChainNode.Id, context.Service.RetrieveChainNode(context.Connection, exposure.ChainNode.Id).Node.Id);
            }
        }

        var asic = context.Service.RetrieveChainNode(context.Connection, "cpo.chain.asic");
        Assert.Contains(asic.Parts, x => x.Id == "cpo.part.host-asic.switch-die");
        Assert.Contains(asic.Companies, x => x.CompanyId == "global.broadcom" && x.VerificationState == "candidate");
    }

    private sealed class TestContext : IDisposable
    {
        private readonly ResearchApplicationFactory factory;
        public IServiceScope Scope { get; }
        public IDbConnection Connection { get; }
        public ICompanyUniverseService Service { get; }

        private TestContext(ResearchApplicationFactory factory, IServiceScope scope, IDbConnection connection,
            ICompanyUniverseService service)
        {
            this.factory = factory;
            Scope = scope;
            Connection = connection;
            Service = service;
        }

        public static TestContext Create()
        {
            var factory = new ResearchApplicationFactory();
            var scope = factory.Services.CreateScope();
            var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
            var connection = connections.NewByKey("Default");
            var service = scope.ServiceProvider.GetRequiredService<ICompanyUniverseService>();
            return new TestContext(factory, scope, connection, service);
        }

        public void Dispose()
        {
            Connection.Dispose();
            Scope.Dispose();
            factory.Dispose();
        }
    }

    private sealed class ResearchApplicationFactory : WebApplicationFactory<Program>
    {
        private string DatabasePath { get; } = Path.Combine(Path.GetTempPath(), $"serenity-quant-research-p3-{Guid.NewGuid():N}.sqlite");

        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?>
                {
                    ["Data:Default:ConnectionString"] = $"Data Source={DatabasePath}",
                    ["Data:Default:ProviderName"] = "Microsoft.Data.Sqlite",
                    ["BackgroundJobs:Enabled"] = "false",
                    ["ClamAV:Enabled"] = "false",
                    ["StartNodeScripts"] = string.Empty
                }));
        }

        protected override void Dispose(bool disposing)
        {
            base.Dispose(disposing);
            SqliteConnection.ClearAllPools();
            if (File.Exists(DatabasePath))
                File.Delete(DatabasePath);
        }
    }
}
