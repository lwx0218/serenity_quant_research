import { fieldsProxy } from "@serenity-is/corelib";

export interface IndustryChainNodeRow {
    IndustryChainNodeId?: number;
    StableId?: string;
    IndustryChainId?: number;
    ParentNodeId?: number;
    Name?: string;
    NodeType?: string;
    SortOrder?: number;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class IndustryChainNodeRow {
    static readonly idProperty = 'IndustryChainNodeId';
    static readonly nameProperty = 'Name';
    static readonly localTextPrefix = 'Research.IndustryChainNode';
    static readonly deletePermission = 'Research:General';
    static readonly insertPermission = 'Research:General';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:General';

    static readonly Fields = fieldsProxy<IndustryChainNodeRow>();
}