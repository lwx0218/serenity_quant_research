using System.Data;
using SerenityQuantResearch.Research.Entities;

namespace SerenityQuantResearch.Research.Services;

public sealed class ResearchWorkspaceRequest : ServiceRequest
{
    public string ObjectType { get; set; }
    public string ObjectId { get; set; }
    public string Source { get; set; }
    public string ComponentId { get; set; }
    public string PartId { get; set; }
    public string ChainNodeId { get; set; }
    public string CompanyId { get; set; }
    public string View { get; set; }
}

public sealed class ResearchWorkspaceResponse : ServiceResponse
{
    public WorkspaceObjectSummary CurrentObject { get; set; }
    public List<string> SourcePath { get; set; } = [];
    public List<WorkspaceTreeGroup> Tree { get; set; } = [];
    public List<WorkspaceObjectSummary> LinkedObjects { get; set; } = [];
    public List<WorkspaceBacklink> Backlinks { get; set; } = [];
    public List<WorkspaceEvidenceContext> Evidence { get; set; } = [];
    public List<ResearchSectionSummary> Conclusions { get; set; } = [];
    public List<ResearchSectionSummary> Gaps { get; set; } = [];
    public List<ResearchSectionSummary> Status { get; set; } = [];
    public bool IsReadOnly { get; set; } = true;
}

public sealed record WorkspaceObjectSummary(string ObjectType, string Id, string Name, string Subtitle, string State, string Description);
public sealed record WorkspaceTreeGroup(string Name, List<WorkspaceObjectSummary> Items);
public sealed record WorkspaceBacklink(string ObjectType, string ObjectId, string Label, string Context, string State);
public sealed record WorkspaceEvidenceContext(string EvidenceId, int Version, string Proposition, string Stance, string ReviewState,
    string SourceLevel, string SourceTitle, string Locator);

public interface IResearchWorkspaceService
{
    ResearchWorkspaceResponse Retrieve(IDbConnection connection, ResearchWorkspaceRequest request);
}

public sealed class ResearchWorkspaceService : IResearchWorkspaceService
{
    private const string DefaultComponentId = "cpo.mod.pic";

    public ResearchWorkspaceResponse Retrieve(IDbConnection connection, ResearchWorkspaceRequest request)
    {
        ArgumentNullException.ThrowIfNull(connection);
        ArgumentNullException.ThrowIfNull(request);

        var data = LoadData(connection);
        var objectType = NormalizeObjectType(request.ObjectType) ?? InferObjectType(request);
        var objectId = FirstNonEmpty(request.ObjectId, objectType switch
        {
            "component" => request.ComponentId,
            "part" => request.PartId,
            "company" => request.CompanyId,
            "technology" => request.ObjectId,
            "chainNode" => request.ChainNodeId,
            _ => null
        });

        if (string.IsNullOrWhiteSpace(objectId))
            objectId = objectType == "component" ? DefaultComponentId : throw new ValidationError("WorkspaceObjectRequired", "A Workspace object type and stable ID are required.");

        var response = objectType switch
        {
            "component" => BuildComponent(data, objectId),
            "part" => BuildPart(data, objectId),
            "company" => BuildCompany(data, objectId),
            "technology" => BuildTechnology(data, objectId),
            "chainNode" => BuildChainNode(data, objectId),
            _ => throw new ValidationError("WorkspaceObjectTypeUnsupported", $"Workspace object type '{objectType}' is not supported.")
        };

        response.SourcePath = BuildSourcePath(data, request, response.CurrentObject);
        response.Tree = BuildTree(data, response.CurrentObject);
        response.IsReadOnly = true;
        return response;
    }

