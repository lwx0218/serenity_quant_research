using System.Data;
using System.IO;
using Serenity.Data;
using SerenityQuantResearch.Research.Entities;

namespace SerenityQuantResearch.Research.Seed;

public interface IResearchSeedImporter
{
    ResearchSeedImportResult ImportDefault();
    ResearchSeedImportResult Import(ResearchSeedDocument seed);
}

public sealed class ResearchSeedImporter(ISqlConnections sqlConnections) : IResearchSeedImporter
{
    private const int SeedUserId = 1;
    private static readonly DateTime SeedAuditTime = new(2026, 8, 24, 0, 0, 0, DateTimeKind.Utc);
    private readonly ISqlConnections sqlConnections = sqlConnections ?? throw new ArgumentNullException(nameof(sqlConnections));

    public ResearchSeedImportResult ImportDefault()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "SeedData", "cpo-research-seed.json");
        if (!File.Exists(path))
            throw new FileNotFoundException("CPO research seed was not copied to the application output.", path);
        return Import(ResearchSeedValidator.Load(File.ReadAllText(path)));
    }

    public ResearchSeedImportResult Import(ResearchSeedDocument seed)
    {
        ResearchSeedValidator.Validate(seed);
        using var connection = sqlConnections.NewByKey("Default");
        using var uow = new UnitOfWork(connection);

        var themeId = GetOrInsertTheme(connection, seed.Theme);
        var chainId = GetOrInsertIndustryChain(connection, themeId, seed.IndustryChain);
        var nodeIds = InsertChainNodes(connection, chainId, seed.ChainNodes);
        var moduleIds = seed.Modules.ToDictionary(x => x.Id,
            x => GetOrInsertModule(connection, themeId, x), StringComparer.Ordinal);
        var partIds = InsertParts(connection, moduleIds, seed.Parts);
        var technologyIds = seed.TechnologyLinks.ToDictionary(x => x.Id,
            x => GetOrInsertTechnology(connection, themeId, x), StringComparer.Ordinal);
        var companyIds = seed.Companies.ToDictionary(x => x.Id,
            x => GetOrInsertCompany(connection, x), StringComparer.Ordinal);

        foreach (var mapping in seed.PartChainMappings)
            EnsurePartChainMapping(connection, partIds[mapping.PartId], nodeIds[mapping.ChainNodeId]);
        foreach (var mapping in seed.PartTechnologyMappings)
            EnsurePartTechnologyMapping(connection, partIds[mapping.PartId], technologyIds[mapping.TechnologyId]);

        InsertExampleChain(connection, seed.ExampleChain, partIds, nodeIds, technologyIds, companyIds);
        uow.Commit();

        return new ResearchSeedImportResult(
            seed.Modules.Count,
            seed.Parts.Count,
            seed.ChainNodes.Count,
            seed.Companies.Count,
            true);
    }

    private static int GetOrInsertTheme(IDbConnection connection, SeedTheme item)
    {
        var f = ThemeRow.Fields;
        var existing = connection.TryFirst<ThemeRow>(q => q.Select(f.ThemeId).Where(f.StableId == item.Id));
        if (existing?.ThemeId is int id)
            return id;
        return Convert.ToInt32(connection.InsertAndGetID(new ThemeRow
        {
            StableId = item.Id, Name = item.Name, Description = item.Description,
            InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        }));
    }

    private static int GetOrInsertIndustryChain(IDbConnection connection, int themeId, SeedIndustryChain item)
    {
        var f = IndustryChainRow.Fields;
        var existing = connection.TryFirst<IndustryChainRow>(q => q.Select(f.IndustryChainId).Where(f.StableId == item.Id));
        if (existing?.IndustryChainId is int id)
            return id;
        return Convert.ToInt32(connection.InsertAndGetID(new IndustryChainRow
        {
            StableId = item.Id, ThemeId = themeId, Name = item.Name, Description = item.Description,
            InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        }));
    }

    private static Dictionary<string, int> InsertChainNodes(IDbConnection connection, int chainId, IEnumerable<SeedChainNode> items)
    {
        var ids = new Dictionary<string, int>(StringComparer.Ordinal);
        var pending = items.ToList();
        while (pending.Count > 0)
        {
            var inserted = 0;
            foreach (var item in pending.ToList())
            {
                if (item.ParentId != null && !ids.ContainsKey(item.ParentId))
                    continue;
                var f = IndustryChainNodeRow.Fields;
                var existing = connection.TryFirst<IndustryChainNodeRow>(q => q.Select(f.IndustryChainNodeId).Where(f.StableId == item.Id));
                ids[item.Id] = existing?.IndustryChainNodeId ?? Convert.ToInt32(connection.InsertAndGetID(new IndustryChainNodeRow
                {
                    StableId = item.Id, IndustryChainId = chainId,
                    ParentNodeId = item.ParentId == null ? null : ids[item.ParentId],
                    Name = item.Name, NodeType = item.NodeType, SortOrder = item.SortOrder,
                    InsertDate = SeedAuditTime, InsertUserId = SeedUserId
                }));
                pending.Remove(item);
                inserted++;
            }
            if (inserted == 0)
                throw new InvalidDataException("Unable to resolve industry-chain parent order.");
        }
        return ids;
    }

    private static int GetOrInsertModule(IDbConnection connection, int themeId, SeedModule item)
    {
        var f = PhysicalModuleRow.Fields;
        var existing = connection.TryFirst<PhysicalModuleRow>(q => q.Select(f.PhysicalModuleId).Where(f.StableId == item.Id));
        if (existing?.PhysicalModuleId is int id)
            return id;
        return Convert.ToInt32(connection.InsertAndGetID(new PhysicalModuleRow
        {
            StableId = item.Id, ThemeId = themeId, Name = item.Name, Description = item.Description,
            SortOrder = item.SortOrder, InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        }));
    }

    private static Dictionary<string, int> InsertParts(IDbConnection connection,
        IReadOnlyDictionary<string, int> moduleIds, IEnumerable<SeedPart> items)
    {
        var ids = new Dictionary<string, int>(StringComparer.Ordinal);
        var pending = items.ToList();
        while (pending.Count > 0)
        {
            var inserted = 0;
            foreach (var item in pending.ToList())
            {
                if (item.ParentPartId != null && !ids.ContainsKey(item.ParentPartId))
                    continue;
                var f = PhysicalPartRow.Fields;
                var existing = connection.TryFirst<PhysicalPartRow>(q => q.Select(f.PhysicalPartId).Where(f.StableId == item.Id));
                ids[item.Id] = existing?.PhysicalPartId ?? Convert.ToInt32(connection.InsertAndGetID(new PhysicalPartRow
                {
                    StableId = item.Id, PhysicalModuleId = moduleIds[item.ModuleId],
                    ParentPartId = item.ParentPartId == null ? null : ids[item.ParentPartId],
                    Name = item.Name, FunctionSummary = item.FunctionSummary,
                    ResearchStatus = item.ResearchStatus, SortOrder = item.SortOrder,
                    InsertDate = SeedAuditTime, InsertUserId = SeedUserId
                }));
                pending.Remove(item);
                inserted++;
            }
            if (inserted == 0)
                throw new InvalidDataException("Unable to resolve physical-part parent order.");
        }
        return ids;
    }

    private static int GetOrInsertTechnology(IDbConnection connection, int themeId, SeedTechnology item)
    {
        var f = TechnologyLinkRow.Fields;
        var existing = connection.TryFirst<TechnologyLinkRow>(q => q.Select(f.TechnologyLinkId).Where(f.StableId == item.Id));
        if (existing?.TechnologyLinkId is int id)
            return id;
        return Convert.ToInt32(connection.InsertAndGetID(new TechnologyLinkRow
        {
            StableId = item.Id, ThemeId = themeId, Name = item.Name, Description = item.Description,
            InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        }));
    }

    private static int GetOrInsertCompany(IDbConnection connection, SeedCompany item)
    {
        var f = CompanyRow.Fields;
        var existing = connection.TryFirst<CompanyRow>(q => q.Select(f.CompanyId).Where(f.StableId == item.Id));
        if (existing?.CompanyId is int id)
            return id;
        return Convert.ToInt32(connection.InsertAndGetID(new CompanyRow
        {
            StableId = item.Id, Name = item.Name, EnglishName = item.EnglishName,
            Ticker = item.Ticker, Exchange = item.Exchange, CountryRegion = item.CountryRegion,
            UniverseLayer = item.UniverseLayer, CoveragePriority = item.CoveragePriority,
            OfficialUrl = item.OfficialUrl, InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        }));
    }

    private static void EnsurePartChainMapping(IDbConnection connection, int partId, int nodeId)
    {
        var f = PhysicalPartIndustryChainNodeRow.Fields;
        if (connection.Exists<PhysicalPartIndustryChainNodeRow>(f.PhysicalPartId == partId & f.IndustryChainNodeId == nodeId))
            return;
        connection.Insert(new PhysicalPartIndustryChainNodeRow
        {
            PhysicalPartId = partId, IndustryChainNodeId = nodeId,
            InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        });
    }

    private static void EnsurePartTechnologyMapping(IDbConnection connection, int partId, int technologyId)
    {
        var f = PhysicalPartTechnologyLinkRow.Fields;
        if (connection.Exists<PhysicalPartTechnologyLinkRow>(f.PhysicalPartId == partId & f.TechnologyLinkId == technologyId))
            return;
        connection.Insert(new PhysicalPartTechnologyLinkRow
        {
            PhysicalPartId = partId, TechnologyLinkId = technologyId,
            InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        });
    }

    private static void InsertExampleChain(IDbConnection connection, SeedExampleChain example,
        IReadOnlyDictionary<string, int> partIds, IReadOnlyDictionary<string, int> nodeIds,
        IReadOnlyDictionary<string, int> technologyIds, IReadOnlyDictionary<string, int> companyIds)
    {
        var partId = partIds[example.PartId];
        var nodeId = nodeIds[example.ChainNodeId];
        var technologyId = technologyIds[example.TechnologyId];
        var companyId = companyIds[example.CompanyId];

        var sourceFields = SourceDocumentRow.Fields;
        var source = connection.TryFirst<SourceDocumentRow>(q => q.Select(sourceFields.SourceDocumentId).Where(sourceFields.StableId == example.Source.Id));
        var sourceId = source?.SourceDocumentId ?? Convert.ToInt32(connection.InsertAndGetID(new SourceDocumentRow
        {
            StableId = example.Source.Id, SourceLevel = example.Source.SourceLevel,
            Publisher = example.Source.Publisher, Title = example.Source.Title,
            OriginalUrl = example.Source.OriginalUrl, CaptureTime = example.Source.CaptureTime,
            RightsNote = example.Source.RightsNote, InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        }));

        var exposureFields = CompanyExposureRow.Fields;
        var exposure = connection.TryFirst<CompanyExposureRow>(q => q.Select(exposureFields.CompanyExposureId).Where(
            exposureFields.CompanyId == companyId & exposureFields.PhysicalPartId == partId &
            exposureFields.IndustryChainNodeId == nodeId & exposureFields.Role == example.Exposure.Role));
        var exposureId = exposure?.CompanyExposureId ?? Convert.ToInt32(connection.InsertAndGetID(new CompanyExposureRow
        {
            CompanyId = companyId, PhysicalPartId = partId, IndustryChainNodeId = nodeId,
            Role = example.Exposure.Role, Relevance = example.Exposure.Relevance,
            Confidence = example.Exposure.Confidence, VerificationState = example.Exposure.VerificationState,
            ScopeNote = example.Exposure.ScopeNote, InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        }));

        var evidenceFields = EvidenceRow.Fields;
        var evidence = connection.TryFirst<EvidenceRow>(q => q.Select(evidenceFields.EvidenceId).Where(
            evidenceFields.StableId == example.Evidence.Id & evidenceFields.Version == example.Evidence.Version));
        var evidenceId = evidence?.EvidenceId ?? Convert.ToInt32(connection.InsertAndGetID(new EvidenceRow
        {
            StableId = example.Evidence.Id, Version = example.Evidence.Version,
            SourceDocumentId = sourceId, CompanyId = companyId, PhysicalPartId = partId,
            IndustryChainNodeId = nodeId, TechnologyLinkId = technologyId,
            Proposition = example.Evidence.Proposition, OriginalQuote = example.Evidence.OriginalQuote,
            Locator = example.Evidence.Locator, Stance = example.Evidence.Stance,
            ReviewState = example.Evidence.ReviewState, AnalystNote = example.Evidence.AnalystNote,
            InsertDate = SeedAuditTime, InsertUserId = SeedUserId
        }));

        var linkFields = CompanyExposureEvidenceRow.Fields;
        if (!connection.Exists<CompanyExposureEvidenceRow>(linkFields.CompanyExposureId == exposureId & linkFields.EvidenceId == evidenceId))
            connection.Insert(new CompanyExposureEvidenceRow
            {
                CompanyExposureId = exposureId, EvidenceId = evidenceId,
                InsertDate = SeedAuditTime, InsertUserId = SeedUserId
            });
    }
}
