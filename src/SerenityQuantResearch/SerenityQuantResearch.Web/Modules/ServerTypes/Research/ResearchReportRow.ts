import { fieldsProxy } from "@serenity-is/corelib";

export interface ResearchReportRow {
    ResearchReportId?: number;
    StableId?: string;
    ThemeId?: number;
    Version?: number;
    Title?: string;
    PublicationState?: string;
    GeneratedAt?: string;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class ResearchReportRow {
    static readonly idProperty = 'ResearchReportId';
    static readonly nameProperty = 'Title';
    static readonly localTextPrefix = 'Research.ResearchReport';
    static readonly deletePermission = 'Research:Publish';
    static readonly insertPermission = 'Research:Publish';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Publish';

    static readonly Fields = fieldsProxy<ResearchReportRow>();
}