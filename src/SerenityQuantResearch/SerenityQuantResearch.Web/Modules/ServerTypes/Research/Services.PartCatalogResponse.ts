import { ServiceResponse } from "@serenity-is/corelib";
import { ResearchModuleSummary } from "./Services.ResearchModuleSummary";

export interface PartCatalogResponse extends ServiceResponse {
    Modules?: ResearchModuleSummary[];
}