using System.Data;
using System.Globalization;
using SerenityQuantResearch.Administration;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Research.Endpoints;

[Route("Services/Research/CompanyUniverse/[action]")]
[ConnectionKey("Default"), ServiceAuthorize(ResearchPermissionKeys.General)]
public sealed class CompanyUniverseEndpoint : ServiceEndpoint
{
    [HttpPost]
    public CompanyUniverseResponse List(IDbConnection connection, CompanyUniverseRequest request,
        [FromServices] ICompanyUniverseService service)
    {
        ArgumentNullException.ThrowIfNull(request);
        return service.List(connection, request);
    }

    [HttpPost]
    public CompanyResearchResponse Retrieve(IDbConnection connection, CompanyResearchRequest request,
        [FromServices] ICompanyUniverseService service)
    {
        ArgumentNullException.ThrowIfNull(request);
        return service.Retrieve(connection, request.CompanyId);
    }

    [HttpPost]
    public ChainNodeResearchResponse RetrieveChainNode(IDbConnection connection, ChainNodeResearchRequest request,
        [FromServices] ICompanyUniverseService service)
    {
        ArgumentNullException.ThrowIfNull(request);
        return service.RetrieveChainNode(connection, request.ChainNodeId);
    }
}

[Route("Services/Research/CompanyExposure/[action]")]
[ConnectionKey("Default"), ServiceAuthorize(ResearchPermissionKeys.Review)]
public sealed class CompanyExposureEndpoint : ServiceEndpoint
{
    [HttpPost]
    public ServiceResponse Update(IUnitOfWork uow, CompanyExposureUpdateRequest request,
        [FromServices] ICompanyUniverseService service, [FromServices] IUserAccessor userAccessor)
    {
        ArgumentNullException.ThrowIfNull(request);
        var actorId = int.Parse(userAccessor.User?.GetIdentifier() ??
            throw new ValidationError("NotAuthenticated", "A human research reviewer must be authenticated."),
            CultureInfo.InvariantCulture);
        var actor = uow.Connection.ById<UserRow>(actorId) ??
            throw new ValidationError("ResearchActorNotFound", "The authenticated research actor was not found.");
        var actorIsHumanReviewer = string.Equals(actor.ActorType, UserActorTypes.Human, StringComparison.Ordinal);
        service.UpdateExposure(uow, request, actorId, actorIsHumanReviewer);
        return new ServiceResponse();
    }
}
