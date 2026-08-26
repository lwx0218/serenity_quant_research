import { fieldsProxy } from "@serenity-is/corelib";

export interface CompanyExposureEvidenceRow {
    CompanyExposureEvidenceId?: number;
    CompanyExposureId?: number;
    EvidenceId?: number;
    InsertDate?: string;
    InsertUserId?: number;
}

export abstract class CompanyExposureEvidenceRow {
    static readonly idProperty = 'CompanyExposureEvidenceId';
    static readonly localTextPrefix = 'Research.CompanyExposureEvidence';
    static readonly deletePermission = 'Research:Review';
    static readonly insertPermission = 'Research:Review';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Review';

    static readonly Fields = fieldsProxy<CompanyExposureEvidenceRow>();
}