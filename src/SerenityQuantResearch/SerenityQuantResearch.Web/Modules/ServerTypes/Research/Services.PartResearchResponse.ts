import { ServiceResponse } from "@serenity-is/corelib";
import { CompanyExposureSummary } from "./Services.CompanyExposureSummary";
import { EvidenceSummary } from "./Services.EvidenceSummary";
import { ResearchNamedLink } from "./Services.ResearchNamedLink";
import { ResearchPartSummary } from "./Services.ResearchPartSummary";
import { ResearchSectionSummary } from "./Services.ResearchSectionSummary";

export interface PartResearchResponse extends ServiceResponse {
    Part?: ResearchPartSummary;
    ChainNodes?: ResearchNamedLink[];
    Technologies?: ResearchNamedLink[];
    Boundaries?: ResearchSectionSummary[];
    UpstreamDownstream?: ResearchSectionSummary[];
    KeySpecifications?: ResearchSectionSummary[];
    Companies?: CompanyExposureSummary[];
    Evidence?: EvidenceSummary[];
    Conclusions?: ResearchSectionSummary[];
    Risks?: ResearchSectionSummary[];
    StatusWarnings?: string[];
    UnresolvedQuestions?: string[];
}