import { ServiceRequest } from "@serenity-is/corelib";

export interface ResearchWorkspaceRequest extends ServiceRequest {
    ObjectType?: string;
    ObjectId?: string;
    Source?: string;
    ComponentId?: string;
    PartId?: string;
    ChainNodeId?: string;
    CompanyId?: string;
    View?: string;
}
