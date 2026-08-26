using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Serenity.Data;
using SerenityQuantResearch.Administration;
using SerenityQuantResearch.Research;
using SerenityQuantResearch.Research.Entities;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Tests;

public sealed class CompanyExposureEndpointPolicyTests
{
    [Fact]
    public async Task Candidate_draft_to_verified_returns_structured_4xx_without_mutation()
    {
        using var factory = new ResearchApplicationFactory();
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false });
        await Login(client, "admin", "serenity");
        var request = BuildBroadcomUpdate(factory, "verified");

        var response = await PostService(client, "/Services/Research/CompanyExposure/Update", request);
        var body = await response.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        Assert.Contains("VerifiedExposureEvidenceRequired", body);
        AssertSeedState(factory, "candidate", "draft");
    }

    [Fact]
    public async Task Review_authorized_machine_account_is_denied_by_server_identity_even_with_eligible_evidence()
    {
        using var factory = new ResearchApplicationFactory();
        var machineUserId = AddMachineReviewerAndEligibleSupportingEvidence(factory);
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false });
        await Login(client, "machine-reviewer", "serenity");
        var request = BuildBroadcomUpdate(factory, "verified");

        var response = await PostService(client, "/Services/Research/CompanyExposure/Update", request);
        var body = await response.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        Assert.Contains("MachineExposureStateChangeDenied", body);
        AssertSeedState(factory, "candidate", "draft");
        Assert.True(machineUserId > 1);
    }

    private static CompanyExposureUpdateRequest BuildBroadcomUpdate(ResearchApplicationFactory factory, string state)
    {
        using var scope = factory.Services.CreateScope();
        var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
        using var connection = connections.NewByKey("Default");
        var exposure = connection.TryFirst<CompanyExposureRow>(q => q.SelectTableFields());
        var part = connection.ById<PhysicalPartRow>(exposure.PhysicalPartId!.Value);
        var node = connection.ById<IndustryChainNodeRow>(exposure.IndustryChainNodeId!.Value);
        return new CompanyExposureUpdateRequest
        {
            ExposureId = exposure.CompanyExposureId,
            CompanyId = "global.broadcom",
            PartId = part.StableId,
            ChainNodeId = node.StableId,
            Role = exposure.Role,
            Relevance = exposure.Relevance,
            Confidence = exposure.Confidence,
            VerificationState = state,
            ScopeNote = exposure.ScopeNote
        };
    }

    private static int AddMachineReviewerAndEligibleSupportingEvidence(ResearchApplicationFactory factory)
    {
        using var scope = factory.Services.CreateScope();
        var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
        using var connection = connections.NewByKey("Default");
        var admin = connection.ById<UserRow>(1);
        var now = new DateTime(2026, 8, 25, 0, 0, 0, DateTimeKind.Utc);
        var machineId = Convert.ToInt32(connection.InsertAndGetID(new UserRow
        {
            Username = "machine-reviewer",
            DisplayName = "Machine Reviewer Test Principal",
            Email = "machine@example.invalid",
            Source = "site",
            ActorType = UserActorTypes.Machine,
            PasswordHash = admin.PasswordHash,
            PasswordSalt = admin.PasswordSalt,
            IsActive = 1,
            InsertDate = now,
            InsertUserId = 1
        }));
        foreach (var permission in new[] { ResearchPermissionKeys.General, ResearchPermissionKeys.Review })
            connection.Insert(new UserPermissionRow { UserId = machineId, PermissionKey = permission, Granted = true });

        var company = connection.TryFirst<CompanyRow>(q => q.SelectTableFields()
            .Where(CompanyRow.Fields.StableId == "global.broadcom"));
        var exposure = connection.TryFirst<CompanyExposureRow>(q => q.SelectTableFields());
        var sourceId = Convert.ToInt32(connection.InsertAndGetID(new SourceDocumentRow
        {
            StableId = "test.source.reviewed-a",
            SourceLevel = "A",
            Publisher = "Test fixture publisher",
            Title = "Explicit endpoint policy fixture",
            OriginalUrl = "https://example.invalid/p3-policy-fixture",
            CaptureTime = now,
            RightsNote = "Temporary test metadata only.",
            InsertDate = now,
            InsertUserId = 1
        }));
        var evidenceId = Convert.ToInt32(connection.InsertAndGetID(new EvidenceRow
        {
            StableId = "TEST-P3-REVIEWED-A",
            Version = 1,
            SourceDocumentId = sourceId,
            CompanyId = company.CompanyId,
            PhysicalPartId = exposure.PhysicalPartId,
            IndustryChainNodeId = exposure.IndustryChainNodeId,
            Proposition = "Temporary explicit supporting fixture for machine-actor endpoint denial.",
            Locator = "test fixture",
            Stance = "supports",
            ReviewState = "reviewed",
            ReviewedBy = 1,
            ReviewedAt = now,
            AnalystNote = "Not seed research and never persisted outside the temporary test database.",
            InsertDate = now,
            InsertUserId = 1
        }));
        connection.Insert(new CompanyExposureEvidenceRow
        {
            CompanyExposureId = exposure.CompanyExposureId,
            EvidenceId = evidenceId,
            InsertDate = now,
            InsertUserId = 1
        });
        return machineId;
    }

    private static void AssertSeedState(ResearchApplicationFactory factory, string exposureState, string evidenceState)
    {
        using var scope = factory.Services.CreateScope();
        var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
        using var connection = connections.NewByKey("Default");
        var exposure = connection.TryFirst<CompanyExposureRow>(q => q.SelectTableFields());
        var seedEvidence = connection.TryFirst<EvidenceRow>(q => q.SelectTableFields()
            .Where(EvidenceRow.Fields.StableId == "EVD-2026-0001"));
        Assert.Equal(exposureState, exposure.VerificationState);
        Assert.Equal(evidenceState, seedEvidence.ReviewState);
    }

    private static async Task Login(HttpClient client, string username, string password)
    {
        var loginPage = await client.GetAsync("/Account/Login");
        loginPage.EnsureSuccessStatusCode();
        var token = ReadCsrfToken(loginPage);
        using var request = new HttpRequestMessage(HttpMethod.Post, "/Account/Login")
        {
            Content = JsonContent.Create(new { Username = username, Password = password })
        };
        request.Headers.Add("X-CSRF-TOKEN", token);
        var response = await client.SendAsync(request);
        response.EnsureSuccessStatusCode();
    }

    private static async Task<HttpResponseMessage> PostService(HttpClient client, string path, object payload)
    {
        var page = await client.GetAsync("/Research/Companies");
        page.EnsureSuccessStatusCode();
        using var request = new HttpRequestMessage(HttpMethod.Post, path) { Content = JsonContent.Create(payload) };
        request.Headers.Add("X-CSRF-TOKEN", ReadCsrfToken(page));
        return await client.SendAsync(request);
    }

    private static string ReadCsrfToken(HttpResponseMessage response)
    {
        var cookie = response.Headers.GetValues("Set-Cookie")
            .SelectMany(x => x.Split(',', StringSplitOptions.TrimEntries))
            .First(x => x.StartsWith("CSRF-TOKEN=", StringComparison.Ordinal));
        var value = cookie["CSRF-TOKEN=".Length..].Split(';')[0];
        return Uri.UnescapeDataString(value);
    }

    private sealed class ResearchApplicationFactory : WebApplicationFactory<Program>
    {
        private string DatabasePath { get; } = Path.Combine(Path.GetTempPath(), $"serenity-quant-research-p3-endpoint-{Guid.NewGuid():N}.sqlite");

        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureAppConfiguration((_, configuration) => configuration.AddInMemoryCollection(
                new Dictionary<string, string?>
                {
                    ["Data:Default:ConnectionString"] = $"Data Source={DatabasePath}",
                    ["Data:Default:ProviderName"] = "Microsoft.Data.Sqlite",
                    ["OpenAccess:Enabled"] = "false",
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
