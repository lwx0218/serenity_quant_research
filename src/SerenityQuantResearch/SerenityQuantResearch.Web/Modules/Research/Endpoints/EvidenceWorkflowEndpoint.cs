using System.Globalization;
using SerenityQuantResearch.Research.Services;

namespace SerenityQuantResearch.Research.Endpoints;

[Route("Services/Research/EvidenceWorkflow/[action]")]
[ConnectionKey("Default"), ServiceAuthorize(ResearchPermissionKeys.Review)]
public sealed class EvidenceWorkflowEndpoint : ServiceEndpoint
{
    [HttpPost]
    public ServiceResponse Transition(IUnitOfWork uow, EvidenceTransitionRequest request,
        [FromServices] IEvidenceWorkflowService service,
        [FromServices] IUserAccessor userAccessor)
    {
        ArgumentNullException.ThrowIfNull(request);
        if (request.EvidenceId is null)
            throw new ArgumentNullException(nameof(request.EvidenceId));
        var actorId = int.Parse(userAccessor.User?.GetIdentifier() ??
            throw new ValidationError("NotAuthenticated", "A human reviewer must be authenticated."),
            CultureInfo.InvariantCulture);
        service.Transition(uow, request.EvidenceId.Value, request.ToState, actorId, actorIsHumanReviewer: true);
        return new ServiceResponse();
    }
}
