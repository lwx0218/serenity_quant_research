import { ResearchPartSummary } from "./Services.ResearchPartSummary";

export interface ResearchModuleSummary {
    Id?: string;
    Name?: string;
    SortOrder?: number;
    Parts?: ResearchPartSummary[];
}