    private static ResearchWorkspaceResponse BuildComponent(LoadedWorkspaceData data, string moduleStableId)
    {
        var module = data.Modules.SingleOrDefault(x => x.StableId == moduleStableId) ??
            throw new ValidationError("WorkspaceComponentNotFound", $"Physical component '{moduleStableId}' was not found.");
        var parts = data.Parts.Where(x => x.PhysicalModuleId == module.PhysicalModuleId).OrderBy(x => x.SortOrder).ToList();
        var partIds = parts.Select(x => x.PhysicalPartId!.Value).ToHashSet();
        var response = CreateResponse(new WorkspaceObjectSummary("component", module.StableId, module.Name,
            "Physical component group", "Candidate", module.Description ?? "Existing physical module from the CPO taxonomy."));

        response.LinkedObjects.AddRange(parts.Select(part => ToPartSummary(part, data.ModulesById[part.PhysicalModuleId!.Value])));
        AddTechnologyLinks(response, data, partIds);
        AddChainNodeLinks(response, data, partIds);
        AddCompanyLinksForParts(response, data, partIds);
        AddEvidence(response, data, EvidenceForParts(data, partIds));
        response.Backlinks.AddRange(parts.Select(part => new WorkspaceBacklink("part", part.StableId, part.Name,
            $"Child physical part inside {module.Name}; derived from PhysicalPart.PhysicalModuleId.", SafeState(part.ResearchStatus))));
        foreach (var exposure in data.Exposures.Where(x => x.PhysicalPartId is int id && partIds.Contains(id)).OrderBy(x => data.CompaniesById[x.CompanyId!.Value].Name))
        {
            var company = data.CompaniesById[exposure.CompanyId!.Value];
            var part = data.PartsById[exposure.PhysicalPartId!.Value];
            response.Backlinks.Add(new WorkspaceBacklink("company", company.StableId, company.Name,
                $"CompanyExposure links {company.Name} to child part {part.Name}; verification remains {SafeState(exposure.VerificationState)}.", SafeState(exposure.VerificationState)));
        }
        AddEvidenceBacklinks(response, data, response.Evidence);
        AddConclusionContext(response, data);
        AddComponentGaps(response, module.Name, parts.Count);
        return response;
    }

    private static ResearchWorkspaceResponse BuildPart(LoadedWorkspaceData data, string partStableId)
    {
        var part = data.Parts.SingleOrDefault(x => x.StableId == partStableId) ??
            throw new ValidationError("WorkspacePartNotFound", $"Physical part '{partStableId}' was not found.");
        var module = data.ModulesById[part.PhysicalModuleId!.Value];
        var partIds = new HashSet<int> { part.PhysicalPartId!.Value };
        var response = CreateResponse(ToPartSummary(part, module));

        response.LinkedObjects.Add(new WorkspaceObjectSummary("component", module.StableId, module.Name,
            "Parent physical component", "Candidate", module.Description ?? "Existing module relationship."));
        AddTechnologyLinks(response, data, partIds);
        AddChainNodeLinks(response, data, partIds);
        AddCompanyLinksForParts(response, data, partIds);
        AddEvidence(response, data, EvidenceForParts(data, partIds));
        response.Backlinks.Add(new WorkspaceBacklink("component", module.StableId, module.Name,
            $"Parent component for {part.Name}; derived from PhysicalPart.PhysicalModuleId.", "Candidate"));
        foreach (var exposure in data.Exposures.Where(x => x.PhysicalPartId == part.PhysicalPartId).OrderBy(x => data.CompaniesById[x.CompanyId!.Value].Name))
        {
            var company = data.CompaniesById[exposure.CompanyId!.Value];
            response.Backlinks.Add(new WorkspaceBacklink("company", company.StableId, company.Name,
                $"Explicit CompanyExposure references {part.Name}; state {SafeState(exposure.VerificationState)}.", SafeState(exposure.VerificationState)));
        }
        AddEvidenceBacklinks(response, data, response.Evidence);
        AddConclusionContext(response, data);
        AddPartGaps(response, part);
        return response;
    }

