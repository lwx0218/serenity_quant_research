import { ServiceOptions, serviceRequest, ServiceResponse } from "@serenity-is/corelib";
import { CompanyExposureUpdateRequest } from "./Services.CompanyExposureUpdateRequest";

export namespace CompanyExposureService {
    export const baseUrl = 'Research/CompanyExposure';

    export declare function Update(request: CompanyExposureUpdateRequest, onSuccess?: (response: ServiceResponse) => void, opt?: ServiceOptions<any>): PromiseLike<ServiceResponse>;

    export const Methods = {
        Update: "Research/CompanyExposure/Update"
    } as const;

    [
        'Update'
    ].forEach(x => {
        (<any>CompanyExposureService)[x] = function (r, s, o) {
            return serviceRequest(baseUrl + '/' + x, r, s, o);
        };
    });
}