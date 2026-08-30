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
using SerenityQuantResearch.Research.Domain;
using SerenityQuantResearch.Research.Entities;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Tests;

public sealed class EvidenceWorkflowEndpointPolicyTests
{
    [Theory]
    [InlineData(EvidenceReviewStates.Reviewed)]
    [InlineData(EvidenceReviewStates.Rejected)]
    public async Task Review_authorized_machine_account_cannot_finalize_evidence_review(string finalState)
    {
        using var factory = new ResearchApplicationFactory();
        var evidenceId = MoveSeedEvidenceToInReviewAsAdmin(factory);
        var machineUserId = AddMachineReviewer(factory);
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false });
        await Login(client, "machine-evidence-reviewer", "serenity");

        var response = await PostService(client, "/Services/Research/EvidenceWorkflow/Transition", new EvidenceTransitionRequest
        {
            EvidenceId = evidenceId,
            ToState = finalState
        });
        var body = await response.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        Assert.Contains("MachineEvidenceReviewDenied", body);
        var persisted = ReadEvidence(factory, evidenceId);
        Assert.Equal(EvidenceReviewStates.InReview, persisted.ReviewState);
        Assert.Null(persisted.ReviewedBy);
        Assert.Null(persisted.ReviewedAt);
        Assert.NotEqual(machineUserId, persisted.UpdateUserId);
        Assert.True(machineUserId > 1);
    }

    [Fact]
    public async Task Human_reviewer_can_finalize_evidence_review()
    {
        using var factory = new ResearchApplicationFactory();
        var evidenceId = MoveSeedEvidenceToInReviewAsAdmin(factory);
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false });
        await Login(client, "admin", "serenity");

        var response = await PostService(client, "/Services/Research/EvidenceWorkflow/Transition", new EvidenceTransitionRequest
        {
            EvidenceId = evidenceId,
            ToState = EvidenceReviewStates.Reviewed
        });

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var persisted = ReadEvidence(factory, evidenceId);
        Assert.Equal(EvidenceReviewStates.Reviewed, persisted.ReviewState);
        Assert.Equal(1, persisted.ReviewedBy);
        Assert.NotNull(persisted.ReviewedAt);
        Assert.Equal(1, persisted.UpdateUserId);
        Assert.NotNull(persisted.UpdateDate);
    }

    private static int MoveSeedEvidenceToInReviewAsAdmin(ResearchApplicationFactory factory)
    {
        using var scope = factory.Services.CreateScope();
        var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
        var workflow = scope.ServiceProvider.GetRequiredService<IEvidenceWorkflowService>();
        using var connection = connections.NewByKey("Default");
        var evidence = connection.TryFirst<EvidenceRow>(q => q.SelectTableFields()
            .Where(EvidenceRow.Fields.StableId == "EVD-2026-0001"));
        using var uow = new UnitOfWork(connection);
        workflow.Transition(uow, evidence.EvidenceId!.Value, EvidenceReviewStates.InReview, actorUserId: 1, actorIsHumanReviewer: true);
        uow.Commit();
        return evidence.EvidenceId.Value;
    }

    private static EvidenceRow ReadEvidence(ResearchApplicationFactory factory, int evidenceId)
    {
        using var scope = factory.Services.CreateScope();
        var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
        using var connection = connections.NewByKey("Default");
        return connection.ById<EvidenceRow>(evidenceId);
    }

    private static int AddMachineReviewer(ResearchApplicationFactory factory)
    {
        using var scope = factory.Services.CreateScope();
        var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
        using var connection = connections.NewByKey("Default");
        var admin = connection.ById<UserRow>(1);
        var now = new DateTime(2026, 8, 30, 0, 0, 0, DateTimeKind.Utc);
        var machineId = Convert.ToInt32(connection.InsertAndGetID(new UserRow
        {
            Username = "machine-evidence-reviewer",
            DisplayName = "Machine Evidence Reviewer Test Principal",
            Email = "machine-evidence@example.invalid",
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
        return machineId;
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
        private string DatabasePath { get; } = Path.Combine(Path.GetTempPath(), $"serenity-evidence-workflow-endpoint-{Guid.NewGuid():N}.sqlite");

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
