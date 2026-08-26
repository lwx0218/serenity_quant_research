using SerenityQuantResearch.Research.Domain;
using SerenityQuantResearch.Research.Entities;

namespace SerenityQuantResearch.Research.Services;

public sealed class EvidenceTransitionRequest : ServiceRequest
{
    public int? EvidenceId { get; set; }
    public string ToState { get; set; }
}

public interface IEvidenceWorkflowService
{
    void Transition(IUnitOfWork uow, int evidenceId, string toState, int actorUserId, bool actorIsHumanReviewer);
}

public sealed class EvidenceWorkflowService : IEvidenceWorkflowService
{
    public void Transition(IUnitOfWork uow, int evidenceId, string toState, int actorUserId, bool actorIsHumanReviewer)
    {
        ArgumentNullException.ThrowIfNull(uow);
        var evidence = uow.Connection.ById<EvidenceRow>(evidenceId) ??
            throw new ValidationError("EvidenceNotFound", $"Evidence '{evidenceId}' was not found.");

        EvidenceReviewPolicy.EnsureTransition(evidence.ReviewState, toState, actorIsHumanReviewer);
        var reviewed = toState is EvidenceReviewStates.Reviewed or EvidenceReviewStates.Rejected;
        uow.Connection.UpdateById(new EvidenceRow
        {
            EvidenceId = evidenceId,
            ReviewState = toState,
            ReviewedBy = reviewed ? actorUserId : null,
            ReviewedAt = reviewed ? DateTime.UtcNow : null,
            UpdateDate = DateTime.UtcNow,
            UpdateUserId = actorUserId
        }, ExpectedRows.One);
    }
}
