import { fieldsProxy } from "@serenity-is/corelib";

export interface PhysicalPartIndustryChainNodeRow {
    PhysicalPartIndustryChainNodeId?: number;
    PhysicalPartId?: number;
    IndustryChainNodeId?: number;
    InsertDate?: string;
    InsertUserId?: number;
}

export abstract class PhysicalPartIndustryChainNodeRow {
    static readonly idProperty = 'PhysicalPartIndustryChainNodeId';
    static readonly localTextPrefix = 'Research.PhysicalPartIndustryChainNode';
    static readonly deletePermission = 'Research:General';
    static readonly insertPermission = 'Research:General';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:General';

    static readonly Fields = fieldsProxy<PhysicalPartIndustryChainNodeRow>();
}