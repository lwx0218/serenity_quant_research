import { WorkspaceObjectSummary } from "./Services.WorkspaceObjectSummary";

export interface WorkspaceTreeGroup {
    Name?: string;
    Items?: WorkspaceObjectSummary[];
}
