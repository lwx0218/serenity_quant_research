namespace SerenityQuantResearch.Research.Domain;

public static class EvidenceReviewStates
{
    public const string Draft = "draft";
    public const string InReview = "in_review";
    public const string Reviewed = "reviewed";
    public const string Rejected = "rejected";
    public const string Superseded = "superseded";

    public static readonly IReadOnlySet<string> All = new HashSet<string>(StringComparer.Ordinal)
    {
        Draft, InReview, Reviewed, Rejected, Superseded
    };
}

public static class CompanyExposureStates
{
    public const string Discovery = "discovery";
    public const string Candidate = "candidate";
    public const string Verified = "verified";
    public const string Rejected = "rejected";
    public const string Stale = "stale";

    public static readonly IReadOnlySet<string> All = new HashSet<string>(StringComparer.Ordinal)
    {
        Discovery, Candidate, Verified, Rejected, Stale
    };
}

public sealed record ExposurePolicyEvidence(string ReviewState, string SourceLevel, string Stance, bool ReviewedByHuman);

public static class CompanyExposurePolicy
{
    public static readonly IReadOnlySet<string> Roles = new HashSet<string>(StringComparer.Ordinal)
    {
        "demand_owner", "platform_vendor", "chip_vendor", "component_vendor", "module_vendor",
        "substrate_pcb", "thermal_structure", "test_equipment", "system_vendor"
    };

    public static readonly IReadOnlySet<string> RelevanceStates = new HashSet<string>(StringComparer.Ordinal)
    {
        "direct", "adjacent", "industry_anchor", "context", "unknown"
    };

    public static readonly IReadOnlySet<string> ConfidenceStates = new HashSet<string>(StringComparer.Ordinal)
    {
        "low", "medium", "high"
    };

    public static bool HasReviewedSupportingEvidence(IEnumerable<ExposurePolicyEvidence> evidence) =>
        evidence?.Any(x => x.Stance == "supports" && x.ReviewState == EvidenceReviewStates.Reviewed &&
            x.ReviewedByHuman && (x.SourceLevel == "A" || x.SourceLevel == "B")) == true;

    public static void EnsureUpdate(string fromState, string toState, bool actorIsHumanReviewer,
        IEnumerable<ExposurePolicyEvidence> evidence)
    {
        if (!CompanyExposureStates.All.Contains(fromState) || !CompanyExposureStates.All.Contains(toState))
            throw new ValidationError("ExposureStateTransitionNotAllowed",
                $"Company exposure transition '{fromState}' -> '{toState}' is not allowed.");
        if (fromState != toState && !actorIsHumanReviewer)
            throw new ValidationError("MachineExposureStateChangeDenied",
                "Machine/service accounts cannot change company exposure verification state.");
        if (toState == CompanyExposureStates.Verified &&
            (!actorIsHumanReviewer || !HasReviewedSupportingEvidence(evidence)))
            throw new ValidationError("VerifiedExposureEvidenceRequired",
                "Verified exposure requires a human reviewer and supporting Level A/B evidence reviewed by a human reviewer.");
    }

    public static void ValidateFields(string role, string relevance, string confidence,
        string verificationState, string scopeNote)
    {
        if (!Roles.Contains(role))
            throw new ValidationError("InvalidExposureRole", $"Company exposure role '{role}' is not allowed.");
        if (!RelevanceStates.Contains(relevance))
            throw new ValidationError("InvalidExposureRelevance", $"Company exposure relevance '{relevance}' is not allowed.");
        if (!ConfidenceStates.Contains(confidence))
            throw new ValidationError("InvalidExposureConfidence", $"Company exposure confidence '{confidence}' is not allowed.");
        if (!CompanyExposureStates.All.Contains(verificationState))
            throw new ValidationError("InvalidExposureState", $"Company exposure state '{verificationState}' is not allowed.");
        if (string.IsNullOrWhiteSpace(scopeNote))
            throw new ValidationError("ScopeNoteRequired", "A scope note is required so the relationship boundary remains explicit.");
        if (scopeNote.Length > 2000)
            throw new ValidationError("ScopeNoteTooLong", "Scope note cannot exceed 2000 characters.");
    }
}

