import { fieldsProxy } from "@serenity-is/corelib";

export interface EvidenceRow {
    EvidenceId?: number;
    StableId?: string;
    Version?: number;
    SourceDocumentId?: number;
    EventId?: number;
    CompanyId?: number;
    PhysicalPartId?: number;
    IndustryChainNodeId?: number;
    TechnologyLinkId?: number;
    Proposition?: string;
    OriginalQuote?: string;
    Locator?: string;
    Stance?: string;
    ReviewState?: string;
    ReviewedBy?: number;
    ReviewedAt?: string;
    AnalystNote?: string;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class EvidenceRow {
    static readonly idProperty = 'EvidenceId';
    static readonly nameProperty = 'Proposition';
    static readonly localTextPrefix = 'Research.Evidence';
    static readonly deletePermission = 'Research:Review';
    static readonly insertPermission = 'Research:Review';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Review';

    static readonly Fields = fieldsProxy<EvidenceRow>();
}