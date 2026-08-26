import { fieldsProxy } from "@serenity-is/corelib";

export interface ResearchConclusionRow {
    ResearchConclusionId?: number;
    StableId?: string;
    ThemeId?: number;
    Version?: number;
    Statement?: string;
    PublicationState?: string;
    Confidence?: string;
    TimeHorizon?: string;
    Risks?: string;
    InvalidationConditions?: string;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class ResearchConclusionRow {
    static readonly idProperty = 'ResearchConclusionId';
    static readonly nameProperty = 'Statement';
    static readonly localTextPrefix = 'Research.ResearchConclusion';
    static readonly deletePermission = 'Research:Publish';
    static readonly insertPermission = 'Research:Publish';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Publish';

    static readonly Fields = fieldsProxy<ResearchConclusionRow>();
}