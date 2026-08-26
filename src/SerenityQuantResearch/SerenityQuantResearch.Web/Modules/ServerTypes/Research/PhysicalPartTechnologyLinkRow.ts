import { fieldsProxy } from "@serenity-is/corelib";

export interface PhysicalPartTechnologyLinkRow {
    PhysicalPartTechnologyLinkId?: number;
    PhysicalPartId?: number;
    TechnologyLinkId?: number;
    InsertDate?: string;
    InsertUserId?: number;
}

export abstract class PhysicalPartTechnologyLinkRow {
    static readonly idProperty = 'PhysicalPartTechnologyLinkId';
    static readonly localTextPrefix = 'Research.PhysicalPartTechnologyLink';
    static readonly deletePermission = 'Research:General';
    static readonly insertPermission = 'Research:General';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:General';

    static readonly Fields = fieldsProxy<PhysicalPartTechnologyLinkRow>();
}