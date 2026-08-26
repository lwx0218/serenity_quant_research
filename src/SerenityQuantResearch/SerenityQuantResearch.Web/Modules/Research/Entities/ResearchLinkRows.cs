namespace SerenityQuantResearch.Research.Entities;

[ConnectionKey("Default"), Module("Research"), TableName("PhysicalPartTechnologyLinks")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.General)]
public sealed class PhysicalPartTechnologyLinkRow : Row<PhysicalPartTechnologyLinkRow.RowFields>, IIdRow
{
    [Identity, IdProperty] public int? PhysicalPartTechnologyLinkId { get => fields.PhysicalPartTechnologyLinkId[this]; set => fields.PhysicalPartTechnologyLinkId[this] = value; }
    [NotNull, ForeignKey(typeof(PhysicalPartRow))] public int? PhysicalPartId { get => fields.PhysicalPartId[this]; set => fields.PhysicalPartId[this] = value; }
    [NotNull, ForeignKey(typeof(TechnologyLinkRow))] public int? TechnologyLinkId { get => fields.TechnologyLinkId[this]; set => fields.TechnologyLinkId[this] = value; }
    [NotNull] public DateTime? InsertDate { get => fields.InsertDate[this]; set => fields.InsertDate[this] = value; }
    [NotNull] public int? InsertUserId { get => fields.InsertUserId[this]; set => fields.InsertUserId[this] = value; }
    public class RowFields : RowFieldsBase { public Int32Field PhysicalPartTechnologyLinkId; public Int32Field PhysicalPartId; public Int32Field TechnologyLinkId; public DateTimeField InsertDate; public Int32Field InsertUserId; }
}

[ConnectionKey("Default"), Module("Research"), TableName("PhysicalPartIndustryChainNodes")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.General)]
public sealed class PhysicalPartIndustryChainNodeRow : Row<PhysicalPartIndustryChainNodeRow.RowFields>, IIdRow
{
    [Identity, IdProperty] public int? PhysicalPartIndustryChainNodeId { get => fields.PhysicalPartIndustryChainNodeId[this]; set => fields.PhysicalPartIndustryChainNodeId[this] = value; }
    [NotNull, ForeignKey(typeof(PhysicalPartRow))] public int? PhysicalPartId { get => fields.PhysicalPartId[this]; set => fields.PhysicalPartId[this] = value; }
    [NotNull, ForeignKey(typeof(IndustryChainNodeRow))] public int? IndustryChainNodeId { get => fields.IndustryChainNodeId[this]; set => fields.IndustryChainNodeId[this] = value; }
    [NotNull] public DateTime? InsertDate { get => fields.InsertDate[this]; set => fields.InsertDate[this] = value; }
    [NotNull] public int? InsertUserId { get => fields.InsertUserId[this]; set => fields.InsertUserId[this] = value; }
    public class RowFields : RowFieldsBase { public Int32Field PhysicalPartIndustryChainNodeId; public Int32Field PhysicalPartId; public Int32Field IndustryChainNodeId; public DateTimeField InsertDate; public Int32Field InsertUserId; }
}

[ConnectionKey("Default"), Module("Research"), TableName("CompanyExposureEvidence")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Review)]
public sealed class CompanyExposureEvidenceRow : Row<CompanyExposureEvidenceRow.RowFields>, IIdRow
{
    [Identity, IdProperty] public int? CompanyExposureEvidenceId { get => fields.CompanyExposureEvidenceId[this]; set => fields.CompanyExposureEvidenceId[this] = value; }
    [NotNull, ForeignKey(typeof(CompanyExposureRow))] public int? CompanyExposureId { get => fields.CompanyExposureId[this]; set => fields.CompanyExposureId[this] = value; }
    [NotNull, ForeignKey(typeof(EvidenceRow))] public int? EvidenceId { get => fields.EvidenceId[this]; set => fields.EvidenceId[this] = value; }
    [NotNull] public DateTime? InsertDate { get => fields.InsertDate[this]; set => fields.InsertDate[this] = value; }
    [NotNull] public int? InsertUserId { get => fields.InsertUserId[this]; set => fields.InsertUserId[this] = value; }
    public class RowFields : RowFieldsBase { public Int32Field CompanyExposureEvidenceId; public Int32Field CompanyExposureId; public Int32Field EvidenceId; public DateTimeField InsertDate; public Int32Field InsertUserId; }
}

