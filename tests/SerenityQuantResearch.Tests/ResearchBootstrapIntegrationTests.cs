using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Serenity.Data;
using SerenityQuantResearch.Administration;
using SerenityQuantResearch.Research.Entities;
using SerenityQuantResearch.Research.Seed;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Tests;

public class ResearchBootstrapIntegrationTests
{
    [Fact]
    public async Task Bootstrap_is_idempotent_and_complete_chain_is_queryable()
    {
        using var factory = new ResearchApplicationFactory();
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions
        {
            AllowAutoRedirect = false
        });

        var root = await client.GetAsync("/");
        Assert.True(root.IsSuccessStatusCode);
        var login = await client.GetAsync("/Account/Login");
        Assert.Equal(System.Net.HttpStatusCode.Redirect, login.StatusCode);
        Assert.Equal("/", login.Headers.Location?.ToString());

        using var scope = factory.Services.CreateScope();
        var importer = scope.ServiceProvider.GetRequiredService<IResearchSeedImporter>();
        importer.ImportDefault();
        importer.ImportDefault();

        var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
        using var connection = connections.NewByKey("Default");
        Assert.Equal(9, connection.List<PhysicalModuleRow>(q => q.Select(PhysicalModuleRow.Fields.PhysicalModuleId)).Count);
        Assert.Equal(21, connection.List<PhysicalPartRow>(q => q.Select(PhysicalPartRow.Fields.PhysicalPartId)).Count);
        Assert.Equal(20, connection.List<CompanyRow>(q => q.Select(CompanyRow.Fields.CompanyId)).Count);
        Assert.Single(connection.List<CompanyExposureRow>(q => q.Select(CompanyExposureRow.Fields.CompanyExposureId)));
        Assert.Single(connection.List<EvidenceRow>(q => q.Select(EvidenceRow.Fields.EvidenceId)));
        Assert.Equal(UserActorTypes.Human, connection.ById<UserRow>(1).ActorType);

        var service = scope.ServiceProvider.GetRequiredService<IPartResearchService>();
        var response = service.RetrieveCompleteChain(connection, "cpo.part.host-asic.switch-die");

        Assert.Equal("cpo.mod.host-asic", response.Part.ModuleId);
        Assert.Contains(response.ChainNodes, x => x.Id == "cpo.chain.asic");
        Assert.Contains(response.Technologies, x => x.Id == "cpo.tech.high-speed-switching");
        Assert.Contains(response.Companies, x => x.CompanyId == "global.broadcom" && x.VerificationState == "candidate");
        Assert.Contains(response.Evidence, x => x.EvidenceId == "EVD-2026-0001" && x.ReviewState == "draft");

        var evidence = connection.TryFirst<EvidenceRow>(q => q.SelectTableFields()
            .Where(EvidenceRow.Fields.StableId == "EVD-2026-0001"));
        Assert.NotNull(evidence.InsertDate);
        Assert.Equal(1, evidence.InsertUserId);

        var workflow = scope.ServiceProvider.GetRequiredService<IEvidenceWorkflowService>();
        using (var uow = new UnitOfWork(connection))
        {
            workflow.Transition(uow, evidence.EvidenceId!.Value, "in_review", 1, actorIsHumanReviewer: false);
            workflow.Transition(uow, evidence.EvidenceId.Value, "reviewed", 1, actorIsHumanReviewer: true);
            uow.Commit();
        }
        var reviewed = connection.ById<EvidenceRow>(evidence.EvidenceId.Value);
        Assert.Equal("reviewed", reviewed.ReviewState);
        Assert.Equal(1, reviewed.ReviewedBy);
        Assert.NotNull(reviewed.ReviewedAt);
        Assert.NotNull(reviewed.UpdateDate);

        SqliteConnection.ClearAllPools();
    }

    private sealed class ResearchApplicationFactory : WebApplicationFactory<Program>
    {
        public string DatabasePath { get; } = Path.Combine(Path.GetTempPath(), $"serenity-quant-research-{Guid.NewGuid():N}.sqlite");

        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureAppConfiguration((_, configuration) =>
            {
                configuration.AddInMemoryCollection(new Dictionary<string, string?>
                {
                    ["Data:Default:ConnectionString"] = $"Data Source={DatabasePath}",
                    ["Data:Default:ProviderName"] = "Microsoft.Data.Sqlite",
                    ["BackgroundJobs:Enabled"] = "false",
                    ["ClamAV:Enabled"] = "false",
                    ["StartNodeScripts"] = string.Empty
                });
            });
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
