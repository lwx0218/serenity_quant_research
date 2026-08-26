import { ServiceRequest } from "@serenity-is/corelib";

export interface CompanyResearchRequest extends ServiceRequest {
    CompanyId?: string;
}