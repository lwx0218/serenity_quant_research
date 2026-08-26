using FluentMigrator;

namespace SerenityQuantResearch.Migrations.DefaultDB;

[DefaultDB, MigrationKey(20260824_1000)]
public class DefaultDB_20260824_1000_ResearchDomain : AutoReversingMigration
{
    public override void Up()
    {
        Create.Table("Themes")
            .WithColumn("ThemeId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(100).NotNullable().Unique("UQ_Themes_StableId")
            .WithColumn("Name").AsString(200).NotNullable()
            .WithColumn("Description").AsString(2000).Nullable()
            .WithAuditColumns();

        Create.Table("IndustryChains")
            .WithColumn("IndustryChainId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(100).NotNullable().Unique("UQ_IndustryChains_StableId")
            .WithColumn("ThemeId").AsInt32().NotNullable().ForeignKey("FK_IndustryChains_ThemeId", "Themes", "ThemeId")
            .WithColumn("Name").AsString(200).NotNullable()
            .WithColumn("Description").AsString(2000).Nullable()
            .WithAuditColumns();

        Create.Table("IndustryChainNodes")
            .WithColumn("IndustryChainNodeId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(120).NotNullable().Unique("UQ_IndustryChainNodes_StableId")
            .WithColumn("IndustryChainId").AsInt32().NotNullable().ForeignKey("FK_IndustryChainNodes_ChainId", "IndustryChains", "IndustryChainId")
            .WithColumn("ParentNodeId").AsInt32().Nullable().ForeignKey("FK_IndustryChainNodes_ParentId", "IndustryChainNodes", "IndustryChainNodeId")
            .WithColumn("Name").AsString(200).NotNullable()
            .WithColumn("NodeType").AsString(40).NotNullable()
            .WithColumn("SortOrder").AsInt32().NotNullable().WithDefaultValue(0)
            .WithAuditColumns();

        Create.Table("PhysicalModules")
            .WithColumn("PhysicalModuleId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(120).NotNullable().Unique("UQ_PhysicalModules_StableId")
            .WithColumn("ThemeId").AsInt32().NotNullable().ForeignKey("FK_PhysicalModules_ThemeId", "Themes", "ThemeId")
            .WithColumn("Name").AsString(200).NotNullable()
            .WithColumn("Description").AsString(2000).Nullable()
            .WithColumn("SortOrder").AsInt32().NotNullable().WithDefaultValue(0)
            .WithAuditColumns();

        Create.Table("PhysicalParts")
            .WithColumn("PhysicalPartId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(140).NotNullable().Unique("UQ_PhysicalParts_StableId")
            .WithColumn("PhysicalModuleId").AsInt32().NotNullable().ForeignKey("FK_PhysicalParts_ModuleId", "PhysicalModules", "PhysicalModuleId")
            .WithColumn("ParentPartId").AsInt32().Nullable().ForeignKey("FK_PhysicalParts_ParentId", "PhysicalParts", "PhysicalPartId")
            .WithColumn("Name").AsString(200).NotNullable()
            .WithColumn("FunctionSummary").AsString(2000).Nullable()
            .WithColumn("ResearchStatus").AsString(40).NotNullable().WithDefaultValue("candidate")
            .WithColumn("SortOrder").AsInt32().NotNullable().WithDefaultValue(0)
            .WithAuditColumns();

        Create.Table("TechnologyLinks")
            .WithColumn("TechnologyLinkId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(120).NotNullable().Unique("UQ_TechnologyLinks_StableId")
            .WithColumn("ThemeId").AsInt32().NotNullable().ForeignKey("FK_TechnologyLinks_ThemeId", "Themes", "ThemeId")
            .WithColumn("Name").AsString(200).NotNullable()
            .WithColumn("Description").AsString(2000).Nullable()
            .WithAuditColumns();

        Create.Table("PhysicalPartTechnologyLinks")
            .WithColumn("PhysicalPartTechnologyLinkId").AsInt32().IdentityKey(this)
            .WithColumn("PhysicalPartId").AsInt32().NotNullable().ForeignKey("FK_PartTech_PartId", "PhysicalParts", "PhysicalPartId")
            .WithColumn("TechnologyLinkId").AsInt32().NotNullable().ForeignKey("FK_PartTech_TechId", "TechnologyLinks", "TechnologyLinkId")
            .WithColumn("InsertDate").AsDateTime().NotNullable()
            .WithColumn("InsertUserId").AsInt32().NotNullable();
        Create.Index("UQ_PartTech_Part_Tech").OnTable("PhysicalPartTechnologyLinks")
            .OnColumn("PhysicalPartId").Ascending().OnColumn("TechnologyLinkId").Ascending().WithOptions().Unique();

        Create.Table("PhysicalPartIndustryChainNodes")
            .WithColumn("PhysicalPartIndustryChainNodeId").AsInt32().IdentityKey(this)
            .WithColumn("PhysicalPartId").AsInt32().NotNullable().ForeignKey("FK_PartChain_PartId", "PhysicalParts", "PhysicalPartId")
            .WithColumn("IndustryChainNodeId").AsInt32().NotNullable().ForeignKey("FK_PartChain_NodeId", "IndustryChainNodes", "IndustryChainNodeId")
            .WithColumn("InsertDate").AsDateTime().NotNullable()
            .WithColumn("InsertUserId").AsInt32().NotNullable();
        Create.Index("UQ_PartChain_Part_Node").OnTable("PhysicalPartIndustryChainNodes")
            .OnColumn("PhysicalPartId").Ascending().OnColumn("IndustryChainNodeId").Ascending().WithOptions().Unique();

        Create.Table("Companies")
            .WithColumn("CompanyId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(100).NotNullable().Unique("UQ_Companies_StableId")
            .WithColumn("Name").AsString(240).NotNullable()
            .WithColumn("EnglishName").AsString(240).Nullable()
            .WithColumn("Ticker").AsString(40).Nullable()
            .WithColumn("Exchange").AsString(40).Nullable()
            .WithColumn("CountryRegion").AsString(80).NotNullable()
            .WithColumn("UniverseLayer").AsString(40).NotNullable()
            .WithColumn("CoveragePriority").AsString(40).NotNullable()
            .WithColumn("OfficialUrl").AsString(1000).Nullable()
            .WithAuditColumns();

        Create.Table("CompanyExposures")
            .WithColumn("CompanyExposureId").AsInt32().IdentityKey(this)
            .WithColumn("CompanyId").AsInt32().NotNullable().ForeignKey("FK_CompanyExposures_CompanyId", "Companies", "CompanyId")
            .WithColumn("PhysicalPartId").AsInt32().Nullable().ForeignKey("FK_CompanyExposures_PartId", "PhysicalParts", "PhysicalPartId")
            .WithColumn("IndustryChainNodeId").AsInt32().Nullable().ForeignKey("FK_CompanyExposures_NodeId", "IndustryChainNodes", "IndustryChainNodeId")
            .WithColumn("Role").AsString(80).NotNullable()
            .WithColumn("Relevance").AsString(40).NotNullable()
            .WithColumn("Confidence").AsString(20).NotNullable()
            .WithColumn("VerificationState").AsString(20).NotNullable()
            .WithColumn("ScopeNote").AsString(2000).Nullable()
            .WithAuditColumns();

        Create.Table("SourceDocuments")
            .WithColumn("SourceDocumentId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(120).NotNullable().Unique("UQ_SourceDocuments_StableId")
            .WithColumn("SourceLevel").AsString(1).NotNullable()
            .WithColumn("Publisher").AsString(240).NotNullable()
            .WithColumn("Title").AsString(500).NotNullable()
            .WithColumn("OriginalUrl").AsString(1500).NotNullable()
            .WithColumn("PublicationTime").AsDateTime().Nullable()
            .WithColumn("CaptureTime").AsDateTime().NotNullable()
            .WithColumn("ContentFingerprint").AsString(64).Nullable()
            .WithColumn("RightsNote").AsString(1000).Nullable()
            .WithAuditColumns();

        Create.Table("Events")
            .WithColumn("EventId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(120).NotNullable().Unique("UQ_Events_StableId")
            .WithColumn("CompanyId").AsInt32().Nullable().ForeignKey("FK_Events_CompanyId", "Companies", "CompanyId")
            .WithColumn("SourceDocumentId").AsInt32().Nullable().ForeignKey("FK_Events_SourceId", "SourceDocuments", "SourceDocumentId")
            .WithColumn("EventType").AsString(60).NotNullable()
            .WithColumn("Title").AsString(500).NotNullable()
            .WithColumn("EventTime").AsDateTime().NotNullable()
            .WithColumn("Description").AsString(2000).Nullable()
            .WithAuditColumns();

        Create.Table("Evidence")
            .WithColumn("EvidenceId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(120).NotNullable()
            .WithColumn("Version").AsInt32().NotNullable().WithDefaultValue(1)
            .WithColumn("SourceDocumentId").AsInt32().NotNullable().ForeignKey("FK_Evidence_SourceId", "SourceDocuments", "SourceDocumentId")
            .WithColumn("EventId").AsInt32().Nullable().ForeignKey("FK_Evidence_EventId", "Events", "EventId")
            .WithColumn("CompanyId").AsInt32().Nullable().ForeignKey("FK_Evidence_CompanyId", "Companies", "CompanyId")
            .WithColumn("PhysicalPartId").AsInt32().Nullable().ForeignKey("FK_Evidence_PartId", "PhysicalParts", "PhysicalPartId")
            .WithColumn("IndustryChainNodeId").AsInt32().Nullable().ForeignKey("FK_Evidence_NodeId", "IndustryChainNodes", "IndustryChainNodeId")
            .WithColumn("TechnologyLinkId").AsInt32().Nullable().ForeignKey("FK_Evidence_TechId", "TechnologyLinks", "TechnologyLinkId")
            .WithColumn("Proposition").AsString(2000).NotNullable()
            .WithColumn("OriginalQuote").AsString(4000).Nullable()
            .WithColumn("Locator").AsString(500).NotNullable()
            .WithColumn("Stance").AsString(20).NotNullable()
            .WithColumn("ReviewState").AsString(20).NotNullable()
            .WithColumn("ReviewedBy").AsInt32().Nullable()
            .WithColumn("ReviewedAt").AsDateTime().Nullable()
            .WithColumn("AnalystNote").AsString(2000).Nullable()
            .WithAuditColumns();
        Create.Index("UQ_Evidence_StableId_Version").OnTable("Evidence")
            .OnColumn("StableId").Ascending().OnColumn("Version").Ascending().WithOptions().Unique();

        Create.Table("CompanyExposureEvidence")
            .WithColumn("CompanyExposureEvidenceId").AsInt32().IdentityKey(this)
            .WithColumn("CompanyExposureId").AsInt32().NotNullable().ForeignKey("FK_ExposureEvidence_ExposureId", "CompanyExposures", "CompanyExposureId")
            .WithColumn("EvidenceId").AsInt32().NotNullable().ForeignKey("FK_ExposureEvidence_EvidenceId", "Evidence", "EvidenceId")
            .WithColumn("InsertDate").AsDateTime().NotNullable()
            .WithColumn("InsertUserId").AsInt32().NotNullable();
        Create.Index("UQ_ExposureEvidence_Exposure_Evidence").OnTable("CompanyExposureEvidence")
            .OnColumn("CompanyExposureId").Ascending().OnColumn("EvidenceId").Ascending().WithOptions().Unique();

        Create.Table("ResearchConclusions")
            .WithColumn("ResearchConclusionId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(120).NotNullable()
            .WithColumn("ThemeId").AsInt32().NotNullable().ForeignKey("FK_ResearchConclusions_ThemeId", "Themes", "ThemeId")
            .WithColumn("Version").AsInt32().NotNullable()
            .WithColumn("Statement").AsString(4000).NotNullable()
            .WithColumn("PublicationState").AsString(20).NotNullable()
            .WithColumn("Confidence").AsString(20).NotNullable()
            .WithColumn("TimeHorizon").AsString(200).Nullable()
            .WithColumn("Risks").AsString(3000).Nullable()
            .WithColumn("InvalidationConditions").AsString(3000).Nullable()
            .WithAuditColumns();
        Create.Index("UQ_ResearchConclusions_StableId_Version").OnTable("ResearchConclusions")
            .OnColumn("StableId").Ascending().OnColumn("Version").Ascending().WithOptions().Unique();

        Create.Table("ConclusionEvidence")
            .WithColumn("ConclusionEvidenceId").AsInt32().IdentityKey(this)
            .WithColumn("ResearchConclusionId").AsInt32().NotNullable().ForeignKey("FK_ConclusionEvidence_ConclusionId", "ResearchConclusions", "ResearchConclusionId")
            .WithColumn("EvidenceId").AsInt32().NotNullable().ForeignKey("FK_ConclusionEvidence_EvidenceId", "Evidence", "EvidenceId")
            .WithColumn("EvidenceVersion").AsInt32().NotNullable()
            .WithColumn("InsertDate").AsDateTime().NotNullable()
            .WithColumn("InsertUserId").AsInt32().NotNullable();
        Create.Index("UQ_ConclusionEvidence_Conclusion_Evidence").OnTable("ConclusionEvidence")
            .OnColumn("ResearchConclusionId").Ascending().OnColumn("EvidenceId").Ascending().WithOptions().Unique();

        Create.Table("ResearchReports")
            .WithColumn("ResearchReportId").AsInt32().IdentityKey(this)
            .WithColumn("StableId").AsString(120).NotNullable()
            .WithColumn("ThemeId").AsInt32().NotNullable().ForeignKey("FK_ResearchReports_ThemeId", "Themes", "ThemeId")
            .WithColumn("Version").AsInt32().NotNullable()
            .WithColumn("Title").AsString(500).NotNullable()
            .WithColumn("PublicationState").AsString(20).NotNullable()
            .WithColumn("GeneratedAt").AsDateTime().Nullable()
            .WithAuditColumns();
        Create.Index("UQ_ResearchReports_StableId_Version").OnTable("ResearchReports")
            .OnColumn("StableId").Ascending().OnColumn("Version").Ascending().WithOptions().Unique();

        Create.Table("ReportConclusions")
            .WithColumn("ReportConclusionId").AsInt32().IdentityKey(this)
            .WithColumn("ResearchReportId").AsInt32().NotNullable().ForeignKey("FK_ReportConclusions_ReportId", "ResearchReports", "ResearchReportId")
            .WithColumn("ResearchConclusionId").AsInt32().NotNullable().ForeignKey("FK_ReportConclusions_ConclusionId", "ResearchConclusions", "ResearchConclusionId")
            .WithColumn("ConclusionVersion").AsInt32().NotNullable()
            .WithColumn("InsertDate").AsDateTime().NotNullable()
            .WithColumn("InsertUserId").AsInt32().NotNullable();
        Create.Index("UQ_ReportConclusions_Report_Conclusion").OnTable("ReportConclusions")
            .OnColumn("ResearchReportId").Ascending().OnColumn("ResearchConclusionId").Ascending().WithOptions().Unique();

        Create.Table("ReportEvidence")
            .WithColumn("ReportEvidenceId").AsInt32().IdentityKey(this)
            .WithColumn("ResearchReportId").AsInt32().NotNullable().ForeignKey("FK_ReportEvidence_ReportId", "ResearchReports", "ResearchReportId")
            .WithColumn("EvidenceId").AsInt32().NotNullable().ForeignKey("FK_ReportEvidence_EvidenceId", "Evidence", "EvidenceId")
            .WithColumn("EvidenceVersion").AsInt32().NotNullable()
            .WithColumn("InsertDate").AsDateTime().NotNullable()
            .WithColumn("InsertUserId").AsInt32().NotNullable();
        Create.Index("UQ_ReportEvidence_Report_Evidence").OnTable("ReportEvidence")
            .OnColumn("ResearchReportId").Ascending().OnColumn("EvidenceId").Ascending().WithOptions().Unique();
    }
}

internal static class ResearchMigrationExtensions
{
    public static FluentMigrator.Builders.Create.Table.ICreateTableColumnOptionOrWithColumnSyntax WithAuditColumns(
        this FluentMigrator.Builders.Create.Table.ICreateTableColumnOptionOrWithColumnSyntax table)
    {
        return table
            .WithColumn("InsertDate").AsDateTime().NotNullable()
            .WithColumn("InsertUserId").AsInt32().NotNullable()
            .WithColumn("UpdateDate").AsDateTime().Nullable()
            .WithColumn("UpdateUserId").AsInt32().Nullable();
    }
}
