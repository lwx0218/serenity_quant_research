import { fieldsProxy } from "@serenity-is/corelib";

export interface ConclusionEvidenceRow {
    ConclusionEvidenceId?: number;
    ResearchConclusionId?: number;
    EvidenceId?: number;
    EvidenceVersion?: number;
    InsertDate?: string;
    InsertUserId?: number;
}

export abstract class ConclusionEvidenceRow {
    static readonly idProperty = 'ConclusionEvidenceId';
    static readonly localTextPrefix = 'Research.ConclusionEvidence';
    static readonly deletePermission = 'Research:Publish';
    static readonly insertPermission = 'Research:Publish';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Publish';

    static readonly Fields = fieldsProxy<ConclusionEvidenceRow>();
}