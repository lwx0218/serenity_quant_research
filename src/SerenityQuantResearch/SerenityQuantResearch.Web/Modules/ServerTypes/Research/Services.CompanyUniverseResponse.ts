import { ServiceResponse } from "@serenity-is/corelib";
import { CompanyFilterOptions } from "./Services.CompanyFilterOptions";
import { CompanyUniverseItem } from "./Services.CompanyUniverseItem";

export interface CompanyUniverseResponse extends ServiceResponse {
    Companies?: CompanyUniverseItem[];
    Filters?: CompanyFilterOptions;
    TotalCount?: number;
    AsOfUtc?: string;
}