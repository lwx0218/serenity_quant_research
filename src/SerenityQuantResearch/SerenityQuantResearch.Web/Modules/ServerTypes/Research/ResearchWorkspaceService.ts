import { ServiceOptions, serviceRequest } from "@serenity-is/corelib";
import { ResearchWorkspaceRequest } from "./Services.ResearchWorkspaceRequest";
import { ResearchWorkspaceResponse } from "./Services.ResearchWorkspaceResponse";

export namespace ResearchWorkspaceService {
    export const baseUrl = 'Research/ResearchWorkspace';

    export declare function Retrieve(request: ResearchWorkspaceRequest, onSuccess?: (response: ResearchWorkspaceResponse) => void, opt?: ServiceOptions<any>): PromiseLike<ResearchWorkspaceResponse>;

    export const Methods = {
        Retrieve: "Research/ResearchWorkspace/Retrieve"
    } as const;

    [
        'Retrieve'
    ].forEach(x => {
        (<any>ResearchWorkspaceService)[x] = function (r, s, o) {
            return serviceRequest(baseUrl + '/' + x, r, s, o);
        };
    });
}
