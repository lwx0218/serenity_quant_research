import { fieldsProxy } from "@serenity-is/corelib";

export interface CompanyExposureRow {
    CompanyExposureId?: number;
    CompanyId?: number;
    PhysicalPartId?: number;
    IndustryChainNodeId?: number;
    Role?: string;
    Relevance?: string;
    Confidence?: string;
    VerificationState?: string;
    ScopeNote?: string;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class CompanyExposureRow {
    static readonly idProperty = 'CompanyExposureId';
    static readonly localTextPrefix = 'Research.CompanyExposure';
    static readonly deletePermission = 'Research:Review';
    static readonly insertPermission = 'Research:Review';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Review';

    static readonly Fields = fieldsProxy<CompanyExposureRow>();
}