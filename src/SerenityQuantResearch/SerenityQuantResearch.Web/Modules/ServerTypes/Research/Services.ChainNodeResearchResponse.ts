import { ServiceResponse } from "@serenity-is/corelib";
import { CompanyExposureSummary } from "./Services.CompanyExposureSummary";
import { ResearchNamedLink } from "./Services.ResearchNamedLink";

export interface ChainNodeResearchResponse extends ServiceResponse {
    Node?: ResearchNamedLink;
    Parts?: ResearchNamedLink[];
    Companies?: CompanyExposureSummary[];
    ResearchGaps?: string[];
}