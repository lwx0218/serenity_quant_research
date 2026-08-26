import { ServiceRequest } from "@serenity-is/corelib";

export interface PartResearchRequest extends ServiceRequest {
    PartId?: string;
}