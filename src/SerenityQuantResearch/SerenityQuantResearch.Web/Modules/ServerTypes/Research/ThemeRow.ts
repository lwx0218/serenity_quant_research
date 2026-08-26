import { fieldsProxy } from "@serenity-is/corelib";

export interface ThemeRow {
    ThemeId?: number;
    StableId?: string;
    Name?: string;
    Description?: string;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class ThemeRow {
    static readonly idProperty = 'ThemeId';
    static readonly nameProperty = 'Name';
    static readonly localTextPrefix = 'Research.Theme';
    static readonly deletePermission = 'Research:General';
    static readonly insertPermission = 'Research:General';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:General';

    static readonly Fields = fieldsProxy<ThemeRow>();
}