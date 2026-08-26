import { fieldsProxy } from "@serenity-is/corelib";

export interface EventRow {
    EventId?: number;
    StableId?: string;
    CompanyId?: number;
    SourceDocumentId?: number;
    EventType?: string;
    Title?: string;
    EventTime?: string;
    Description?: string;
    InsertUserId?: number;
    InsertDate?: string;
    UpdateUserId?: number;
    UpdateDate?: string;
}

export abstract class EventRow {
    static readonly idProperty = 'EventId';
    static readonly nameProperty = 'Title';
    static readonly localTextPrefix = 'Research.Event';
    static readonly deletePermission = 'Research:Review';
    static readonly insertPermission = 'Research:Review';
    static readonly readPermission = 'Research:General';
    static readonly updatePermission = 'Research:Review';

    static readonly Fields = fieldsProxy<EventRow>();
}