using System.Data;
using SerenityQuantResearch.Research.Entities;

namespace SerenityQuantResearch.Research.Services;

public sealed class PartResearchRequest : ServiceRequest
{
    public string PartId { get; set; }
}

public sealed class PartResearchResponse : ServiceResponse
{
    public ResearchPartSummary Part { get; set; }
    public List<ResearchNamedLink> ChainNodes { get; set; } = [];
    public List<ResearchNamedLink> Technologies { get; set; } = [];
    public List<ResearchSectionSummary> Boundaries { get; set; } = [];
    public List<ResearchSectionSummary> UpstreamDownstream { get; set; } = [];
    public List<ResearchSectionSummary> KeySpecifications { get; set; } = [];
    public List<CompanyExposureSummary> Companies { get; set; } = [];
    public List<EvidenceSummary> Evidence { get; set; } = [];
    public List<ResearchSectionSummary> Conclusions { get; set; } = [];
    public List<ResearchSectionSummary> Risks { get; set; } = [];
    public List<string> StatusWarnings { get; set; } = [];
    public List<string> UnresolvedQuestions { get; set; } = [];
}

public sealed class PartCatalogResponse : ServiceResponse
{
    public List<ResearchModuleSummary> Modules { get; set; } = [];
}

public sealed record ResearchModuleSummary(string Id, string Name, int SortOrder, List<ResearchPartSummary> Parts);
public sealed record ResearchPartSummary(string Id, string Name, string FunctionSummary, string ResearchStatus,
    string ModuleId, string ModuleName, int ModuleSortOrder, int PartSortOrder);
public sealed record ResearchNamedLink(string Id, string Name);
public sealed record ResearchSectionSummary(string State, string Text);
public sealed record CompanyExposureSummary(string CompanyId, string CompanyName, string Role, string Relevance, string Confidence, string VerificationState, string ScopeNote);
public sealed record EvidenceSummary(string EvidenceId, int Version, string Proposition, string Stance, string ReviewState, string SourceLevel, string SourceTitle, string Locator);

public interface IPartResearchService
{
    PartCatalogResponse ListParts(IDbConnection connection);
    PartResearchResponse RetrieveCompleteChain(IDbConnection connection, string partId);
}

public sealed class PartResearchService : IPartResearchService
{
    public PartCatalogResponse ListParts(IDbConnection connection)
    {
        ArgumentNullException.ThrowIfNull(connection);

        var modules = connection.List<PhysicalModuleRow>(q => q.SelectTableFields()
            .OrderBy(PhysicalModuleRow.Fields.SortOrder));
        var parts = connection.List<PhysicalPartRow>(q => q.SelectTableFields()
            .OrderBy(PhysicalPartRow.Fields.PhysicalModuleId)
            .OrderBy(PhysicalPartRow.Fields.SortOrder));

        return new PartCatalogResponse
        {
            Modules = modules.Select(module => new ResearchModuleSummary(module.StableId, module.Name,
                module.SortOrder.Value, parts
                    .Where(part => part.PhysicalModuleId == module.PhysicalModuleId)
                    .OrderBy(part => part.SortOrder)
                    .Select(part => ToSummary(part, module))
                    .ToList()))
                .ToList()
        };
    }

