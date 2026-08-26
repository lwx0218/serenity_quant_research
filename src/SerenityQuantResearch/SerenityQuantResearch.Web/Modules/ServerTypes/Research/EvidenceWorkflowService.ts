import { ServiceOptions, serviceRequest, ServiceResponse } from "@serenity-is/corelib";
import { EvidenceTransitionRequest } from "./Services.EvidenceTransitionRequest";

export namespace EvidenceWorkflowService {
    export const baseUrl = 'Research/EvidenceWorkflow';

    export declare function Transition(request: EvidenceTransitionRequest, onSuccess?: (response: ServiceResponse) => void, opt?: ServiceOptions<any>): PromiseLike<ServiceResponse>;

    export const Methods = {
        Transition: "Research/EvidenceWorkflow/Transition"
    } as const;

    [
        'Transition'
    ].forEach(x => {
        (<any>EvidenceWorkflowService)[x] = function (r, s, o) {
            return serviceRequest(baseUrl + '/' + x, r, s, o);
        };
    });
}