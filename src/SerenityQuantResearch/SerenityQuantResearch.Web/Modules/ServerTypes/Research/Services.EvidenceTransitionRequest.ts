import { ServiceRequest } from "@serenity-is/corelib";

export interface EvidenceTransitionRequest extends ServiceRequest {
    EvidenceId?: number;
    ToState?: string;
}