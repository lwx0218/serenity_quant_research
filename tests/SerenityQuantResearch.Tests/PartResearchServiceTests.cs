using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Serenity.Data;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Tests;

public sealed class PartResearchServiceTests
{
    [Fact]
    public void Catalog_and_every_seeded_part_resolve_through_part_research_service()
    {
        using var factory = new ResearchApplicationFactory();
        using var scope = factory.Services.CreateScope();
        var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
        var service = scope.ServiceProvider.GetRequiredService<IPartResearchService>();
        using var connection = connections.NewByKey("Default");

        var catalog = service.ListParts(connection);
        Assert.Equal(9, catalog.Modules.Count);
        Assert.Equal(21, catalog.Modules.Sum(module => module.Parts.Count));
        Assert.All(catalog.Modules, module => Assert.NotEmpty(module.Parts));

        foreach (var summary in catalog.Modules.SelectMany(module => module.Parts))
        {
            var response = service.RetrieveCompleteChain(connection, summary.Id);
            Assert.Equal(summary.Id, response.Part.Id);
            Assert.Equal(summary.ModuleId, response.Part.ModuleId);
            Assert.NotEmpty(response.ChainNodes);
            Assert.NotEmpty(response.Boundaries);
            Assert.NotEmpty(response.UpstreamDownstream);
            Assert.NotEmpty(response.KeySpecifications);
            Assert.NotEmpty(response.Conclusions);
            Assert.NotEmpty(response.Risks);
            Assert.NotEmpty(response.StatusWarnings);
            Assert.NotEmpty(response.UnresolvedQuestions);
            Assert.Contains(response.Conclusions, item => item.State == "none");
            Assert.Contains(response.KeySpecifications, item => item.State == "unresolved");
        }

        var example = service.RetrieveCompleteChain(connection, "cpo.part.host-asic.switch-die");
        Assert.Contains(example.Companies, company =>
            company.CompanyId == "global.broadcom" && company.VerificationState == "candidate");
        Assert.Contains(example.Evidence, evidence =>
            evidence.EvidenceId == "EVD-2026-0001" && evidence.ReviewState == "draft");
        Assert.Contains(example.StatusWarnings, warning => warning.Contains("未审核证据"));
    }

    private sealed class ResearchApplicationFactory : WebApplicationFactory<Program>
    {
        private string DatabasePath { get; } = Path.Combine(Path.GetTempPath(), $"serenity-quant-research-p2-{Guid.NewGuid():N}.sqlite");

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