    private static ResearchWorkspaceResponse BuildCompany(LoadedWorkspaceData data, string companyStableId)
    {
        var company = data.Companies.SingleOrDefault(x => x.StableId == companyStableId) ??
            throw new ValidationError("WorkspaceCompanyNotFound", $"Company '{companyStableId}' was not found.");
        var exposures = data.Exposures.Where(x => x.CompanyId == company.CompanyId).OrderBy(x => x.Role).ToList();
        var response = CreateResponse(new WorkspaceObjectSummary("company", company.StableId, company.Name,
            $"{company.EnglishName ?? "English name Unknown"} · {company.Ticker ?? "Ticker Unknown"} · {company.CountryRegion ?? "Unknown"}",
            CoverageState(data, company, exposures), company.OfficialUrl ?? "Official URL Unknown"));

        foreach (var exposure in exposures)
        {
            if (exposure.PhysicalPartId is int partId && data.PartsById.TryGetValue(partId, out var part))
                response.LinkedObjects.Add(ToPartSummary(part, data.ModulesById[part.PhysicalModuleId!.Value]));
            if (exposure.IndustryChainNodeId is int nodeId && data.NodesById.TryGetValue(nodeId, out var node))
                response.LinkedObjects.Add(ToChainNodeSummary(node));
        }
        AddEvidence(response, data, EvidenceForCompany(data, company, exposures));
        foreach (var exposure in exposures)
        {
            var partName = exposure.PhysicalPartId is int partId && data.PartsById.TryGetValue(partId, out var part) ? part.Name : "part Unknown";
            var nodeName = exposure.IndustryChainNodeId is int nodeId && data.NodesById.TryGetValue(nodeId, out var node) ? node.Name : "chain node Unknown";
            response.Backlinks.Add(new WorkspaceBacklink("company", company.StableId, company.Name,
                $"CompanyExposure keeps {partName} / {nodeName} as read-only relationship context; state {SafeState(exposure.VerificationState)}.", SafeState(exposure.VerificationState)));
        }
        AddEvidenceBacklinks(response, data, response.Evidence);
        AddConclusionContext(response, data);
        AddCompanyGaps(response, company, exposures);
        return response;
    }

    private static ResearchWorkspaceResponse BuildTechnology(LoadedWorkspaceData data, string technologyStableId)
    {
        var technology = data.Technologies.SingleOrDefault(x => x.StableId == technologyStableId) ??
            throw new ValidationError("WorkspaceTechnologyNotFound", $"Technology '{technologyStableId}' was not found.");
        var partIds = data.PartTechnologyLinks.Where(x => x.TechnologyLinkId == technology.TechnologyLinkId)
            .Select(x => x.PhysicalPartId!.Value).ToHashSet();
        var response = CreateResponse(ToTechnologySummary(technology));
        response.LinkedObjects.AddRange(partIds.Select(id => data.PartsById[id]).OrderBy(x => x.Name)
            .Select(part => ToPartSummary(part, data.ModulesById[part.PhysicalModuleId!.Value])));
        AddCompanyLinksForParts(response, data, partIds);
        AddEvidence(response, data, data.Evidence.Where(x => x.TechnologyLinkId == technology.TechnologyLinkId).ToList());
        foreach (var partId in partIds)
        {
            var part = data.PartsById[partId];
            response.Backlinks.Add(new WorkspaceBacklink("part", part.StableId, part.Name,
                $"PhysicalPartTechnologyLink references {technology.Name}.", SafeState(part.ResearchStatus)));
        }
        AddEvidenceBacklinks(response, data, response.Evidence);
        AddConclusionContext(response, data);
        response.Gaps.Add(new ResearchSectionSummary("unresolved", "Technology Workspace only shows explicit part/evidence links; it does not infer material adoption or supplier status."));
        return response;
    }