    public PartResearchResponse RetrieveCompleteChain(IDbConnection connection, string partId)
    {
        ArgumentNullException.ThrowIfNull(connection);
        ArgumentException.ThrowIfNullOrWhiteSpace(partId);

        var partFields = PhysicalPartRow.Fields;
        var part = connection.TryFirst<PhysicalPartRow>(q => q.SelectTableFields().Where(partFields.StableId == partId)) ??
            throw new ValidationError("PartNotFound", $"Physical part '{partId}' was not found.");
        var module = connection.ById<PhysicalModuleRow>(part.PhysicalModuleId.Value);

        var response = new PartResearchResponse
        {
            Part = ToSummary(part, module)
        };

        var chainLinkFields = PhysicalPartIndustryChainNodeRow.Fields;
        foreach (var link in connection.List<PhysicalPartIndustryChainNodeRow>(q => q.SelectTableFields()
            .Where(chainLinkFields.PhysicalPartId == part.PhysicalPartId.Value)))
        {
            var node = connection.ById<IndustryChainNodeRow>(link.IndustryChainNodeId.Value);
            response.ChainNodes.Add(new ResearchNamedLink(node.StableId, node.Name));
        }

        var technologyLinkFields = PhysicalPartTechnologyLinkRow.Fields;
        foreach (var link in connection.List<PhysicalPartTechnologyLinkRow>(q => q.SelectTableFields()
            .Where(technologyLinkFields.PhysicalPartId == part.PhysicalPartId.Value)))
        {
            var technology = connection.ById<TechnologyLinkRow>(link.TechnologyLinkId.Value);
            response.Technologies.Add(new ResearchNamedLink(technology.StableId, technology.Name));
        }

        var exposureFields = CompanyExposureRow.Fields;
        foreach (var exposure in connection.List<CompanyExposureRow>(q => q.SelectTableFields()
            .Where(exposureFields.PhysicalPartId == part.PhysicalPartId.Value)))
        {
            var company = connection.ById<CompanyRow>(exposure.CompanyId.Value);
            response.Companies.Add(new CompanyExposureSummary(company.StableId, company.Name,
                exposure.Role, exposure.Relevance, exposure.Confidence,
                exposure.VerificationState, exposure.ScopeNote));
        }

        var evidenceFields = EvidenceRow.Fields;
        foreach (var evidence in connection.List<EvidenceRow>(q => q.SelectTableFields()
            .Where(evidenceFields.PhysicalPartId == part.PhysicalPartId.Value)))
        {
            var source = connection.ById<SourceDocumentRow>(evidence.SourceDocumentId.Value);
            response.Evidence.Add(new EvidenceSummary(evidence.StableId, evidence.Version.Value,
                evidence.Proposition, evidence.Stance, evidence.ReviewState,
                source.SourceLevel, source.Title, evidence.Locator));
        }

        AddResearchGaps(response);
        return response;
    }

    private static ResearchPartSummary ToSummary(PhysicalPartRow part, PhysicalModuleRow module) =>
        new(part.StableId, part.Name, part.FunctionSummary, part.ResearchStatus,
            module.StableId, module.Name, module.SortOrder.Value, part.SortOrder.Value);

    private static void AddResearchGaps(PartResearchResponse response)
    {
        response.Boundaries.Add(new ResearchSectionSummary("baseline",
            $"物理 taxonomy 边界：{response.Part.Name} 归入 {response.Part.ModuleName}；具体产品中的独立性、集成位置和装配边界仍需产品级证据确认。"));
        response.UpstreamDownstream.Add(new ResearchSectionSummary("unresolved",
            response.ChainNodes.Count == 0
                ? "尚无产业链节点映射，不能判断上游/下游关系。"
                : "当前 seed 仅记录产业链节点关联，尚未审核方向性；不得把节点关联解释为确定的上游/下游或供应关系。"));
        response.KeySpecifications.Add(new ResearchSectionSummary("unresolved",
            "尚无与该部件直接关联且经审核的产品规格；速率、材料、功耗、尺寸与接口参数不得从参考图片或 taxonomy 推导。"));
        response.Conclusions.Add(new ResearchSectionSummary("none",
            "P2 baseline 尚无可解析到该部件的 published conclusion；不得将候选暴露、draft evidence 或页面空缺解释为研究结论。"));
        response.Risks.Add(new ResearchSectionSummary("warning",
            "taxonomy-to-product 映射风险：已核验类别不等于具体产品采用、供应关系、量产状态或投资结论。"));

        response.StatusWarnings.Add($"研究状态：{response.Part.ResearchStatus}；分类状态不代表具体产品事实已核验。");

        if (response.Companies.Count == 0)
            response.StatusWarnings.Add("尚无候选公司暴露映射；不得由部件类别推导供应关系。");
        if (response.Evidence.Count == 0)
            response.StatusWarnings.Add("尚无直接关联证据；页面内容仅为 taxonomy 研究基线。");
        else if (response.Evidence.Any(x => x.ReviewState != "reviewed"))
            response.StatusWarnings.Add("存在未审核证据；draft / in_review 记录不得作为已核验事实引用。");

        response.UnresolvedQuestions.Add(response.Part.ResearchStatus switch
        {
            "architecture_option" => "具体产品是否采用该架构选项，采用范围与替代路线是什么？",
            "product_candidate" => "该候选产品形态是否有产品级一手证据支持？",
            "product_boundary_pending" => "该功能在具体产品中是否作为独立物理部件存在？",
            "interface_option" => "具体接口制式、系统边界与可维护性如何核验？",
            "validated_system_category" => "系统级部件与 CPA 共封装边界如何在具体产品中划分？",
            _ => "具体产品的规格、集成边界、验证阶段与量产状态是什么？"
        });

        if (response.Companies.Count == 0)
            response.UnresolvedQuestions.Add("哪些公司与该部件存在可由 Level A/B 证据支持的映射？");
        if (response.Evidence.Count == 0)
            response.UnresolvedQuestions.Add("需要补充哪些一手来源、反证与时效信息？");
    }
}
