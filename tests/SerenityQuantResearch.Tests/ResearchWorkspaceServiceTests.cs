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

public sealed class ResearchWorkspaceServiceTests
{
    [Fact]
    public void Component_workspace_projects_existing_links_status_and_read_only_gaps()
    {
        using var context = TestContext.Create();
        var response = context.Service.Retrieve(context.Connection, new ResearchWorkspaceRequest
        {
            ObjectType = "component",
            ObjectId = "cpo.mod.host-asic",
            Source = "cpo-explorer",
            ComponentId = "cpo.mod.host-asic",
            PartId = "cpo.part.host-asic.switch-die"
        });

        Assert.True(response.IsReadOnly);
        Assert.Equal("component", response.CurrentObject.ObjectType);
        Assert.Equal("cpo.mod.host-asic", response.CurrentObject.Id);
        Assert.Contains(response.SourcePath, x => x.Contains("CPO Explorer"));
        Assert.Contains(response.LinkedObjects, x => x.ObjectType == "part" && x.Id == "cpo.part.host-asic.switch-die");
        Assert.Contains(response.LinkedObjects, x => x.ObjectType == "technology" && x.Id == "cpo.tech.high-speed-switching");
        Assert.Contains(response.LinkedObjects, x => x.ObjectType == "chainNode" && x.Id == "cpo.chain.asic");
        Assert.Contains(response.LinkedObjects, x => x.ObjectType == "company" && x.Id == "global.broadcom");
        Assert.Contains(response.Evidence, x => x.EvidenceId == "EVD-2026-0001" && x.ReviewState == "draft");
        Assert.Contains(response.Backlinks, x => x.ObjectType == "company" && x.ObjectId == "global.broadcom" && x.State == "candidate");
        Assert.Contains(response.Conclusions, x => x.State == "none");
        Assert.Contains(response.Gaps, x => x.State == "unresolved" && x.Text.Contains("candidate", StringComparison.OrdinalIgnoreCase));
        Assert.Contains(response.Status, x => x.State == "read-only");
    }

    [Fact]
    public void Company_workspace_keeps_candidate_exposure_and_draft_evidence_separate_from_conclusions()
    {
        using var context = TestContext.Create();
        var response = context.Service.Retrieve(context.Connection, new ResearchWorkspaceRequest
        {
            ObjectType = "company",
            CompanyId = "global.broadcom",
            Source = "company-detail",
            ComponentId = "cpo.mod.host-asic",
            PartId = "cpo.part.host-asic.switch-die",
            ChainNodeId = "cpo.chain.asic"
        });

        Assert.True(response.IsReadOnly);
        Assert.Equal("company", response.CurrentObject.ObjectType);
        Assert.Equal("global.broadcom", response.CurrentObject.Id);
        Assert.Equal("Candidate", response.CurrentObject.State);
        Assert.Contains(response.SourcePath, x => x == "Broadcom Inc.");
        Assert.Contains(response.LinkedObjects, x => x.ObjectType == "part" && x.Id == "cpo.part.host-asic.switch-die");
        Assert.Contains(response.LinkedObjects, x => x.ObjectType == "chainNode" && x.Id == "cpo.chain.asic");
        Assert.Contains(response.Evidence, x => x.EvidenceId == "EVD-2026-0001" && x.ReviewState == "draft" && x.Stance == "contextualizes");
        Assert.Contains(response.Backlinks, x => x.Context.Contains("CompanyExposure", StringComparison.Ordinal));
        Assert.Contains(response.Status, x => x.Text.Contains("not upgraded to reviewed fact", StringComparison.Ordinal));
        Assert.Contains(response.Conclusions, x => x.State == "none");
        Assert.Contains(response.Gaps, x => x.Text.Contains("separate from verified conclusions", StringComparison.Ordinal));
    }

    [Fact]
    public void Linked_object_traversal_is_derived_and_does_not_mutate_existing_rows()
    {
        using var context = TestContext.Create();
        var before = context.CountRows();

        var part = context.Service.Retrieve(context.Connection, new ResearchWorkspaceRequest
        {
            ObjectType = "part",
            ObjectId = "cpo.part.host-asic.switch-die"
        });
        var companyLink = Assert.Single(part.LinkedObjects, x => x.ObjectType == "company" && x.Id == "global.broadcom");
        var company = context.Service.Retrieve(context.Connection, new ResearchWorkspaceRequest
        {
            ObjectType = companyLink.ObjectType,
            ObjectId = companyLink.Id
        });

        Assert.Contains(company.LinkedObjects, x => x.ObjectType == "part" && x.Id == "cpo.part.host-asic.switch-die");
        Assert.Equal(before, context.CountRows());
    }