    private static ResearchWorkspaceResponse BuildChainNode(LoadedWorkspaceData data, string nodeStableId)
    {
        var node = data.Nodes.SingleOrDefault(x => x.StableId == nodeStableId) ??
            throw new ValidationError("WorkspaceChainNodeNotFound", $"Industry-chain node '{nodeStableId}' was not found.");
        var partIds = data.PartChainLinks.Where(x => x.IndustryChainNodeId == node.IndustryChainNodeId)
            .Select(x => x.PhysicalPartId!.Value).ToHashSet();
        var response = CreateResponse(ToChainNodeSummary(node));
        response.LinkedObjects.AddRange(partIds.Select(id => data.PartsById[id]).OrderBy(x => x.Name)
            .Select(part => ToPartSummary(part, data.ModulesById[part.PhysicalModuleId!.Value])));
        foreach (var exposure in data.Exposures.Where(x => x.IndustryChainNodeId == node.IndustryChainNodeId).OrderBy(x => data.CompaniesById[x.CompanyId!.Value].Name))
        {
            var company = data.CompaniesById[exposure.CompanyId!.Value];
            response.LinkedObjects.Add(ToCompanySummary(data, company));
            response.Backlinks.Add(new WorkspaceBacklink("company", company.StableId, company.Name,
                $"CompanyExposure references this chain node; verification remains {SafeState(exposure.VerificationState)}.", SafeState(exposure.VerificationState)));
        }
        AddEvidence(response, data, data.Evidence.Where(x => x.IndustryChainNodeId == node.IndustryChainNodeId).ToList());
        AddEvidenceBacklinks(response, data, response.Evidence);
        AddConclusionContext(response, data);
        response.Gaps.Add(new ResearchSectionSummary("unresolved", "Chain-node Workspace shows explicit mappings only; directionality, supplier/customer status, and production exposure remain unresolved unless evidence supports them."));
        return response;
    }

    private static ResearchWorkspaceResponse CreateResponse(WorkspaceObjectSummary current) => new()
    {
        CurrentObject = current,
        Status =
        [
            new ResearchSectionSummary("read-only", "Workspace v1 is read-only and linked-object-first; it exposes no write command metadata."),
            new ResearchSectionSummary("research-state", $"Current object state: {SafeState(current.State)}.")
        ]
    };

    private static void AddTechnologyLinks(ResearchWorkspaceResponse response, LoadedWorkspaceData data, HashSet<int> partIds)
    {
        var technologyIds = data.PartTechnologyLinks.Where(x => partIds.Contains(x.PhysicalPartId!.Value))
            .Select(x => x.TechnologyLinkId!.Value).Distinct().ToHashSet();
        response.LinkedObjects.AddRange(technologyIds.Select(id => data.TechnologiesById[id]).OrderBy(x => x.Name).Select(ToTechnologySummary));
    }

    private static void AddChainNodeLinks(ResearchWorkspaceResponse response, LoadedWorkspaceData data, HashSet<int> partIds)
    {
        var nodeIds = data.PartChainLinks.Where(x => partIds.Contains(x.PhysicalPartId!.Value))
            .Select(x => x.IndustryChainNodeId!.Value).Distinct().ToHashSet();
        response.LinkedObjects.AddRange(nodeIds.Select(id => data.NodesById[id]).OrderBy(x => x.SortOrder).Select(ToChainNodeSummary));
    }

    private static void AddCompanyLinksForParts(ResearchWorkspaceResponse response, LoadedWorkspaceData data, HashSet<int> partIds)
    {
        var companies = data.Exposures.Where(x => x.PhysicalPartId is int id && partIds.Contains(id))
            .GroupBy(x => x.CompanyId!.Value).Select(x => data.CompaniesById[x.Key]).OrderBy(x => x.Name);
        response.LinkedObjects.AddRange(companies.Select(company => ToCompanySummary(data, company)));
    }

