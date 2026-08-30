using System.Data;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Research.Endpoints;

[Route("Services/Research/ResearchWorkspace/[action]")]
[ConnectionKey("Default"), ServiceAuthorize(ResearchPermissionKeys.General)]
public sealed class ResearchWorkspaceEndpoint : ServiceEndpoint
{
    [HttpPost]
    public ResearchWorkspaceResponse Retrieve(IDbConnection connection, ResearchWorkspaceRequest request,
        [FromServices] IResearchWorkspaceService service)
    {
        ArgumentNullException.ThrowIfNull(request);
        return service.Retrieve(connection, request);
    }
}
