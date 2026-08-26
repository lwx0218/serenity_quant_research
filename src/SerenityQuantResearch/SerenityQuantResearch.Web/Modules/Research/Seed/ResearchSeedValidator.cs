using System.IO;
using System.Text.Json;
using SerenityQuantResearch.Research.Domain;

namespace SerenityQuantResearch.Research.Seed;

public static class ResearchSeedValidator
{
    public static ResearchSeedDocument Load(string json)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(json);
        var seed = JsonSerializer.Deserialize<ResearchSeedDocument>(json,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ??
            throw new InvalidDataException("Research seed JSON is empty.");
        Validate(seed);
        return seed;
    }

    public static void Validate(ResearchSeedDocument seed)
    {
        ArgumentNullException.ThrowIfNull(seed);
        Require(seed.Theme?.Id, "theme.id");
        Require(seed.Theme?.Name, "theme.name");
        Require(seed.IndustryChain?.Id, "industryChain.id");
        Require(seed.IndustryChain?.Name, "industryChain.name");

        var moduleIds = UniqueIds(seed.Modules, x => x.Id, "module");
        var partIds = UniqueIds(seed.Parts, x => x.Id, "part");
        var nodeIds = UniqueIds(seed.ChainNodes, x => x.Id, "chain node");
        var technologyIds = UniqueIds(seed.TechnologyLinks, x => x.Id, "technology");
        var companyIds = UniqueIds(seed.Companies, x => x.Id, "company");

        foreach (var module in seed.Modules)
            Require(module.Name, $"module '{module.Id}' name");

        foreach (var part in seed.Parts)
        {
            Require(part.Name, $"part '{part.Id}' name");
            Require(part.ResearchStatus, $"part '{part.Id}' researchStatus");
            if (!moduleIds.Contains(part.ModuleId))
                throw new InvalidDataException($"Part '{part.Id}' references missing module '{part.ModuleId}'.");
            if (part.ParentPartId != null && !partIds.Contains(part.ParentPartId))
                throw new InvalidDataException($"Part '{part.Id}' references missing parent '{part.ParentPartId}'.");
            if (part.ParentPartId == part.Id)
                throw new InvalidDataException($"Part '{part.Id}' cannot be its own parent.");
        }
        EnsureAcyclic(seed.Parts);

        foreach (var node in seed.ChainNodes)
        {
            Require(node.Name, $"chain node '{node.Id}' name");
            Require(node.NodeType, $"chain node '{node.Id}' nodeType");
            if (node.ParentId != null && !nodeIds.Contains(node.ParentId))
                throw new InvalidDataException($"Chain node '{node.Id}' references missing parent '{node.ParentId}'.");
        }

        foreach (var mapping in seed.PartChainMappings)
        {
            if (!partIds.Contains(mapping.PartId) || !nodeIds.Contains(mapping.ChainNodeId))
                throw new InvalidDataException($"Invalid part-chain mapping '{mapping.PartId}' -> '{mapping.ChainNodeId}'.");
        }

        foreach (var mapping in seed.PartTechnologyMappings)
        {
            if (!partIds.Contains(mapping.PartId) || !technologyIds.Contains(mapping.TechnologyId))
                throw new InvalidDataException($"Invalid part-technology mapping '{mapping.PartId}' -> '{mapping.TechnologyId}'.");
        }

        foreach (var company in seed.Companies)
        {
            Require(company.Name, $"company '{company.Id}' name");
            Require(company.UniverseLayer, $"company '{company.Id}' universeLayer");
            Require(company.CoveragePriority, $"company '{company.Id}' coveragePriority");
        }

        var example = seed.ExampleChain ?? throw new InvalidDataException("exampleChain is required.");
        if (!partIds.Contains(example.PartId) || !nodeIds.Contains(example.ChainNodeId) ||
            !technologyIds.Contains(example.TechnologyId) || !companyIds.Contains(example.CompanyId))
            throw new InvalidDataException("exampleChain references an unknown object.");
        Require(example.Exposure?.VerificationState, "exampleChain.exposure.verificationState");
        Require(example.Source?.Id, "exampleChain.source.id");
        Require(example.Source?.OriginalUrl, "exampleChain.source.originalUrl");
        if (example.Source?.SourceLevel is not ("A" or "B" or "C"))
            throw new InvalidDataException("exampleChain.source.sourceLevel must be A, B or C.");
        Require(example.Evidence?.Id, "exampleChain.evidence.id");
        if (!EvidenceReviewStates.All.Contains(example.Evidence?.ReviewState ?? string.Empty))
            throw new InvalidDataException("exampleChain.evidence.reviewState is invalid.");
        if (example.Evidence?.ReviewState != EvidenceReviewStates.Draft)
            throw new InvalidDataException("Machine-assisted seed evidence must start as draft.");
    }

    private static HashSet<string> UniqueIds<T>(IEnumerable<T> items, Func<T, string> selector, string label)
    {
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var item in items ?? [])
        {
            var id = selector(item);
            Require(id, $"{label} id");
            if (!ids.Add(id))
                throw new InvalidDataException($"Duplicate {label} id '{id}'.");
        }
        if (ids.Count == 0)
            throw new InvalidDataException($"At least one {label} is required.");
        return ids;
    }

    private static void EnsureAcyclic(IEnumerable<SeedPart> parts)
    {
        var parentById = parts.ToDictionary(x => x.Id, x => x.ParentPartId, StringComparer.Ordinal);
        foreach (var start in parentById.Keys)
        {
            var seen = new HashSet<string>(StringComparer.Ordinal);
            var current = start;
            while (current != null && parentById.TryGetValue(current, out var parent))
            {
                if (!seen.Add(current))
                    throw new InvalidDataException($"Physical part hierarchy contains a cycle at '{current}'.");
                current = parent;
            }
        }
    }

    private static void Require(string value, string field)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new InvalidDataException($"Required seed field '{field}' is missing.");
    }
}