    private static List<EvidenceRow> EvidenceForParts(LoadedWorkspaceData data, HashSet<int> partIds)
    {
        var exposureIds = data.Exposures.Where(x => x.PhysicalPartId is int id && partIds.Contains(id))
            .Select(x => x.CompanyExposureId!.Value).ToHashSet();
        var evidenceIds = data.ExposureEvidence.Where(x => exposureIds.Contains(x.CompanyExposureId!.Value))
            .Select(x => x.EvidenceId!.Value).ToHashSet();
        return data.Evidence.Where(x => (x.PhysicalPartId is int partId && partIds.Contains(partId)) || evidenceIds.Contains(x.EvidenceId!.Value)).ToList();
    }

    private static List<EvidenceRow> EvidenceForCompany(LoadedWorkspaceData data, CompanyRow company, List<CompanyExposureRow> exposures)
    {
        var exposureIds = exposures.Select(x => x.CompanyExposureId!.Value).ToHashSet();
        var evidenceIds = data.ExposureEvidence.Where(x => exposureIds.Contains(x.CompanyExposureId!.Value))
            .Select(x => x.EvidenceId!.Value).ToHashSet();
        return data.Evidence.Where(x => x.CompanyId == company.CompanyId || evidenceIds.Contains(x.EvidenceId!.Value)).ToList();
    }

    private static void AddEvidence(ResearchWorkspaceResponse response, LoadedWorkspaceData data, List<EvidenceRow> evidenceRows)
    {
        foreach (var item in evidenceRows.GroupBy(x => x.EvidenceId!.Value).Select(x => x.First()).OrderBy(x => x.StableId))
        {
            var source = data.SourcesById[item.SourceDocumentId!.Value];
            response.Evidence.Add(new WorkspaceEvidenceContext(item.StableId, item.Version!.Value, item.Proposition,
                item.Stance, SafeState(item.ReviewState), source.SourceLevel, source.Title, item.Locator));
        }
        if (response.Evidence.Count == 0)
            response.Status.Add(new ResearchSectionSummary("not-reviewed", "No direct evidence relationship is available for this Workspace object; absence is a research gap, not a conclusion."));
        else if (response.Evidence.Any(x => x.ReviewState != "reviewed"))
            response.Status.Add(new ResearchSectionSummary("not-reviewed", "Draft / in_review evidence is visible as context only and is not upgraded to reviewed fact."));
    }

    private static void AddEvidenceBacklinks(ResearchWorkspaceResponse response, LoadedWorkspaceData data, List<WorkspaceEvidenceContext> evidence)
    {
        var evidenceIds = evidence.Select(x => x.EvidenceId).ToHashSet(StringComparer.Ordinal);
        foreach (var item in data.Evidence.Where(x => evidenceIds.Contains(x.StableId)).OrderBy(x => x.StableId))
            response.Backlinks.Add(new WorkspaceBacklink("evidence", item.StableId, $"{item.StableId}@v{item.Version}",
                $"Evidence {SafeState(item.ReviewState)} · {item.Stance}; link is derived from existing evidence/exposure rows.", SafeState(item.ReviewState)));
    }

    private static void AddConclusionContext(ResearchWorkspaceResponse response, LoadedWorkspaceData data)
    {
        var evidenceIds = data.Evidence.Where(x => response.Evidence.Any(e => e.EvidenceId == x.StableId))
            .Select(x => x.EvidenceId!.Value).ToHashSet();
        var conclusionIds = data.ConclusionEvidence.Where(x => evidenceIds.Contains(x.EvidenceId!.Value))
            .Select(x => x.ResearchConclusionId!.Value).Distinct().ToHashSet();
        var conclusions = data.Conclusions.Where(x => conclusionIds.Contains(x.ResearchConclusionId!.Value)).OrderBy(x => x.StableId).ToList();
        if (conclusions.Count == 0)
        {
            response.Conclusions.Add(new ResearchSectionSummary("none", "No existing conclusion resolves through this object's evidence relationships; gaps below are not conclusions."));
            return;
        }
        response.Conclusions.AddRange(conclusions.Select(x => new ResearchSectionSummary(SafeState(x.PublicationState),
            $"{x.StableId}@v{x.Version}: {x.Statement}")));
    }

