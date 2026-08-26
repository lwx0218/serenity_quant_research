import { fieldsProxy } from "@serenity-is/corelib";

export interface ReportConclusionRow {
    ReportConclusionId?: number;
    ResearchReportId?: number;
    ResearchConclusionId?: number;
    ConclusionVersion?: number;
    InsertDate?: string;
    InsertUserId?: number;
}

export abstract class ReportConclusionRow {
    static readonly idProperty = 'ReportConclusionId';
    static readonly localTextPrefix = 'Research.ReportConclusion';
    static readonly deletePermission = 'Research:Publish';
    static readonly insertPermission = 'Research:Publish';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Publish';

    static readonly Fields = fieldsProxy<ReportConclusionRow>();
}