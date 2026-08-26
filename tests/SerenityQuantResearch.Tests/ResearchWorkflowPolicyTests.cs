using Serenity.Services;
using SerenityQuantResearch.Research.Domain;

namespace SerenityQuantResearch.Tests;

public class ResearchWorkflowPolicyTests
{
    [Theory]
    [InlineData(EvidenceReviewStates.Draft, EvidenceReviewStates.InReview, false, true)]
    [InlineData(EvidenceReviewStates.Draft, EvidenceReviewStates.Reviewed, true, false)]
    [InlineData(EvidenceReviewStates.InReview, EvidenceReviewStates.Reviewed, false, false)]
    [InlineData(EvidenceReviewStates.InReview, EvidenceReviewStates.Reviewed, true, true)]
    [InlineData(EvidenceReviewStates.Reviewed, EvidenceReviewStates.Superseded, true, true)]
    [InlineData(EvidenceReviewStates.Rejected, EvidenceReviewStates.Draft, true, false)]
    public void Evidence_transitions_follow_contract(string from, string to, bool humanReviewer, bool expected)
    {
        Assert.Equal(expected, EvidenceReviewPolicy.CanTransition(from, to, humanReviewer));
    }

    [Theory]
    [InlineData("candidate", "verified", false, "reviewed", "A", "supports", false)]
    [InlineData("candidate", "verified", true, "draft", "A", "supports", false)]
    [InlineData("candidate", "verified", true, "in_review", "A", "supports", false)]
    [InlineData("candidate", "verified", true, "rejected", "A", "supports", false)]
    [InlineData("candidate", "verified", true, "reviewed", "C", "supports", false)]
    [InlineData("candidate", "verified", true, "reviewed", "A", "contextualizes", false)]
    [InlineData("candidate", "verified", true, "reviewed", "A", "supports", true)]
    [InlineData("discovery", "candidate", false, "draft", "C", "contextualizes", false)]
    public void Exposure_transitions_require_human_reviewed_supporting_A_or_B_evidence(
        string from, string to, bool human, string reviewState, string sourceLevel, string stance, bool allowed)
    {
        var evidence = new[] { new ExposurePolicyEvidence(reviewState, sourceLevel, stance, ReviewedByHuman: true) };
        if (allowed)
            CompanyExposurePolicy.EnsureUpdate(from, to, human, evidence);
        else
            Assert.Throws<ValidationError>(() => CompanyExposurePolicy.EnsureUpdate(from, to, human, evidence));
    }

    [Fact]
    public void Machine_reviewed_evidence_cannot_support_verified_exposure()
    {
        var evidence = new[] { new ExposurePolicyEvidence("reviewed", "A", "supports", ReviewedByHuman: false) };
        var error = Assert.Throws<ValidationError>(() =>
            CompanyExposurePolicy.EnsureUpdate("candidate", "verified", true, evidence));
        Assert.Equal("VerifiedExposureEvidenceRequired", error.ErrorCode);
    }

    [Fact]
    public void Rejected_and_stale_exposure_states_remain_valid_auditable_states()
    {
        CompanyExposurePolicy.EnsureUpdate("candidate", "rejected", true, []);
        CompanyExposurePolicy.EnsureUpdate("verified", "stale", true, []);
        Assert.Contains("rejected", CompanyExposureStates.All);
        Assert.Contains("stale", CompanyExposureStates.All);
    }

    [Fact]
    public void Conclusion_requires_reviewed_primary_evidence_and_verified_exposure()
    {
        var errors = ConclusionPublicationPolicy.Validate(
            [new PublicationEvidence(EvidenceReviewStates.Reviewed, "A", "supports", true)],
            companyExposureVerified: true,
            counterEvidenceSearchRecorded: true,
            confidence: "medium",
            timeHorizon: "12 months",
            risks: "Technology and timing risk",
            invalidationConditions: "Official disclosure contradicts the mapping");

        Assert.Empty(errors);
    }

    [Fact]
    public void Level_C_and_unverified_exposure_cannot_publish()
    {
        var errors = ConclusionPublicationPolicy.Validate(
            [new PublicationEvidence(EvidenceReviewStates.Reviewed, "C", "supports", true)],
            companyExposureVerified: false,
            counterEvidenceSearchRecorded: false,
            confidence: "low",
            timeHorizon: "12 months",
            risks: "Unknown",
            invalidationConditions: "Unknown");

        Assert.Contains(errors, x => x.Contains("Level C"));
        Assert.Contains(errors, x => x.Contains("exposure"));
        Assert.Contains(errors, x => x.Contains("Counter-evidence"));
    }
}