    private static void AddComponentGaps(ResearchWorkspaceResponse response, string moduleName, int childCount)
    {
        if (childCount == 0)
            response.Gaps.Add(new ResearchSectionSummary("unresolved", $"{moduleName} has no explicit child parts in the current taxonomy."));
        if (response.Evidence.Count == 0)
            response.Gaps.Add(new ResearchSectionSummary("unresolved", "Which Level A/B sources directly support this component boundary?"));
        response.Gaps.Add(new ResearchSectionSummary("unresolved", "Existing part/company adjacency is candidate relationship context; it must not be read as supplier, customer, production, or investment conclusion."));
    }

    private static void AddPartGaps(ResearchWorkspaceResponse response, PhysicalPartRow part)
    {
        response.Gaps.Add(new ResearchSectionSummary("unresolved", part.ResearchStatus switch
        {
            "architecture_option" => "Is this architecture option used in a specific product, and what alternate route is evidenced?",
            "product_candidate" => "Does a product-level primary source support this candidate product form?",
            "product_boundary_pending" => "Is this function a separate physical part in the product under review?",
            "interface_option" => "Which interface standard and system boundary are evidenced?",
            _ => "Which source verifies this object's specifications, integration boundary, validation phase, and production state?"
        }));
        if (response.Evidence.Count == 0)
            response.Gaps.Add(new ResearchSectionSummary("unresolved", "No direct evidence is linked; add no inferred facts in Workspace v1."));
    }

    private static void AddCompanyGaps(ResearchWorkspaceResponse response, CompanyRow company, List<CompanyExposureRow> exposures)
    {
        if (exposures.Count == 0)
            response.Gaps.Add(new ResearchSectionSummary("unresolved", $"{company.Name} has no explicit CompanyExposure rows; do not infer component exposure from identity or keywords."));
        if (response.Evidence.Count == 0)
            response.Gaps.Add(new ResearchSectionSummary("unresolved", "No explicit company/evidence audit relationship is available."));
        response.Gaps.Add(new ResearchSectionSummary("unresolved", "Candidate exposure, draft evidence, and unmapped fields remain separate from verified conclusions."));
    }

    private static List<WorkspaceTreeGroup> BuildTree(LoadedWorkspaceData data, WorkspaceObjectSummary current) =>
    [
        new WorkspaceTreeGroup("Physical Components", data.Modules.OrderBy(x => x.SortOrder)
            .Select(x => new WorkspaceObjectSummary("component", x.StableId, x.Name, "Component", current.Id == x.StableId ? "current" : "Candidate", x.Description)).ToList()),
        new WorkspaceTreeGroup("Physical Parts", data.Parts.OrderBy(x => x.SortOrder)
            .Take(12).Select(x => ToPartSummary(x, data.ModulesById[x.PhysicalModuleId!.Value])).ToList()),
        new WorkspaceTreeGroup("Technologies", data.Technologies.OrderBy(x => x.Name).Select(ToTechnologySummary).ToList()),
        new WorkspaceTreeGroup("Companies", data.Companies.OrderBy(x => x.Name).Take(12).Select(x => ToCompanySummary(data, x)).ToList())
    ];

