namespace SerenityQuantResearch.Research.Entities;

[ConnectionKey("Default"), Module("Research"), TableName("ResearchConclusions")]
[DisplayName("Research Conclusions"), InstanceName("Research Conclusion")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Publish)]
public sealed class ResearchConclusionRow : Serenity.Extensions.Entities.LoggingRow<ResearchConclusionRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Conclusion Id"), Identity, IdProperty]
    public int? ResearchConclusionId { get => fields.ResearchConclusionId[this]; set => fields.ResearchConclusionId[this] = value; }

    [DisplayName("Stable Id"), Size(120), NotNull, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Theme"), NotNull, ForeignKey(typeof(ThemeRow)), LeftJoin("jTheme")]
    public int? ThemeId { get => fields.ThemeId[this]; set => fields.ThemeId[this] = value; }

    [DisplayName("Version"), NotNull]
    public int? Version { get => fields.Version[this]; set => fields.Version[this] = value; }

    [DisplayName("Statement"), Size(4000), NotNull, NameProperty]
    public string Statement { get => fields.Statement[this]; set => fields.Statement[this] = value; }

    [DisplayName("Publication State"), Size(20), NotNull]
    public string PublicationState { get => fields.PublicationState[this]; set => fields.PublicationState[this] = value; }

    [DisplayName("Confidence"), Size(20), NotNull]
    public string Confidence { get => fields.Confidence[this]; set => fields.Confidence[this] = value; }

    [DisplayName("Time Horizon"), Size(200)]
    public string TimeHorizon { get => fields.TimeHorizon[this]; set => fields.TimeHorizon[this] = value; }

    [DisplayName("Risks"), Size(3000)]
    public string Risks { get => fields.Risks[this]; set => fields.Risks[this] = value; }

    [DisplayName("Invalidation Conditions"), Size(3000)]
    public string InvalidationConditions { get => fields.InvalidationConditions[this]; set => fields.InvalidationConditions[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field ResearchConclusionId;
        public StringField StableId;
        public Int32Field ThemeId;
        public Int32Field Version;
        public StringField Statement;
        public StringField PublicationState;
        public StringField Confidence;
        public StringField TimeHorizon;
        public StringField Risks;
        public StringField InvalidationConditions;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("ResearchReports")]
[DisplayName("Research Reports"), InstanceName("Research Report")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Publish)]
public sealed class ResearchReportRow : Serenity.Extensions.Entities.LoggingRow<ResearchReportRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Report Id"), Identity, IdProperty]
    public int? ResearchReportId { get => fields.ResearchReportId[this]; set => fields.ResearchReportId[this] = value; }

    [DisplayName("Stable Id"), Size(120), NotNull, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Theme"), NotNull, ForeignKey(typeof(ThemeRow)), LeftJoin("jTheme")]
    public int? ThemeId { get => fields.ThemeId[this]; set => fields.ThemeId[this] = value; }

    [DisplayName("Version"), NotNull]
    public int? Version { get => fields.Version[this]; set => fields.Version[this] = value; }

    [DisplayName("Title"), Size(500), NotNull, NameProperty]
    public string Title { get => fields.Title[this]; set => fields.Title[this] = value; }

    [DisplayName("Publication State"), Size(20), NotNull]
    public string PublicationState { get => fields.PublicationState[this]; set => fields.PublicationState[this] = value; }

    [DisplayName("Generated At")]
    public DateTime? GeneratedAt { get => fields.GeneratedAt[this]; set => fields.GeneratedAt[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field ResearchReportId;
        public StringField StableId;
        public Int32Field ThemeId;
        public Int32Field Version;
        public StringField Title;
        public StringField PublicationState;
        public DateTimeField GeneratedAt;
    }
}
