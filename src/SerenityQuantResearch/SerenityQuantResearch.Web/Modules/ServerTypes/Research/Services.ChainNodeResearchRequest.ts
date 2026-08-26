import { ServiceRequest } from "@serenity-is/corelib";

export interface ChainNodeResearchRequest extends ServiceRequest {
    ChainNodeId?: string;
}