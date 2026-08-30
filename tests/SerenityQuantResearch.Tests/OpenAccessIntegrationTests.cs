using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Serenity.Data;
using SerenityQuantResearch.Research.Entities;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Tests;

public sealed class OpenAccessIntegrationTests
{
    [Fact]
    public async Task Pages_and_read_admin_services_are_available_without_login()
    {
        using var factory = new OpenAccessApplicationFactory();
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false });

        foreach (var path in new[] { "/", "/Research/Cpo", "/Research/Companies", "/Administration/User" })
        {
            var response = await client.GetAsync(path);
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            Assert.DoesNotContain("/Account/Login", response.Headers.Location?.ToString() ?? string.Empty);
        }

        var page = await client.GetAsync("/Research/Companies");
        using var request = CreateJsonPost(page, "/Services/Administration/User/List", new { });
        var service = await client.SendAsync(request);
        Assert.Equal(HttpStatusCode.OK, service.StatusCode);
        Assert.Contains("admin", await service.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task Anonymous_open_access_can_reach_audited_write_endpoint_as_admin()
    {
        using var factory = new OpenAccessApplicationFactory();
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false });
        CompanyExposureUpdateRequest update;
        int exposureId;

        using (var scope = factory.Services.CreateScope())
        {
            var connections = scope.ServiceProvider.GetRequiredService<ISqlConnections>();
            using var connection = connections.NewByKey("Default");
            var exposure = connection.TryFirst<CompanyExposureRow>(q => q.SelectTableFields());
            var part = connection.ById<PhysicalPartRow>(exposure.PhysicalPartId!.Value);
            var node = connection.ById<IndustryChainNodeRow>(exposure.IndustryChainNodeId!.Value);
            exposureId = exposure.CompanyExposureId!.Value;
            update = new CompanyExposureUpdateRequest
            {
                ExposureId = exposureId,
                CompanyId = "global.broadcom",
                PartId = part.StableId,
                ChainNodeId = node.StableId,
                Role = exposure.Role,
                Relevance = exposure.Relevance,
                Confidence = exposure.Confidence,
                VerificationState = exposure.VerificationState,
                ScopeNote = exposure.ScopeNote + " Open-access integration audit check."
            };
        }

        var page = await client.GetAsync("/Research/Companies/global.broadcom");
        using var request = CreateJsonPost(page, "/Services/Research/CompanyExposure/Update", update);
        var response = await client.SendAsync(request);
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        using var verifyScope = factory.Services.CreateScope();
        var verifyConnections = verifyScope.ServiceProvider.GetRequiredService<ISqlConnections>();
        using var verify = verifyConnections.NewByKey("Default");
        var persisted = verify.ById<CompanyExposureRow>(exposureId);
        Assert.Equal(1, persisted.UpdateUserId);
        Assert.Contains("Open-access integration audit check", persisted.ScopeNote);
        Assert.Equal("candidate", persisted.VerificationState);
        var evidence = verify.TryFirst<EvidenceRow>(q => q.SelectTableFields()
            .Where(EvidenceRow.Fields.StableId == "EVD-2026-0001"));
        Assert.Equal("draft", evidence.ReviewState);
    }

    [Fact]
    public async Task Root_dashboard_redirect_and_admin_maintenance_routes_are_available()
    {
        using var factory = new OpenAccessApplicationFactory();
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false });

        var root = await client.GetAsync("/");
        Assert.Equal(HttpStatusCode.OK, root.StatusCode);
        Assert.Contains("cpo-explorer-app", await root.Content.ReadAsStringAsync());

        var dashboard = await client.GetAsync("/Dashboard");
        Assert.Equal(HttpStatusCode.Redirect, dashboard.StatusCode);
        Assert.Equal("/", dashboard.Headers.Location?.ToString());

        foreach (var path in new[] { "/Administration/User", "/Administration/Role" })
        {
            var response = await client.GetAsync(path);
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        }
    }

    [Fact]
    public async Task Login_page_is_bypassed_when_open_access_is_enabled()
    {
        using var factory = new OpenAccessApplicationFactory();
        using var client = factory.CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false });
        var response = await client.GetAsync("/Account/Login");
        Assert.Equal(HttpStatusCode.Redirect, response.StatusCode);
        Assert.Equal("/", response.Headers.Location?.ToString());
    }

    private static HttpRequestMessage CreateJsonPost(HttpResponseMessage page, string path, object payload)
    {
        var cookie = page.Headers.GetValues("Set-Cookie")
            .SelectMany(x => x.Split(',', StringSplitOptions.TrimEntries))
            .First(x => x.StartsWith("CSRF-TOKEN=", StringComparison.Ordinal));
        var token = Uri.UnescapeDataString(cookie["CSRF-TOKEN=".Length..].Split(';')[0]);
        var request = new HttpRequestMessage(HttpMethod.Post, path) { Content = JsonContent.Create(payload) };
        request.Headers.Add("X-CSRF-TOKEN", token);
        return request;
    }

    private sealed class OpenAccessApplicationFactory : WebApplicationFactory<Program>
    {
        private string DatabasePath { get; } = Path.Combine(Path.GetTempPath(), $"serenity-open-access-{Guid.NewGuid():N}.sqlite");

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
