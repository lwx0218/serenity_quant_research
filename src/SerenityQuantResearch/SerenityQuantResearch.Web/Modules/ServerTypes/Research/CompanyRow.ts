import { fieldsProxy } from "@serenity-is/corelib";

export interface CompanyRow {
    CompanyId?: number;
    StableId?: string;
    Name?: string;
    EnglishName?: string;
    Ticker?: string;
    Exchange?: string;
    CountryRegion?: string;
    UniverseLayer?: string;
    CoveragePriority?: string;
    OfficialUrl?: string;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class CompanyRow {
    static readonly idProperty = 'CompanyId';
    static readonly nameProperty = 'Name';
    static readonly localTextPrefix = 'Research.Company';
    static readonly deletePermission = 'Research:General';
    static readonly insertPermission = 'Research:General';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:General';

    static readonly Fields = fieldsProxy<CompanyRow>();
}