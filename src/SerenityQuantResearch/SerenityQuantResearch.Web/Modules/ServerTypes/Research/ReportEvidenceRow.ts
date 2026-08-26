import { fieldsProxy } from "@serenity-is/corelib";

export interface ReportEvidenceRow {
    ReportEvidenceId?: number;
    ResearchReportId?: number;
    EvidenceId?: number;
    EvidenceVersion?: number;
    InsertDate?: string;
    InsertUserId?: number;
}

export abstract class ReportEvidenceRow {
    static readonly idProperty = 'ReportEvidenceId';
    static readonly localTextPrefix = 'Research.ReportEvidence';
    static readonly deletePermission = 'Research:Publish';
    static readonly insertPermission = 'Research:Publish';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Publish';

    static readonly Fields = fieldsProxy<ReportEvidenceRow>();
}