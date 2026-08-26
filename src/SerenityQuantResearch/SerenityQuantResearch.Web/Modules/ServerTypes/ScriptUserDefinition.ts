export interface ScriptUserDefinition {
    Username?: string;
    DisplayName?: string;
    IsAdmin?: boolean;
    ActorType?: string;
    Permissions?: { [key: string]: boolean };
}