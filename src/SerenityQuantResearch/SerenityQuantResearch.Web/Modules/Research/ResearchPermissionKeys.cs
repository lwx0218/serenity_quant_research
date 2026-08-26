namespace SerenityQuantResearch.Research;

[NestedPermissionKeys]
[DisplayName("Research")]
public static class ResearchPermissionKeys
{
    [Description("Read and maintain research drafts")]
    public const string General = "Research:General";

    [Description("Review evidence and company exposure")]
    public const string Review = "Research:Review";

    [Description("Publish conclusions and reports")]
    public const string Publish = "Research:Publish";
}
