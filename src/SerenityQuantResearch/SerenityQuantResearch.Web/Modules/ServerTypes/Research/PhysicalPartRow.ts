import { fieldsProxy } from "@serenity-is/corelib";

export interface PhysicalPartRow {
    PhysicalPartId?: number;
    StableId?: string;
    PhysicalModuleId?: number;
    ParentPartId?: number;
    Name?: string;
    FunctionSummary?: string;
    ResearchStatus?: string;
    SortOrder?: number;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class PhysicalPartRow {
    static readonly idProperty = 'PhysicalPartId';
    static readonly nameProperty = 'Name';
    static readonly localTextPrefix = 'Research.PhysicalPart';
    static readonly deletePermission = 'Research:General';
    static readonly insertPermission = 'Research:General';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:General';

    static readonly Fields = fieldsProxy<PhysicalPartRow>();
}