    private static List<string> BuildSourcePath(LoadedWorkspaceData data, ResearchWorkspaceRequest request, WorkspaceObjectSummary current)
    {
        var path = new List<string> { request.Source == "cpo-explorer" ? "CPO Explorer" : request.Source == "company-detail" ? "Company Detail" : request.Source == "company-pool" ? "Company Pool" : "Research Workspace" };
        if (!string.IsNullOrWhiteSpace(request.ComponentId) && data.ModulesByStableId.TryGetValue(request.ComponentId, out var module))
            path.Add(module.Name);
        if (!string.IsNullOrWhiteSpace(request.PartId) && data.PartsByStableId.TryGetValue(request.PartId, out var part))
            path.Add(part.Name);
        if (!string.IsNullOrWhiteSpace(request.ChainNodeId) && data.NodesByStableId.TryGetValue(request.ChainNodeId, out var node))
            path.Add(node.Name);
        if (!string.IsNullOrWhiteSpace(request.CompanyId) && data.CompaniesByStableId.TryGetValue(request.CompanyId, out var company))
            path.Add(company.Name);
        if (!path.Contains(current.Name, StringComparer.Ordinal))
            path.Add(current.Name);
        return path;
    }

    private static WorkspaceObjectSummary ToPartSummary(PhysicalPartRow part, PhysicalModuleRow module) =>
        new("part", part.StableId, part.Name, module.Name, SafeState(part.ResearchStatus), part.FunctionSummary ?? "Function summary Unknown");

    private static WorkspaceObjectSummary ToTechnologySummary(TechnologyLinkRow technology) =>
        new("technology", technology.StableId, technology.Name, "Technology route", "Candidate", technology.Description ?? "Description Unknown");

    private static WorkspaceObjectSummary ToChainNodeSummary(IndustryChainNodeRow node) =>
        new("chainNode", node.StableId, node.Name, "Industry-chain node", "Candidate", node.NodeType ?? "Node type Unknown");

    private static WorkspaceObjectSummary ToCompanySummary(LoadedWorkspaceData data, CompanyRow company) =>
        new("company", company.StableId, company.Name, company.EnglishName ?? "English name Unknown",
            CoverageState(data, company, data.Exposures.Where(x => x.CompanyId == company.CompanyId).ToList()),
            company.CountryRegion ?? "Country / region Unknown");

    private static string CoverageState(LoadedWorkspaceData data, CompanyRow company, List<CompanyExposureRow> exposures)
    {
        if (exposures.Count == 0)
            return "Unknown";
        if (exposures.Any(x => string.Equals(x.VerificationState, "verified", StringComparison.Ordinal)))
            return "verified";
        if (exposures.Any(x => string.Equals(x.VerificationState, "candidate", StringComparison.Ordinal)))
            return "Candidate";
        return SafeState(exposures.Select(x => x.VerificationState).FirstOrDefault());
    }

    private static string NormalizeObjectType(string value) => value switch
    {
        "component" or "module" => "component",
        "part" => "part",
        "company" => "company",
        "technology" or "tech" => "technology",
        "chainNode" or "chain" or "node" => "chainNode",
        _ => string.IsNullOrWhiteSpace(value) ? null : value
    };

    private static string InferObjectType(ResearchWorkspaceRequest request)
    {
        if (!string.IsNullOrWhiteSpace(request.CompanyId))
            return "company";
        if (!string.IsNullOrWhiteSpace(request.PartId))
            return "part";
        if (!string.IsNullOrWhiteSpace(request.ChainNodeId))
            return "chainNode";
        return "component";
    }

    private static string FirstNonEmpty(params string[] values) => values.FirstOrDefault(x => !string.IsNullOrWhiteSpace(x));
    private static string SafeState(string value) => string.IsNullOrWhiteSpace(value) ? "Unknown" : value;

    private static LoadedWorkspaceData LoadData(IDbConnection connection)
    {
        return new LoadedWorkspaceData(
            connection.List<PhysicalModuleRow>(q => q.SelectTableFields()),
            connection.List<PhysicalPartRow>(q => q.SelectTableFields()),
            connection.List<TechnologyLinkRow>(q => q.SelectTableFields()),
            connection.List<PhysicalPartTechnologyLinkRow>(q => q.SelectTableFields()),
            connection.List<IndustryChainNodeRow>(q => q.SelectTableFields()),
            connection.List<PhysicalPartIndustryChainNodeRow>(q => q.SelectTableFields()),
            connection.List<CompanyRow>(q => q.SelectTableFields()),
            connection.List<CompanyExposureRow>(q => q.SelectTableFields()),
            connection.List<EvidenceRow>(q => q.SelectTableFields()),
            connection.List<SourceDocumentRow>(q => q.SelectTableFields()),
            connection.List<CompanyExposureEvidenceRow>(q => q.SelectTableFields()),
            connection.List<ResearchConclusionRow>(q => q.SelectTableFields()),
            connection.List<ConclusionEvidenceRow>(q => q.SelectTableFields()));
    }

