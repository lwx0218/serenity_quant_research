import { CompanyEvidenceSummary } from "./Services.CompanyEvidenceSummary";
import { ResearchNamedLink } from "./Services.ResearchNamedLink";

export interface CompanyExposureDetail {
    ExposureId?: number;
    Part?: ResearchNamedLink;
    ChainNode?: ResearchNamedLink;
    Role?: string;
    Relevance?: string;
    Confidence?: string;
    VerificationState?: string;
    ScopeNote?: string;
    SupportingEvidence?: CompanyEvidenceSummary[];
    ContradictingEvidence?: CompanyEvidenceSummary[];
    ContextEvidence?: CompanyEvidenceSummary[];
    MeetsVerifiedPolicy?: boolean;
    InsertDate?: string;
    InsertUserId?: number;
    UpdateDate?: string;
    UpdateUserId?: number;
}