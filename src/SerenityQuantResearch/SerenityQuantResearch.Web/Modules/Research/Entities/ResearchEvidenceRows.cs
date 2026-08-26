namespace SerenityQuantResearch.Research.Entities;

[ConnectionKey("Default"), Module("Research"), TableName("Companies")]
[DisplayName("Companies"), InstanceName("Company")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.General)]
public sealed class CompanyRow : Serenity.Extensions.Entities.LoggingRow<CompanyRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Company Id"), Identity, IdProperty]
    public int? CompanyId { get => fields.CompanyId[this]; set => fields.CompanyId[this] = value; }

    [DisplayName("Stable Id"), Size(100), NotNull, Unique, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Name"), Size(240), NotNull, NameProperty]
    public string Name { get => fields.Name[this]; set => fields.Name[this] = value; }

    [DisplayName("English Name"), Size(240)]
    public string EnglishName { get => fields.EnglishName[this]; set => fields.EnglishName[this] = value; }

    [DisplayName("Ticker"), Size(40)]
    public string Ticker { get => fields.Ticker[this]; set => fields.Ticker[this] = value; }

    [DisplayName("Exchange"), Size(40)]
    public string Exchange { get => fields.Exchange[this]; set => fields.Exchange[this] = value; }

    [DisplayName("Country / Region"), Size(80), NotNull]
    public string CountryRegion { get => fields.CountryRegion[this]; set => fields.CountryRegion[this] = value; }

    [DisplayName("Universe Layer"), Size(40), NotNull]
    public string UniverseLayer { get => fields.UniverseLayer[this]; set => fields.UniverseLayer[this] = value; }

    [DisplayName("Coverage Priority"), Size(40), NotNull]
    public string CoveragePriority { get => fields.CoveragePriority[this]; set => fields.CoveragePriority[this] = value; }

    [DisplayName("Official URL"), Size(1000)]
    public string OfficialUrl { get => fields.OfficialUrl[this]; set => fields.OfficialUrl[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field CompanyId;
        public StringField StableId;
        public StringField Name;
        public StringField EnglishName;
        public StringField Ticker;
        public StringField Exchange;
        public StringField CountryRegion;
        public StringField UniverseLayer;
        public StringField CoveragePriority;
        public StringField OfficialUrl;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("CompanyExposures")]
[DisplayName("Company Exposures"), InstanceName("Company Exposure")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Review)]
public sealed class CompanyExposureRow : Serenity.Extensions.Entities.LoggingRow<CompanyExposureRow.RowFields>, IIdRow
{
    [DisplayName("Exposure Id"), Identity, IdProperty]
    public int? CompanyExposureId { get => fields.CompanyExposureId[this]; set => fields.CompanyExposureId[this] = value; }

    [DisplayName("Company"), NotNull, ForeignKey(typeof(CompanyRow)), LeftJoin("jCompany")]
    public int? CompanyId { get => fields.CompanyId[this]; set => fields.CompanyId[this] = value; }

    [DisplayName("Physical Part"), ForeignKey(typeof(PhysicalPartRow)), LeftJoin("jPart")]
    public int? PhysicalPartId { get => fields.PhysicalPartId[this]; set => fields.PhysicalPartId[this] = value; }

    [DisplayName("Industry Chain Node"), ForeignKey(typeof(IndustryChainNodeRow)), LeftJoin("jNode")]
    public int? IndustryChainNodeId { get => fields.IndustryChainNodeId[this]; set => fields.IndustryChainNodeId[this] = value; }

    [DisplayName("Role"), Size(80), NotNull]
    public string Role { get => fields.Role[this]; set => fields.Role[this] = value; }

    [DisplayName("Relevance"), Size(40), NotNull]
    public string Relevance { get => fields.Relevance[this]; set => fields.Relevance[this] = value; }

    [DisplayName("Confidence"), Size(20), NotNull]
    public string Confidence { get => fields.Confidence[this]; set => fields.Confidence[this] = value; }

    [DisplayName("Verification State"), Size(20), NotNull]
    public string VerificationState { get => fields.VerificationState[this]; set => fields.VerificationState[this] = value; }

    [DisplayName("Scope Note"), Size(2000)]
    public string ScopeNote { get => fields.ScopeNote[this]; set => fields.ScopeNote[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field CompanyExposureId;
        public Int32Field CompanyId;
        public Int32Field PhysicalPartId;
        public Int32Field IndustryChainNodeId;
        public StringField Role;
        public StringField Relevance;
        public StringField Confidence;
        public StringField VerificationState;
        public StringField ScopeNote;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("SourceDocuments")]
[DisplayName("Source Documents"), InstanceName("Source Document")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Review)]
public sealed class SourceDocumentRow : Serenity.Extensions.Entities.LoggingRow<SourceDocumentRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Source Document Id"), Identity, IdProperty]
    public int? SourceDocumentId { get => fields.SourceDocumentId[this]; set => fields.SourceDocumentId[this] = value; }

    [DisplayName("Stable Id"), Size(120), NotNull, Unique, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Source Level"), Size(1), NotNull]
    public string SourceLevel { get => fields.SourceLevel[this]; set => fields.SourceLevel[this] = value; }

    [DisplayName("Publisher"), Size(240), NotNull]
    public string Publisher { get => fields.Publisher[this]; set => fields.Publisher[this] = value; }

    [DisplayName("Title"), Size(500), NotNull, NameProperty]
    public string Title { get => fields.Title[this]; set => fields.Title[this] = value; }

    [DisplayName("Original URL"), Size(1500), NotNull]
    public string OriginalUrl { get => fields.OriginalUrl[this]; set => fields.OriginalUrl[this] = value; }

    [DisplayName("Publication Time")]
    public DateTime? PublicationTime { get => fields.PublicationTime[this]; set => fields.PublicationTime[this] = value; }

    [DisplayName("Capture Time"), NotNull]
    public DateTime? CaptureTime { get => fields.CaptureTime[this]; set => fields.CaptureTime[this] = value; }

    [DisplayName("Content Fingerprint"), Size(64)]
    public string ContentFingerprint { get => fields.ContentFingerprint[this]; set => fields.ContentFingerprint[this] = value; }

    [DisplayName("Rights Note"), Size(1000)]
    public string RightsNote { get => fields.RightsNote[this]; set => fields.RightsNote[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field SourceDocumentId;
        public StringField StableId;
        public StringField SourceLevel;
        public StringField Publisher;
        public StringField Title;
        public StringField OriginalUrl;
        public DateTimeField PublicationTime;
        public DateTimeField CaptureTime;
        public StringField ContentFingerprint;
        public StringField RightsNote;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("Events")]
[DisplayName("Events"), InstanceName("Event")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Review)]
public sealed class EventRow : Serenity.Extensions.Entities.LoggingRow<EventRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Event Id"), Identity, IdProperty]
    public int? EventId { get => fields.EventId[this]; set => fields.EventId[this] = value; }

    [DisplayName("Stable Id"), Size(120), NotNull, Unique, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Company"), ForeignKey(typeof(CompanyRow)), LeftJoin("jCompany")]
    public int? CompanyId { get => fields.CompanyId[this]; set => fields.CompanyId[this] = value; }

    [DisplayName("Source Document"), ForeignKey(typeof(SourceDocumentRow)), LeftJoin("jSource")]
    public int? SourceDocumentId { get => fields.SourceDocumentId[this]; set => fields.SourceDocumentId[this] = value; }

    [DisplayName("Event Type"), Size(60), NotNull]
    public string EventType { get => fields.EventType[this]; set => fields.EventType[this] = value; }

    [DisplayName("Title"), Size(500), NotNull, NameProperty]
    public string Title { get => fields.Title[this]; set => fields.Title[this] = value; }

    [DisplayName("Event Time"), NotNull]
    public DateTime? EventTime { get => fields.EventTime[this]; set => fields.EventTime[this] = value; }

    [DisplayName("Description"), Size(2000)]
    public string Description { get => fields.Description[this]; set => fields.Description[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field EventId;
        public StringField StableId;
        public Int32Field CompanyId;
        public Int32Field SourceDocumentId;
        public StringField EventType;
        public StringField Title;
        public DateTimeField EventTime;
        public StringField Description;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("Evidence")]
[DisplayName("Evidence"), InstanceName("Evidence")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.Review)]
public sealed class EvidenceRow : Serenity.Extensions.Entities.LoggingRow<EvidenceRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Evidence Id"), Identity, IdProperty]
    public int? EvidenceId { get => fields.EvidenceId[this]; set => fields.EvidenceId[this] = value; }

    [DisplayName("Stable Id"), Size(120), NotNull, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Version"), NotNull]
    public int? Version { get => fields.Version[this]; set => fields.Version[this] = value; }

    [DisplayName("Source Document"), NotNull, ForeignKey(typeof(SourceDocumentRow)), LeftJoin("jSource")]
    public int? SourceDocumentId { get => fields.SourceDocumentId[this]; set => fields.SourceDocumentId[this] = value; }

    [DisplayName("Event"), ForeignKey(typeof(EventRow)), LeftJoin("jEvent")]
    public int? EventId { get => fields.EventId[this]; set => fields.EventId[this] = value; }

    [DisplayName("Company"), ForeignKey(typeof(CompanyRow)), LeftJoin("jCompany")]
    public int? CompanyId { get => fields.CompanyId[this]; set => fields.CompanyId[this] = value; }

    [DisplayName("Physical Part"), ForeignKey(typeof(PhysicalPartRow)), LeftJoin("jPart")]
    public int? PhysicalPartId { get => fields.PhysicalPartId[this]; set => fields.PhysicalPartId[this] = value; }

    [DisplayName("Industry Chain Node"), ForeignKey(typeof(IndustryChainNodeRow)), LeftJoin("jNode")]
    public int? IndustryChainNodeId { get => fields.IndustryChainNodeId[this]; set => fields.IndustryChainNodeId[this] = value; }

    [DisplayName("Technology Link"), ForeignKey(typeof(TechnologyLinkRow)), LeftJoin("jTechnology")]
    public int? TechnologyLinkId { get => fields.TechnologyLinkId[this]; set => fields.TechnologyLinkId[this] = value; }

    [DisplayName("Proposition"), Size(2000), NotNull, NameProperty]
    public string Proposition { get => fields.Proposition[this]; set => fields.Proposition[this] = value; }

    [DisplayName("Original Quote"), Size(4000)]
    public string OriginalQuote { get => fields.OriginalQuote[this]; set => fields.OriginalQuote[this] = value; }

    [DisplayName("Locator"), Size(500), NotNull]
    public string Locator { get => fields.Locator[this]; set => fields.Locator[this] = value; }

    [DisplayName("Stance"), Size(20), NotNull]
    public string Stance { get => fields.Stance[this]; set => fields.Stance[this] = value; }

    [DisplayName("Review State"), Size(20), NotNull]
    public string ReviewState { get => fields.ReviewState[this]; set => fields.ReviewState[this] = value; }

    [DisplayName("Reviewed By")]
    public int? ReviewedBy { get => fields.ReviewedBy[this]; set => fields.ReviewedBy[this] = value; }

    [DisplayName("Reviewed At")]
    public DateTime? ReviewedAt { get => fields.ReviewedAt[this]; set => fields.ReviewedAt[this] = value; }

    [DisplayName("Analyst Note"), Size(2000)]
    public string AnalystNote { get => fields.AnalystNote[this]; set => fields.AnalystNote[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field EvidenceId;
        public StringField StableId;
        public Int32Field Version;
        public Int32Field SourceDocumentId;
        public Int32Field EventId;
        public Int32Field CompanyId;
        public Int32Field PhysicalPartId;
        public Int32Field IndustryChainNodeId;
        public Int32Field TechnologyLinkId;
        public StringField Proposition;
        public StringField OriginalQuote;
        public StringField Locator;
        public StringField Stance;
        public StringField ReviewState;
        public Int32Field ReviewedBy;
        public DateTimeField ReviewedAt;
        public StringField AnalystNote;
    }
}
