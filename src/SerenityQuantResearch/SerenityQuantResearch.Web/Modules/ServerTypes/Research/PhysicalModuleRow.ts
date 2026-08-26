import { fieldsProxy } from "@serenity-is/corelib";

export interface PhysicalModuleRow {
    PhysicalModuleId?: number;
    StableId?: string;
    ThemeId?: number;
    Name?: string;
    Description?: string;
    SortOrder?: number;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class PhysicalModuleRow {
    static readonly idProperty = 'PhysicalModuleId';
    static readonly nameProperty = 'Name';
    static readonly localTextPrefix = 'Research.PhysicalModule';
    static readonly deletePermission = 'Research:General';
    static readonly insertPermission = 'Research:General';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:General';

    static readonly Fields = fieldsProxy<PhysicalModuleRow>();
}