public static class ConclusionPublicationStates
{
    public const string Draft = "draft";
    public const string InReview = "in_review";
    public const string Published = "published";
    public const string Superseded = "superseded";
    public const string Withdrawn = "withdrawn";
}

public static class EvidenceReviewPolicy
{
    private static readonly IReadOnlyDictionary<string, IReadOnlySet<string>> AllowedTransitions =
        new Dictionary<string, IReadOnlySet<string>>(StringComparer.Ordinal)
        {
            [EvidenceReviewStates.Draft] = new HashSet<string>(StringComparer.Ordinal)
                { EvidenceReviewStates.InReview },
            [EvidenceReviewStates.InReview] = new HashSet<string>(StringComparer.Ordinal)
                { EvidenceReviewStates.Draft, EvidenceReviewStates.Reviewed, EvidenceReviewStates.Rejected },
            [EvidenceReviewStates.Reviewed] = new HashSet<string>(StringComparer.Ordinal)
                { EvidenceReviewStates.Superseded },
            [EvidenceReviewStates.Rejected] = new HashSet<string>(StringComparer.Ordinal),
            [EvidenceReviewStates.Superseded] = new HashSet<string>(StringComparer.Ordinal)
        };

    public static bool CanTransition(string from, string to, bool actorIsHumanReviewer)
    {
        if (!EvidenceReviewStates.All.Contains(from) || !EvidenceReviewStates.All.Contains(to))
            return false;

        if ((to == EvidenceReviewStates.Reviewed || to == EvidenceReviewStates.Rejected) &&
            !actorIsHumanReviewer)
            return false;

        return AllowedTransitions[from].Contains(to);
    }

    public static void EnsureTransition(string from, string to, bool actorIsHumanReviewer)
    {
        if (!CanTransition(from, to, actorIsHumanReviewer))
            throw new InvalidOperationException($"Evidence transition '{from}' -> '{to}' is not allowed.");
    }
}

public sealed record PublicationEvidence(
    string ReviewState,
    string SourceLevel,
    string Stance,
    bool DirectlySupportsProposition);

public static class ConclusionPublicationPolicy
{
    public static IReadOnlyList<string> Validate(
        IEnumerable<PublicationEvidence> evidence,
        bool companyExposureVerified,
        bool counterEvidenceSearchRecorded,
        string confidence,
        string timeHorizon,
        string risks,
        string invalidationConditions)
    {
        var items = evidence?.ToList() ?? [];
        var errors = new List<string>();
        var reviewed = items.Where(x => x.ReviewState == EvidenceReviewStates.Reviewed).ToList();
        var directA = reviewed.Any(x => x.SourceLevel == "A" && x.DirectlySupportsProposition);
        var independentBCount = reviewed.Count(x => x.SourceLevel == "B" && x.DirectlySupportsProposition);

        if (!directA && independentBCount < 2)
            errors.Add("Publication requires one reviewed Level A source or two reviewed Level B sources.");
        if (!companyExposureVerified)
            errors.Add("Company exposure must be verified before publication.");
        if (!counterEvidenceSearchRecorded)
            errors.Add("Counter-evidence search scope must be recorded.");
        if (string.IsNullOrWhiteSpace(confidence))
            errors.Add("Confidence is required.");
        if (string.IsNullOrWhiteSpace(timeHorizon))
            errors.Add("Time horizon is required.");
        if (string.IsNullOrWhiteSpace(risks))
            errors.Add("Risks are required.");
        if (string.IsNullOrWhiteSpace(invalidationConditions))
            errors.Add("Invalidation conditions are required.");
        if (reviewed.Any(x => x.SourceLevel == "C" && x.DirectlySupportsProposition))
            errors.Add("Level C evidence cannot support publication.");

        return errors;
    }
}
