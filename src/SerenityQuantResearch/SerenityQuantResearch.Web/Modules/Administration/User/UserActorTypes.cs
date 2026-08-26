namespace SerenityQuantResearch.Administration;

public static class UserActorTypes
{
    public const string Human = "human";
    public const string Machine = "machine";

    public static readonly IReadOnlySet<string> All = new HashSet<string>(StringComparer.Ordinal)
    {
        Human, Machine
    };
}