    private sealed class LoadedWorkspaceData(
        List<PhysicalModuleRow> modules,
        List<PhysicalPartRow> parts,
        List<TechnologyLinkRow> technologies,
        List<PhysicalPartTechnologyLinkRow> partTechnologyLinks,
        List<IndustryChainNodeRow> nodes,
        List<PhysicalPartIndustryChainNodeRow> partChainLinks,
        List<CompanyRow> companies,
        List<CompanyExposureRow> exposures,
        List<EvidenceRow> evidence,
        List<SourceDocumentRow> sources,
        List<CompanyExposureEvidenceRow> exposureEvidence,
        List<ResearchConclusionRow> conclusions,
        List<ConclusionEvidenceRow> conclusionEvidence)
    {
        public List<PhysicalModuleRow> Modules { get; } = modules;
        public List<PhysicalPartRow> Parts { get; } = parts;
        public List<TechnologyLinkRow> Technologies { get; } = technologies;
        public List<PhysicalPartTechnologyLinkRow> PartTechnologyLinks { get; } = partTechnologyLinks;
        public List<IndustryChainNodeRow> Nodes { get; } = nodes;
        public List<PhysicalPartIndustryChainNodeRow> PartChainLinks { get; } = partChainLinks;
        public List<CompanyRow> Companies { get; } = companies;
        public List<CompanyExposureRow> Exposures { get; } = exposures;
        public List<EvidenceRow> Evidence { get; } = evidence;
        public List<CompanyExposureEvidenceRow> ExposureEvidence { get; } = exposureEvidence;
        public List<ResearchConclusionRow> Conclusions { get; } = conclusions;
        public List<ConclusionEvidenceRow> ConclusionEvidence { get; } = conclusionEvidence;
        public Dictionary<int, PhysicalModuleRow> ModulesById { get; } = modules.ToDictionary(x => x.PhysicalModuleId!.Value);
        public Dictionary<string, PhysicalModuleRow> ModulesByStableId { get; } = modules.ToDictionary(x => x.StableId, StringComparer.Ordinal);
        public Dictionary<int, PhysicalPartRow> PartsById { get; } = parts.ToDictionary(x => x.PhysicalPartId!.Value);
        public Dictionary<string, PhysicalPartRow> PartsByStableId { get; } = parts.ToDictionary(x => x.StableId, StringComparer.Ordinal);
        public Dictionary<int, TechnologyLinkRow> TechnologiesById { get; } = technologies.ToDictionary(x => x.TechnologyLinkId!.Value);
        public Dictionary<int, IndustryChainNodeRow> NodesById { get; } = nodes.ToDictionary(x => x.IndustryChainNodeId!.Value);
        public Dictionary<string, IndustryChainNodeRow> NodesByStableId { get; } = nodes.ToDictionary(x => x.StableId, StringComparer.Ordinal);
        public Dictionary<int, CompanyRow> CompaniesById { get; } = companies.ToDictionary(x => x.CompanyId!.Value);
        public Dictionary<string, CompanyRow> CompaniesByStableId { get; } = companies.ToDictionary(x => x.StableId, StringComparer.Ordinal);
        public Dictionary<int, SourceDocumentRow> SourcesById { get; } = sources.ToDictionary(x => x.SourceDocumentId!.Value);
    }
}
