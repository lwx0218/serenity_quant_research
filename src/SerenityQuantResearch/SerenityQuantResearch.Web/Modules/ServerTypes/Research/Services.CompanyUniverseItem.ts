import { CompanyExposureDetail } from "./Services.CompanyExposureDetail";

export interface CompanyUniverseItem {
    CompanyId?: string;
    Name?: string;
    EnglishName?: string;
    Ticker?: string;
    Exchange?: string;
    CountryRegion?: string;
    UniverseLayer?: string;
    CoveragePriority?: string;
    OfficialUrl?: string;
    Exposures?: CompanyExposureDetail[];
    Roles?: string[];
    VerificationStates?: string[];
    EvidenceCoverage?: string;
    EvidenceCount?: number;
    ReviewedEvidenceCount?: number;
    Freshness?: string;
    LatestCaptureTime?: string;
    CoverageNote?: string;
    InsertDate?: string;
    InsertUserId?: number;
    UpdateDate?: string;
    UpdateUserId?: number;
}