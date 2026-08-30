using System.Globalization;
using SerenityQuantResearch.Administration;
using SerenityQuantResearch.Research.Domain;
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
        var actor = uow.Connection.ById<UserRow>(actorId) ??
            throw new ValidationError("ResearchActorNotFound", "The authenticated research actor was not found.");
        var actorIsHumanReviewer = string.Equals(actor.ActorType, UserActorTypes.Human, StringComparison.Ordinal);
        if (!actorIsHumanReviewer && request.ToState is EvidenceReviewStates.Reviewed or EvidenceReviewStates.Rejected)
            throw new ValidationError("MachineEvidenceReviewDenied",
                "Machine/service accounts cannot finalize evidence review.");
        service.Transition(uow, request.EvidenceId.Value, request.ToState, actorId, actorIsHumanReviewer);
        return new ServiceResponse();
    }
}
