import { ServiceRequest } from "@serenity-is/corelib";

export interface CompanyExposureUpdateRequest extends ServiceRequest {
    ExposureId?: number;
    CompanyId?: string;
    PartId?: string;
    ChainNodeId?: string;
    Role?: string;
    Relevance?: string;
    Confidence?: string;
    VerificationState?: string;
    ScopeNote?: string;
}