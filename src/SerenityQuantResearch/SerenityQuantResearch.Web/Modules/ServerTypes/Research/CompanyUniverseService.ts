import { ServiceOptions, serviceRequest } from "@serenity-is/corelib";
import { ChainNodeResearchRequest } from "./Services.ChainNodeResearchRequest";
import { ChainNodeResearchResponse } from "./Services.ChainNodeResearchResponse";
import { CompanyResearchRequest } from "./Services.CompanyResearchRequest";
import { CompanyResearchResponse } from "./Services.CompanyResearchResponse";
import { CompanyUniverseRequest } from "./Services.CompanyUniverseRequest";
import { CompanyUniverseResponse } from "./Services.CompanyUniverseResponse";

export namespace CompanyUniverseService {
    export const baseUrl = 'Research/CompanyUniverse';

    export declare function List(request: CompanyUniverseRequest, onSuccess?: (response: CompanyUniverseResponse) => void, opt?: ServiceOptions<any>): PromiseLike<CompanyUniverseResponse>;
    export declare function Retrieve(request: CompanyResearchRequest, onSuccess?: (response: CompanyResearchResponse) => void, opt?: ServiceOptions<any>): PromiseLike<CompanyResearchResponse>;
    export declare function RetrieveChainNode(request: ChainNodeResearchRequest, onSuccess?: (response: ChainNodeResearchResponse) => void, opt?: ServiceOptions<any>): PromiseLike<ChainNodeResearchResponse>;

    export const Methods = {
        List: "Research/CompanyUniverse/List",
        Retrieve: "Research/CompanyUniverse/Retrieve",
        RetrieveChainNode: "Research/CompanyUniverse/RetrieveChainNode"
    } as const;

    [
        'List',
        'Retrieve',
        'RetrieveChainNode'
    ].forEach(x => {
        (<any>CompanyUniverseService)[x] = function (r, s, o) {
            return serviceRequest(baseUrl + '/' + x, r, s, o);
        };
    });
}