[ConnectionKey("Default"), Module("Research"), TableName("ConclusionEvidence")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Publish)]
public sealed class ConclusionEvidenceRow : Row<ConclusionEvidenceRow.RowFields>, IIdRow
{
    [Identity, IdProperty] public int? ConclusionEvidenceId { get => fields.ConclusionEvidenceId[this]; set => fields.ConclusionEvidenceId[this] = value; }
    [NotNull, ForeignKey(typeof(ResearchConclusionRow))] public int? ResearchConclusionId { get => fields.ResearchConclusionId[this]; set => fields.ResearchConclusionId[this] = value; }
    [NotNull, ForeignKey(typeof(EvidenceRow))] public int? EvidenceId { get => fields.EvidenceId[this]; set => fields.EvidenceId[this] = value; }
    [NotNull] public int? EvidenceVersion { get => fields.EvidenceVersion[this]; set => fields.EvidenceVersion[this] = value; }
    [NotNull] public DateTime? InsertDate { get => fields.InsertDate[this]; set => fields.InsertDate[this] = value; }
    [NotNull] public int? InsertUserId { get => fields.InsertUserId[this]; set => fields.InsertUserId[this] = value; }
    public class RowFields : RowFieldsBase { public Int32Field ConclusionEvidenceId; public Int32Field ResearchConclusionId; public Int32Field EvidenceId; public Int32Field EvidenceVersion; public DateTimeField InsertDate; public Int32Field InsertUserId; }
}

[ConnectionKey("Default"), Module("Research"), TableName("ReportConclusions")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Publish)]
public sealed class ReportConclusionRow : Row<ReportConclusionRow.RowFields>, IIdRow
{
    [Identity, IdProperty] public int? ReportConclusionId { get => fields.ReportConclusionId[this]; set => fields.ReportConclusionId[this] = value; }
    [NotNull, ForeignKey(typeof(ResearchReportRow))] public int? ResearchReportId { get => fields.ResearchReportId[this]; set => fields.ResearchReportId[this] = value; }
    [NotNull, ForeignKey(typeof(ResearchConclusionRow))] public int? ResearchConclusionId { get => fields.ResearchConclusionId[this]; set => fields.ResearchConclusionId[this] = value; }
    [NotNull] public int? ConclusionVersion { get => fields.ConclusionVersion[this]; set => fields.ConclusionVersion[this] = value; }
    [NotNull] public DateTime? InsertDate { get => fields.InsertDate[this]; set => fields.InsertDate[this] = value; }
    [NotNull] public int? InsertUserId { get => fields.InsertUserId[this]; set => fields.InsertUserId[this] = value; }
    public class RowFields : RowFieldsBase { public Int32Field ReportConclusionId; public Int32Field ResearchReportId; public Int32Field ResearchConclusionId; public Int32Field ConclusionVersion; public DateTimeField InsertDate; public Int32Field InsertUserId; }
}

[ConnectionKey("Default"), Module("Research"), TableName("ReportEvidence")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Publish)]
public sealed class ReportEvidenceRow : Row<ReportEvidenceRow.RowFields>, IIdRow
{
    [Identity, IdProperty] public int? ReportEvidenceId { get => fields.ReportEvidenceId[this]; set => fields.ReportEvidenceId[this] = value; }
    [NotNull, ForeignKey(typeof(ResearchReportRow))] public int? ResearchReportId { get => fields.ResearchReportId[this]; set => fields.ResearchReportId[this] = value; }
    [NotNull, ForeignKey(typeof(EvidenceRow))] public int? EvidenceId { get => fields.EvidenceId[this]; set => fields.EvidenceId[this] = value; }
    [NotNull] public int? EvidenceVersion { get => fields.EvidenceVersion[this]; set => fields.EvidenceVersion[this] = value; }
    [NotNull] public DateTime? InsertDate { get => fields.InsertDate[this]; set => fields.InsertDate[this] = value; }
    [NotNull] public int? InsertUserId { get => fields.InsertUserId[this]; set => fields.InsertUserId[this] = value; }
    public class RowFields : RowFieldsBase { public Int32Field ReportEvidenceId; public Int32Field ResearchReportId; public Int32Field EvidenceId; public Int32Field EvidenceVersion; public DateTimeField InsertDate; public Int32Field InsertUserId; }
}