    [Theory]
    [InlineData("global.broadcom", null, null, "company", "global.broadcom")]
    [InlineData(null, "cpo.part.host-asic.switch-die", null, "part", "cpo.part.host-asic.switch-die")]
    [InlineData(null, null, "cpo.chain.asic", "chainNode", "cpo.chain.asic")]
    public void Workspace_request_aliases_infer_object_type_before_stable_id_fallback(string? companyId, string? partId, string? chainNodeId,
        string expectedType, string expectedId)
    {
        using var context = TestContext.Create();
        var response = context.Service.Retrieve(context.Connection, new ResearchWorkspaceRequest
        {
            CompanyId = companyId,
            PartId = partId,
            ChainNodeId = chainNodeId
        });

        Assert.Equal(expectedType, response.CurrentObject.ObjectType);
        Assert.Equal(expectedId, response.CurrentObject.Id);
        Assert.True(response.IsReadOnly);
    }

    [Theory]
    [InlineData("note", "x", "WorkspaceObjectTypeUnsupported")]
    [InlineData("company", "missing.company", "WorkspaceCompanyNotFound")]
    public void Invalid_or_unsupported_workspace_objects_return_validation_errors(string objectType, string objectId, string expectedCode)
    {
        using var context = TestContext.Create();
        var error = Assert.Throws<ValidationError>(() => context.Service.Retrieve(context.Connection, new ResearchWorkspaceRequest
        {
            ObjectType = objectType,
            ObjectId = objectId
        }));
        Assert.Equal(expectedCode, error.ErrorCode);
    }

    [Fact]
    public async Task Workspace_page_route_is_available_without_writing_contracts()
    {
        using var context = TestContext.Create();
        using var client = context.Factory.CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false });

        var page = await client.GetAsync("/Research/Workspace?objectType=company&companyId=global.broadcom&source=company-detail");

        Assert.True(page.IsSuccessStatusCode);
        var html = await page.Content.ReadAsStringAsync();
        Assert.Contains("research-workspace-app", html);
        Assert.DoesNotContain("New Note", html, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("Graph", html, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("ResearchNote", html, StringComparison.OrdinalIgnoreCase);
    }

    private sealed class TestContext : IDisposable
    {
        public ResearchApplicationFactory Factory { get; }
        public IServiceScope Scope { get; }
        public ISqlConnections Connections { get; }
        public System.Data.IDbConnection Connection { get; }
        public IResearchWorkspaceService Service { get; }

        private TestContext(ResearchApplicationFactory factory, IServiceScope scope, ISqlConnections connections,
            System.Data.IDbConnection connection, IResearchWorkspaceService service)
        {
            Factory = factory;
            Scope = scope;
            Connections = connections;
            Connection = connection;
            Service = service;
        }

        public static TestContext Create()
        {
            var factory = new ResearchApplicationFactory();
            var scope = factory.Services.CreateScope();
            var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
            var connection = connections.NewByKey("Default");
            var service = scope.ServiceProvider.GetRequiredService<IResearchWorkspaceService>();
            return new TestContext(factory, scope, connections, connection, service);
        }

        public (int Modules, int Parts, int Companies, int Exposures, int Evidence, int Conclusions) CountRows() =>
        (
            Connection.List<PhysicalModuleRow>(q => q.Select(PhysicalModuleRow.Fields.PhysicalModuleId)).Count,
            Connection.List<PhysicalPartRow>(q => q.Select(PhysicalPartRow.Fields.PhysicalPartId)).Count,
            Connection.List<CompanyRow>(q => q.Select(CompanyRow.Fields.CompanyId)).Count,
            Connection.List<CompanyExposureRow>(q => q.Select(CompanyExposureRow.Fields.CompanyExposureId)).Count,
            Connection.List<EvidenceRow>(q => q.Select(EvidenceRow.Fields.EvidenceId)).Count,
            Connection.List<ResearchConclusionRow>(q => q.Select(ResearchConclusionRow.Fields.ResearchConclusionId)).Count
        );

        public void Dispose()
        {
            Connection.Dispose();
            Scope.Dispose();
            Factory.Dispose();
        }
    }

    private sealed class ResearchApplicationFactory : WebApplicationFactory<Program>
    {
        private string DatabasePath { get; } = Path.Combine(Path.GetTempPath(), $"serenity-quant-research-r6-{Guid.NewGuid():N}.sqlite");

        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?>
                {
                    ["Data:Default:ConnectionString"] = $"Data Source={DatabasePath}",
                    ["Data:Default:ProviderName"] = "Microsoft.Data.Sqlite",
                    ["OpenAccess:Enabled"] = "true",
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
