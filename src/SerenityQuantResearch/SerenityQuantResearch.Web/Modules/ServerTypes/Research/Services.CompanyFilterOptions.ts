import { ResearchNamedLink } from "./Services.ResearchNamedLink";

export interface CompanyFilterOptions {
    Parts?: ResearchNamedLink[];
    ChainNodes?: ResearchNamedLink[];
    Roles?: string[];
    Exchanges?: string[];
    CountriesRegions?: string[];
    UniverseLayers?: string[];
    CoveragePriorities?: string[];
    VerificationStates?: string[];
    EvidenceCoverageStates?: string[];
    FreshnessStates?: string[];
}