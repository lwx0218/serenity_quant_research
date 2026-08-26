import { ServiceOptions, ServiceRequest, serviceRequest } from "@serenity-is/corelib";
import { PartCatalogResponse } from "./Services.PartCatalogResponse";
import { PartResearchRequest } from "./Services.PartResearchRequest";
import { PartResearchResponse } from "./Services.PartResearchResponse";

export namespace PartResearchService {
    export const baseUrl = 'Research/PartResearch';

    export declare function ListParts(request: ServiceRequest, onSuccess?: (response: PartCatalogResponse) => void, opt?: ServiceOptions<any>): PromiseLike<PartCatalogResponse>;
    export declare function RetrieveCompleteChain(request: PartResearchRequest, onSuccess?: (response: PartResearchResponse) => void, opt?: ServiceOptions<any>): PromiseLike<PartResearchResponse>;

    export const Methods = {
        ListParts: "Research/PartResearch/ListParts",
        RetrieveCompleteChain: "Research/PartResearch/RetrieveCompleteChain"
    } as const;

    [
        'ListParts',
        'RetrieveCompleteChain'
    ].forEach(x => {
        (<any>PartResearchService)[x] = function (r, s, o) {
            return serviceRequest(baseUrl + '/' + x, r, s, o);
        };
    });
}