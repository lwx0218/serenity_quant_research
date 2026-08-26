import { fieldsProxy } from "@serenity-is/corelib";

export interface SourceDocumentRow {
    SourceDocumentId?: number;
    StableId?: string;
    SourceLevel?: string;
    Publisher?: string;
    Title?: string;
    OriginalUrl?: string;
    PublicationTime?: string;
    CaptureTime?: string;
    ContentFingerprint?: string;
    RightsNote?: string;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class SourceDocumentRow {
    static readonly idProperty = 'SourceDocumentId';
    static readonly nameProperty = 'Title';
    static readonly localTextPrefix = 'Research.SourceDocument';
    static readonly deletePermission = 'Research:Review';
    static readonly insertPermission = 'Research:Review';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Review';

    static readonly Fields = fieldsProxy<SourceDocumentRow>();
}