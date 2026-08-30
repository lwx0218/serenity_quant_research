import { ServiceResponse } from "@serenity-is/corelib";
import { ResearchSectionSummary } from "./Services.ResearchSectionSummary";
import { WorkspaceBacklink } from "./Services.WorkspaceBacklink";
import { WorkspaceEvidenceContext } from "./Services.WorkspaceEvidenceContext";
import { WorkspaceObjectSummary } from "./Services.WorkspaceObjectSummary";
import { WorkspaceTreeGroup } from "./Services.WorkspaceTreeGroup";

export interface ResearchWorkspaceResponse extends ServiceResponse {
    CurrentObject?: WorkspaceObjectSummary;
    SourcePath?: string[];
    Tree?: WorkspaceTreeGroup[];
    LinkedObjects?: WorkspaceObjectSummary[];
    Backlinks?: WorkspaceBacklink[];
    Evidence?: WorkspaceEvidenceContext[];
    Conclusions?: ResearchSectionSummary[];
    Gaps?: ResearchSectionSummary[];
    Status?: ResearchSectionSummary[];
    IsReadOnly?: boolean;
}
