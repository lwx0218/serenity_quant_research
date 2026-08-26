namespace SerenityQuantResearch.Research.Seed;

public sealed class ResearchSeedDocument
{
    public SeedTheme Theme { get; set; }
    public SeedIndustryChain IndustryChain { get; set; }
    public List<SeedChainNode> ChainNodes { get; set; } = [];
    public List<SeedModule> Modules { get; set; } = [];
    public List<SeedPart> Parts { get; set; } = [];
    public List<SeedTechnology> TechnologyLinks { get; set; } = [];
    public List<SeedPartChainMapping> PartChainMappings { get; set; } = [];
    public List<SeedPartTechnologyMapping> PartTechnologyMappings { get; set; } = [];
    public List<SeedCompany> Companies { get; set; } = [];
    public SeedExampleChain ExampleChain { get; set; }
}

public sealed class SeedTheme { public string Id { get; set; } public string Name { get; set; } public string Description { get; set; } }
public sealed class SeedIndustryChain { public string Id { get; set; } public string Name { get; set; } public string Description { get; set; } }
public sealed class SeedChainNode { public string Id { get; set; } public string ParentId { get; set; } public string Name { get; set; } public string NodeType { get; set; } public int SortOrder { get; set; } }
public sealed class SeedModule { public string Id { get; set; } public string Name { get; set; } public string Description { get; set; } public int SortOrder { get; set; } }
public sealed class SeedPart { public string Id { get; set; } public string ModuleId { get; set; } public string ParentPartId { get; set; } public string Name { get; set; } public string FunctionSummary { get; set; } public string ResearchStatus { get; set; } public int SortOrder { get; set; } }
public sealed class SeedTechnology { public string Id { get; set; } public string Name { get; set; } public string Description { get; set; } }
public sealed class SeedPartChainMapping { public string PartId { get; set; } public string ChainNodeId { get; set; } }
public sealed class SeedPartTechnologyMapping { public string PartId { get; set; } public string TechnologyId { get; set; } }
public sealed class SeedCompany { public string Id { get; set; } public string Name { get; set; } public string EnglishName { get; set; } public string Ticker { get; set; } public string Exchange { get; set; } public string CountryRegion { get; set; } public string UniverseLayer { get; set; } public string CoveragePriority { get; set; } public string OfficialUrl { get; set; } }
public sealed class SeedExposure { public string Role { get; set; } public string Relevance { get; set; } public string Confidence { get; set; } public string VerificationState { get; set; } public string ScopeNote { get; set; } }
public sealed class SeedSource { public string Id { get; set; } public string SourceLevel { get; set; } public string Publisher { get; set; } public string Title { get; set; } public string OriginalUrl { get; set; } public DateTime CaptureTime { get; set; } public string RightsNote { get; set; } }
public sealed class SeedEvidence { public string Id { get; set; } public int Version { get; set; } public string Proposition { get; set; } public string OriginalQuote { get; set; } public string Locator { get; set; } public string Stance { get; set; } public string ReviewState { get; set; } public string AnalystNote { get; set; } }
public sealed class SeedExampleChain
{
    public string PartId { get; set; }
    public string ChainNodeId { get; set; }
    public string TechnologyId { get; set; }
    public string CompanyId { get; set; }
    public SeedExposure Exposure { get; set; }
    public SeedSource Source { get; set; }
    public SeedEvidence Evidence { get; set; }
}

public sealed record ResearchSeedImportResult(
    int Modules,
    int Parts,
    int ChainNodes,
    int Companies,
    bool ExampleChainAvailable);
