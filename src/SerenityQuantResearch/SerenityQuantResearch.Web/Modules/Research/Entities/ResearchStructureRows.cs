namespace SerenityQuantResearch.Research.Entities;

[ConnectionKey("Default"), Module("Research"), TableName("Themes")]
[DisplayName("Themes"), InstanceName("Theme")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.General)]
public sealed class ThemeRow : Serenity.Extensions.Entities.LoggingRow<ThemeRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Theme Id"), Identity, IdProperty]
    public int? ThemeId { get => fields.ThemeId[this]; set => fields.ThemeId[this] = value; }

    [DisplayName("Stable Id"), Size(100), NotNull, Unique, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Name"), Size(200), NotNull, NameProperty]
    public string Name { get => fields.Name[this]; set => fields.Name[this] = value; }

    [DisplayName("Description"), Size(2000)]
    public string Description { get => fields.Description[this]; set => fields.Description[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field ThemeId;
        public StringField StableId;
        public StringField Name;
        public StringField Description;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("IndustryChains")]
[DisplayName("Industry Chains"), InstanceName("Industry Chain")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.General)]
public sealed class IndustryChainRow : Serenity.Extensions.Entities.LoggingRow<IndustryChainRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Industry Chain Id"), Identity, IdProperty]
    public int? IndustryChainId { get => fields.IndustryChainId[this]; set => fields.IndustryChainId[this] = value; }

    [DisplayName("Stable Id"), Size(100), NotNull, Unique, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Theme"), NotNull, ForeignKey(typeof(ThemeRow)), LeftJoin("jTheme")]
    public int? ThemeId { get => fields.ThemeId[this]; set => fields.ThemeId[this] = value; }

    [DisplayName("Name"), Size(200), NotNull, NameProperty]
    public string Name { get => fields.Name[this]; set => fields.Name[this] = value; }

    [DisplayName("Description"), Size(2000)]
    public string Description { get => fields.Description[this]; set => fields.Description[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field IndustryChainId;
        public StringField StableId;
        public Int32Field ThemeId;
        public StringField Name;
        public StringField Description;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("IndustryChainNodes")]
[DisplayName("Industry Chain Nodes"), InstanceName("Industry Chain Node")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.General)]
public sealed class IndustryChainNodeRow : Serenity.Extensions.Entities.LoggingRow<IndustryChainNodeRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Node Id"), Identity, IdProperty]
    public int? IndustryChainNodeId { get => fields.IndustryChainNodeId[this]; set => fields.IndustryChainNodeId[this] = value; }

    [DisplayName("Stable Id"), Size(120), NotNull, Unique, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Industry Chain"), NotNull, ForeignKey(typeof(IndustryChainRow)), LeftJoin("jChain")]
    public int? IndustryChainId { get => fields.IndustryChainId[this]; set => fields.IndustryChainId[this] = value; }

    [DisplayName("Parent Node"), ForeignKey(typeof(IndustryChainNodeRow)), LeftJoin("jParent")]
    public int? ParentNodeId { get => fields.ParentNodeId[this]; set => fields.ParentNodeId[this] = value; }

    [DisplayName("Name"), Size(200), NotNull, NameProperty]
    public string Name { get => fields.Name[this]; set => fields.Name[this] = value; }

    [DisplayName("Node Type"), Size(40), NotNull]
    public string NodeType { get => fields.NodeType[this]; set => fields.NodeType[this] = value; }

    [DisplayName("Sort Order"), NotNull]
    public int? SortOrder { get => fields.SortOrder[this]; set => fields.SortOrder[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field IndustryChainNodeId;
        public StringField StableId;
        public Int32Field IndustryChainId;
        public Int32Field ParentNodeId;
        public StringField Name;
        public StringField NodeType;
        public Int32Field SortOrder;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("PhysicalModules")]
[DisplayName("Physical Modules"), InstanceName("Physical Module")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.General)]
public sealed class PhysicalModuleRow : Serenity.Extensions.Entities.LoggingRow<PhysicalModuleRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Module Id"), Identity, IdProperty]
    public int? PhysicalModuleId { get => fields.PhysicalModuleId[this]; set => fields.PhysicalModuleId[this] = value; }

    [DisplayName("Stable Id"), Size(120), NotNull, Unique, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Theme"), NotNull, ForeignKey(typeof(ThemeRow)), LeftJoin("jTheme")]
    public int? ThemeId { get => fields.ThemeId[this]; set => fields.ThemeId[this] = value; }

    [DisplayName("Name"), Size(200), NotNull, NameProperty]
    public string Name { get => fields.Name[this]; set => fields.Name[this] = value; }

    [DisplayName("Description"), Size(2000)]
    public string Description { get => fields.Description[this]; set => fields.Description[this] = value; }

    [DisplayName("Sort Order"), NotNull]
    public int? SortOrder { get => fields.SortOrder[this]; set => fields.SortOrder[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field PhysicalModuleId;
        public StringField StableId;
        public Int32Field ThemeId;
        public StringField Name;
        public StringField Description;
        public Int32Field SortOrder;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("PhysicalParts")]
[DisplayName("Physical Parts"), InstanceName("Physical Part")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.General)]
public sealed class PhysicalPartRow : Serenity.Extensions.Entities.LoggingRow<PhysicalPartRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Part Id"), Identity, IdProperty]
    public int? PhysicalPartId { get => fields.PhysicalPartId[this]; set => fields.PhysicalPartId[this] = value; }

    [DisplayName("Stable Id"), Size(140), NotNull, Unique, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Physical Module"), NotNull, ForeignKey(typeof(PhysicalModuleRow)), LeftJoin("jModule")]
    public int? PhysicalModuleId { get => fields.PhysicalModuleId[this]; set => fields.PhysicalModuleId[this] = value; }

    [DisplayName("Parent Part"), ForeignKey(typeof(PhysicalPartRow)), LeftJoin("jParent")]
    public int? ParentPartId { get => fields.ParentPartId[this]; set => fields.ParentPartId[this] = value; }

    [DisplayName("Name"), Size(200), NotNull, NameProperty]
    public string Name { get => fields.Name[this]; set => fields.Name[this] = value; }

    [DisplayName("Function Summary"), Size(2000)]
    public string FunctionSummary { get => fields.FunctionSummary[this]; set => fields.FunctionSummary[this] = value; }

    [DisplayName("Research Status"), Size(40), NotNull]
    public string ResearchStatus { get => fields.ResearchStatus[this]; set => fields.ResearchStatus[this] = value; }

    [DisplayName("Sort Order"), NotNull]
    public int? SortOrder { get => fields.SortOrder[this]; set => fields.SortOrder[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field PhysicalPartId;
        public StringField StableId;
        public Int32Field PhysicalModuleId;
        public Int32Field ParentPartId;
        public StringField Name;
        public StringField FunctionSummary;
        public StringField ResearchStatus;
        public Int32Field SortOrder;
    }
}

[ConnectionKey("Default"), Module("Research"), TableName("TechnologyLinks")]
[DisplayName("Technology Links"), InstanceName("Technology Link")]
[ReadPermission(ResearchPermissionKeys.General), ModifyPermission(ResearchPermissionKeys.General)]
public sealed class TechnologyLinkRow : Serenity.Extensions.Entities.LoggingRow<TechnologyLinkRow.RowFields>, IIdRow, INameRow
{
    [DisplayName("Technology Link Id"), Identity, IdProperty]
    public int? TechnologyLinkId { get => fields.TechnologyLinkId[this]; set => fields.TechnologyLinkId[this] = value; }

    [DisplayName("Stable Id"), Size(120), NotNull, Unique, QuickSearch]
    public string StableId { get => fields.StableId[this]; set => fields.StableId[this] = value; }

    [DisplayName("Theme"), NotNull, ForeignKey(typeof(ThemeRow)), LeftJoin("jTheme")]
    public int? ThemeId { get => fields.ThemeId[this]; set => fields.ThemeId[this] = value; }

    [DisplayName("Name"), Size(200), NotNull, NameProperty]
    public string Name { get => fields.Name[this]; set => fields.Name[this] = value; }

    [DisplayName("Description"), Size(2000)]
    public string Description { get => fields.Description[this]; set => fields.Description[this] = value; }

    public class RowFields : Serenity.Extensions.Entities.LoggingRowFields
    {
        public Int32Field TechnologyLinkId;
        public StringField StableId;
        public Int32Field ThemeId;
        public StringField Name;
        public StringField Description;
    }
}
