import { ServiceResponse } from "@serenity-is/corelib";
import { CompanyConclusionSummary } from "./Services.CompanyConclusionSummary";
import { CompanyEventSummary } from "./Services.CompanyEventSummary";
import { CompanyEvidenceSummary } from "./Services.CompanyEvidenceSummary";
import { CompanyFilterOptions } from "./Services.CompanyFilterOptions";
import { CompanyUniverseItem } from "./Services.CompanyUniverseItem";

export interface CompanyResearchResponse extends ServiceResponse {
    Company?: CompanyUniverseItem;
    Events?: CompanyEventSummary[];
    EarningsFinancialEvidence?: CompanyEvidenceSummary[];
    CapexInvestmentEvidence?: CompanyEvidenceSummary[];
    Conclusions?: CompanyConclusionSummary[];
    SourcesAudit?: CompanyEvidenceSummary[];
    LinkOptions?: CompanyFilterOptions;
    ResearchGaps?: string[];
}