using System.Data;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Research.Endpoints;

[Route("Services/Research/PartResearch/[action]")]
[ConnectionKey("Default"), ServiceAuthorize(ResearchPermissionKeys.General)]
public sealed class PartResearchEndpoint : ServiceEndpoint
{
    [HttpPost]
    public PartCatalogResponse ListParts(IDbConnection connection,
        ServiceRequest request, [FromServices] IPartResearchService service)
    {
        ArgumentNullException.ThrowIfNull(request);
        return service.ListParts(connection);
    }

    [HttpPost]
    public PartResearchResponse RetrieveCompleteChain(IDbConnection connection,
        PartResearchRequest request, [FromServices] IPartResearchService service)
    {
        ArgumentNullException.ThrowIfNull(request);
        return service.RetrieveCompleteChain(connection, request.PartId);
    }
}
