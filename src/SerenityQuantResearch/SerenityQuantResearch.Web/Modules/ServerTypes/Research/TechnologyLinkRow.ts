import { fieldsProxy } from "@serenity-is/corelib";

export interface TechnologyLinkRow {
    TechnologyLinkId?: number;
    StableId?: string;
    ThemeId?: number;
    Name?: string;
    Description?: string;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class TechnologyLinkRow {
    static readonly idProperty = 'TechnologyLinkId';
    static readonly nameProperty = 'Name';
    static readonly localTextPrefix = 'Research.TechnologyLink';
    static readonly deletePermission = 'Research:General';
    static readonly insertPermission = 'Research:General';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:General';

    static readonly Fields = fieldsProxy<TechnologyLinkRow>();
}