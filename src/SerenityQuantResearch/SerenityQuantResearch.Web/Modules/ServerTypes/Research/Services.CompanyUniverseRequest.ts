import { ServiceRequest } from "@serenity-is/corelib";

export interface CompanyUniverseRequest extends ServiceRequest {
    SearchText?: string;
    PartId?: string;
    ChainNodeId?: string;
    Role?: string;
    Exchange?: string;
    CountryRegion?: string;
    UniverseLayer?: string;
    CoveragePriority?: string;
    VerificationState?: string;
    EvidenceCoverage?: string;
    Freshness?: string;
}