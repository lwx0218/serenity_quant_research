using System.Data;
using SerenityQuantResearch.Administration;
using SerenityQuantResearch.Research.Domain;
using SerenityQuantResearch.Research.Entities;

namespace SerenityQuantResearch.Research.Services;

public sealed class CompanyUniverseRequest : ServiceRequest
{
    public string SearchText { get; set; }
    public string PartId { get; set; }
    public string ChainNodeId { get; set; }
    public string Role { get; set; }
    public string Exchange { get; set; }
    public string CountryRegion { get; set; }
    public string UniverseLayer { get; set; }
    public string CoveragePriority { get; set; }
    public string VerificationState { get; set; }
    public string EvidenceCoverage { get; set; }
    public string Freshness { get; set; }
}

public sealed class CompanyResearchRequest : ServiceRequest
{
    public string CompanyId { get; set; }
}

public sealed class ChainNodeResearchRequest : ServiceRequest
{
    public string ChainNodeId { get; set; }
}

public sealed class CompanyExposureUpdateRequest : ServiceRequest
{
    public int? ExposureId { get; set; }
    public string CompanyId { get; set; }
    public string PartId { get; set; }
    public string ChainNodeId { get; set; }
    public string Role { get; set; }
    public string Relevance { get; set; }
    public string Confidence { get; set; }
    public string VerificationState { get; set; }
    public string ScopeNote { get; set; }
}

public sealed class CompanyUniverseResponse : ServiceResponse
{
    public List<CompanyUniverseItem> Companies { get; set; } = [];
    public CompanyFilterOptions Filters { get; set; } = new();
    public int TotalCount { get; set; }
    public DateTime AsOfUtc { get; set; }
}

public sealed class CompanyResearchResponse : ServiceResponse
{
    public CompanyUniverseItem Company { get; set; }
    public List<CompanyEventSummary> Events { get; set; } = [];
    public List<CompanyEvidenceSummary> EarningsFinancialEvidence { get; set; } = [];
    public List<CompanyEvidenceSummary> CapexInvestmentEvidence { get; set; } = [];
    public List<CompanyConclusionSummary> Conclusions { get; set; } = [];
    public List<CompanyEvidenceSummary> SourcesAudit { get; set; } = [];
    public CompanyFilterOptions LinkOptions { get; set; } = new();
    public List<string> ResearchGaps { get; set; } = [];
}

public sealed class ChainNodeResearchResponse : ServiceResponse
{
    public ResearchNamedLink Node { get; set; }
    public List<ResearchNamedLink> Parts { get; set; } = [];
    public List<CompanyExposureSummary> Companies { get; set; } = [];
    public List<string> ResearchGaps { get; set; } = [];
}

public sealed class CompanyFilterOptions
{
    public List<ResearchNamedLink> Parts { get; set; } = [];
    public List<ResearchNamedLink> ChainNodes { get; set; } = [];
    public List<string> Roles { get; set; } = [];
    public List<string> Exchanges { get; set; } = [];
    public List<string> CountriesRegions { get; set; } = [];
    public List<string> UniverseLayers { get; set; } = [];
    public List<string> CoveragePriorities { get; set; } = [];
    public List<string> VerificationStates { get; set; } = [];
    public List<string> EvidenceCoverageStates { get; set; } = ["none", "unreviewed", "reviewed", "mixed"];
    public List<string> FreshnessStates { get; set; } = ["unknown", "fresh", "review_due", "historical"]; 
}

public sealed class CompanyUniverseItem
{
    public string CompanyId { get; set; }
    public string Name { get; set; }
    public string EnglishName { get; set; }
    public string Ticker { get; set; }
    public string Exchange { get; set; }
    public string CountryRegion { get; set; }
    public string UniverseLayer { get; set; }
    public string CoveragePriority { get; set; }
    public string OfficialUrl { get; set; }
    public List<CompanyExposureDetail> Exposures { get; set; } = [];
    public List<string> Roles { get; set; } = [];
    public List<string> VerificationStates { get; set; } = [];
    public string EvidenceCoverage { get; set; }
    public int EvidenceCount { get; set; }
    public int ReviewedEvidenceCount { get; set; }
    public string Freshness { get; set; }
    public DateTime? LatestCaptureTime { get; set; }
    public string CoverageNote { get; set; }
    public DateTime? InsertDate { get; set; }
    public int? InsertUserId { get; set; }
    public DateTime? UpdateDate { get; set; }
    public int? UpdateUserId { get; set; }
}

public sealed class CompanyExposureDetail
{
    public int ExposureId { get; set; }
    public ResearchNamedLink Part { get; set; }
    public ResearchNamedLink ChainNode { get; set; }
    public string Role { get; set; }
    public string Relevance { get; set; }
    public string Confidence { get; set; }
    public string VerificationState { get; set; }
    public string ScopeNote { get; set; }
    public List<CompanyEvidenceSummary> SupportingEvidence { get; set; } = [];
    public List<CompanyEvidenceSummary> ContradictingEvidence { get; set; } = [];
    public List<CompanyEvidenceSummary> ContextEvidence { get; set; } = [];
    public bool MeetsVerifiedPolicy { get; set; }
    public DateTime? InsertDate { get; set; }
    public int? InsertUserId { get; set; }
    public DateTime? UpdateDate { get; set; }
    public int? UpdateUserId { get; set; }
}

public sealed class CompanyEvidenceSummary
{
    public int EvidenceRecordId { get; set; }
    public string EvidenceId { get; set; }
    public int Version { get; set; }
    public string Proposition { get; set; }
    public string Stance { get; set; }
    public string ReviewState { get; set; }
    public string SourceLevel { get; set; }
    public string SourceTitle { get; set; }
    public string Publisher { get; set; }
    public string OriginalUrl { get; set; }
    public string Locator { get; set; }
    public DateTime? PublicationTime { get; set; }
    public DateTime CaptureTime { get; set; }
    public string Freshness { get; set; }
    public DateTime? ReviewedAt { get; set; }
    public int? ReviewedBy { get; set; }
}

public sealed record CompanyEventSummary(string EventId, string EventType, string Title, DateTime EventTime, string Description);
public sealed record CompanyConclusionSummary(string ConclusionId, int Version, string Statement, string PublicationState, string Confidence);

public interface ICompanyUniverseService
{
    CompanyUniverseResponse List(IDbConnection connection, CompanyUniverseRequest request, DateTime? asOfUtc = null);
    CompanyResearchResponse Retrieve(IDbConnection connection, string companyId, DateTime? asOfUtc = null);
    ChainNodeResearchResponse RetrieveChainNode(IDbConnection connection, string chainNodeId);
    void UpdateExposure(IUnitOfWork uow, CompanyExposureUpdateRequest request, int actorUserId, bool actorIsHumanReviewer);
}

public sealed class CompanyUniverseService : ICompanyUniverseService
{
    public CompanyUniverseResponse List(IDbConnection connection, CompanyUniverseRequest request, DateTime? asOfUtc = null)
    {
        ArgumentNullException.ThrowIfNull(connection);
        ArgumentNullException.ThrowIfNull(request);
        var asOf = asOfUtc ?? DateTime.UtcNow;
        var data = LoadData(connection, asOf);
        var all = data.Companies.Select(company => BuildCompanyItem(company, data, asOf)).ToList();
        var filtered = all.Where(company => Matches(company, request)).OrderBy(x => x.Name, StringComparer.Ordinal).ToList();

        return new CompanyUniverseResponse
        {
            Companies = filtered,
            Filters = BuildFilterOptions(data),
            TotalCount = all.Count,
            AsOfUtc = asOf
        };
    }

    public CompanyResearchResponse Retrieve(IDbConnection connection, string companyId, DateTime? asOfUtc = null)
    {
        ArgumentNullException.ThrowIfNull(connection);
        ArgumentException.ThrowIfNullOrWhiteSpace(companyId);
        var asOf = asOfUtc ?? DateTime.UtcNow;
        var data = LoadData(connection, asOf);
        var company = data.Companies.SingleOrDefault(x => x.StableId == companyId) ??
            throw new ValidationError("CompanyNotFound", $"Company '{companyId}' was not found.");
        var item = BuildCompanyItem(company, data, asOf);
        var companyEvidenceIds = item.Exposures
            .SelectMany(x => x.SupportingEvidence.Concat(x.ContradictingEvidence).Concat(x.ContextEvidence))
            .Select(x => x.EvidenceRecordId)
            .Concat(data.Evidence.Where(x => x.CompanyId == company.CompanyId).Select(x => x.EvidenceId!.Value))
            .Distinct()
            .ToHashSet();
        var sourceAudit = data.Evidence.Where(x => companyEvidenceIds.Contains(x.EvidenceId!.Value))
            .Select(x => ToEvidenceSummary(x, data.SourcesById[x.SourceDocumentId!.Value], asOf))
            .OrderByDescending(x => x.CaptureTime)
            .ToList();
        var conclusionIds = data.ConclusionEvidence.Where(x => companyEvidenceIds.Contains(x.EvidenceId!.Value))
            .Select(x => x.ResearchConclusionId!.Value).ToHashSet();

        var response = new CompanyResearchResponse
        {
            Company = item,
            Events = data.Events.Where(x => x.CompanyId == company.CompanyId)
                .OrderByDescending(x => x.EventTime)
                .Select(x => new CompanyEventSummary(x.StableId, x.EventType, x.Title, x.EventTime!.Value, x.Description))
                .ToList(),
            Conclusions = data.Conclusions.Where(x => conclusionIds.Contains(x.ResearchConclusionId!.Value))
                .Select(x => new CompanyConclusionSummary(x.StableId, x.Version!.Value, x.Statement, x.PublicationState, x.Confidence))
                .ToList(),
            SourcesAudit = sourceAudit,
            LinkOptions = BuildFilterOptions(data)
        };

        response.ResearchGaps.Add("Earnings & Financial Evidence：当前 schema 没有已审核的财务证据类型关联；不得按命题关键词自动分类。");
        response.ResearchGaps.Add("Capex & Investment：当前 schema 没有已审核的 Capex/投资证据类型关联；不得从公司名称或产品类别推断。");
        if (item.Exposures.Count == 0)
            response.ResearchGaps.Add("Industry-chain Exposure：尚无显式 CompanyExposure 记录；空缺不表示不存在，也不得自动补全。");
        if (response.Events.Count == 0)
            response.ResearchGaps.Add("Events：尚无与该稳定 company ID 显式关联的事件记录。");
        if (response.Conclusions.Count == 0)
            response.ResearchGaps.Add("Research Conclusions：尚无经 evidence 关系解析到该公司的结论记录。");
        if (sourceAudit.Count == 0)
            response.ResearchGaps.Add("Sources & Audit：尚无显式关联证据；需要后续人工研究补齐。");
        return response;
    }

    public ChainNodeResearchResponse RetrieveChainNode(IDbConnection connection, string chainNodeId)
    {
        ArgumentNullException.ThrowIfNull(connection);
        ArgumentException.ThrowIfNullOrWhiteSpace(chainNodeId);
        var node = connection.TryFirst<IndustryChainNodeRow>(q => q.SelectTableFields()
            .Where(IndustryChainNodeRow.Fields.StableId == chainNodeId)) ??
            throw new ValidationError("ChainNodeNotFound", $"Industry-chain node '{chainNodeId}' was not found.");
        var parts = connection.List<PhysicalPartRow>(q => q.SelectTableFields());
        var partById = parts.ToDictionary(x => x.PhysicalPartId!.Value);
        var partLinks = connection.List<PhysicalPartIndustryChainNodeRow>(q => q.SelectTableFields()
            .Where(PhysicalPartIndustryChainNodeRow.Fields.IndustryChainNodeId == node.IndustryChainNodeId!.Value));
        var companies = connection.List<CompanyRow>(q => q.SelectTableFields()).ToDictionary(x => x.CompanyId!.Value);
        var exposures = connection.List<CompanyExposureRow>(q => q.SelectTableFields()
            .Where(CompanyExposureRow.Fields.IndustryChainNodeId == node.IndustryChainNodeId.Value));
        var response = new ChainNodeResearchResponse
        {
            Node = new ResearchNamedLink(node.StableId, node.Name),
            Parts = partLinks.Select(x => partById[x.PhysicalPartId!.Value])
                .OrderBy(x => x.Name)
                .Select(x => new ResearchNamedLink(x.StableId, x.Name)).ToList(),
            Companies = exposures.Select(x =>
            {
                var company = companies[x.CompanyId!.Value];
                return new CompanyExposureSummary(company.StableId, company.Name, x.Role, x.Relevance,
                    x.Confidence, x.VerificationState, x.ScopeNote);
            }).OrderBy(x => x.CompanyName).ToList()
        };
        if (response.Companies.Count == 0)
            response.ResearchGaps.Add("尚无公司通过显式 CompanyExposure 关联到该产业链节点；不得按名称或关键词推导。");
        return response;
    }

    public void UpdateExposure(IUnitOfWork uow, CompanyExposureUpdateRequest request, int actorUserId, bool actorIsHumanReviewer)
    {
        ArgumentNullException.ThrowIfNull(uow);
        ArgumentNullException.ThrowIfNull(request);
        if (request.ExposureId is null)
            throw new ValidationError("ExposureRequired", "ExposureId is required.");
        ArgumentException.ThrowIfNullOrWhiteSpace(request.CompanyId);

        var exposure = uow.Connection.ById<CompanyExposureRow>(request.ExposureId.Value) ??
            throw new ValidationError("ExposureNotFound", $"Company exposure '{request.ExposureId}' was not found.");
        var company = uow.Connection.ById<CompanyRow>(exposure.CompanyId!.Value);
        if (!string.Equals(company.StableId, request.CompanyId, StringComparison.Ordinal))
            throw new ValidationError("CompanyMismatch", "The exposure does not belong to the requested stable company ID.");

        var partId = ResolveOptionalPart(uow.Connection, request.PartId);
        var nodeId = ResolveOptionalNode(uow.Connection, request.ChainNodeId);
        if (partId is null && nodeId is null)
            throw new ValidationError("ExposureTargetRequired", "A physical part or industry-chain node is required.");

        CompanyExposurePolicy.ValidateFields(request.Role, request.Relevance, request.Confidence,
            request.VerificationState, request.ScopeNote);
        var policyEvidence = LoadExposureEvidence(uow.Connection, exposure.CompanyExposureId!.Value)
            .Select(x => new ExposurePolicyEvidence(x.Evidence.ReviewState, x.Source.SourceLevel,
                x.Evidence.Stance, x.ReviewedByHuman));
        CompanyExposurePolicy.EnsureUpdate(exposure.VerificationState, request.VerificationState,
            actorIsHumanReviewer, policyEvidence);

        uow.Connection.UpdateById(new CompanyExposureRow
        {
            CompanyExposureId = exposure.CompanyExposureId,
            PhysicalPartId = partId,
            IndustryChainNodeId = nodeId,
            Role = request.Role,
            Relevance = request.Relevance,
            Confidence = request.Confidence,
            VerificationState = request.VerificationState,
            ScopeNote = request.ScopeNote,
            UpdateDate = DateTime.UtcNow,
            UpdateUserId = actorUserId
        }, ExpectedRows.One);
    }

    private static int? ResolveOptionalPart(IDbConnection connection, string stableId)
    {
        if (string.IsNullOrWhiteSpace(stableId))
            return null;
        return connection.TryFirst<PhysicalPartRow>(q => q.Select(PhysicalPartRow.Fields.PhysicalPartId)
            .Where(PhysicalPartRow.Fields.StableId == stableId))?.PhysicalPartId ??
            throw new ValidationError("PartNotFound", $"Physical part '{stableId}' was not found.");
    }

    private static int? ResolveOptionalNode(IDbConnection connection, string stableId)
    {
        if (string.IsNullOrWhiteSpace(stableId))
            return null;
        return connection.TryFirst<IndustryChainNodeRow>(q => q.Select(IndustryChainNodeRow.Fields.IndustryChainNodeId)
            .Where(IndustryChainNodeRow.Fields.StableId == stableId))?.IndustryChainNodeId ??
            throw new ValidationError("ChainNodeNotFound", $"Industry-chain node '{stableId}' was not found.");
    }

    private static CompanyUniverseItem BuildCompanyItem(CompanyRow company, LoadedData data, DateTime asOf)
    {
        var exposures = data.Exposures.Where(x => x.CompanyId == company.CompanyId)
            .Select(x => BuildExposure(x, data, asOf)).ToList();
        var evidence = exposures.SelectMany(x => x.SupportingEvidence.Concat(x.ContradictingEvidence).Concat(x.ContextEvidence))
            .Concat(data.Evidence.Where(x => x.CompanyId == company.CompanyId)
                .Select(x => ToEvidenceSummary(x, data.SourcesById[x.SourceDocumentId!.Value], asOf)))
            .GroupBy(x => x.EvidenceRecordId).Select(x => x.First()).ToList();
        var reviewed = evidence.Count(x => x.ReviewState == EvidenceReviewStates.Reviewed);
        var coverage = evidence.Count == 0 ? "none" : reviewed == 0 ? "unreviewed" : reviewed == evidence.Count ? "reviewed" : "mixed";
        var latest = evidence.Count == 0 ? (DateTime?)null : evidence.Max(x => x.CaptureTime);
        var freshness = evidence.Count == 0 ? "unknown" : evidence.Select(x => x.Freshness).OrderBy(FreshnessSeverity).Last();

        return new CompanyUniverseItem
        {
            CompanyId = company.StableId,
            Name = company.Name,
            EnglishName = company.EnglishName,
            Ticker = company.Ticker,
            Exchange = company.Exchange,
            CountryRegion = company.CountryRegion,
            UniverseLayer = company.UniverseLayer,
            CoveragePriority = company.CoveragePriority,
            OfficialUrl = company.OfficialUrl,
            Exposures = exposures,
            Roles = exposures.Select(x => x.Role).Distinct(StringComparer.Ordinal).OrderBy(x => x).ToList(),
            VerificationStates = exposures.Count == 0 ? ["unmapped"] : exposures.Select(x => x.VerificationState)
                .Distinct(StringComparer.Ordinal).OrderBy(x => x).ToList(),
            EvidenceCoverage = coverage,
            EvidenceCount = evidence.Count,
            ReviewedEvidenceCount = reviewed,
            Freshness = freshness,
            LatestCaptureTime = latest,
            CoverageNote = exposures.Count == 0
                ? "研究缺口：尚无显式 CompanyExposure；不得由公司名称、产品类别或关键词推导。"
                : $"{exposures.Count} 条显式暴露；{reviewed}/{evidence.Count} 条证据已审核。候选/发现状态不构成已核验事实。",
            InsertDate = company.InsertDate,
            InsertUserId = company.InsertUserId,
            UpdateDate = company.UpdateDate,
            UpdateUserId = company.UpdateUserId
        };
    }

    private static CompanyExposureDetail BuildExposure(CompanyExposureRow exposure, LoadedData data, DateTime asOf)
    {
        var evidence = data.ExposureEvidence.Where(x => x.CompanyExposureId == exposure.CompanyExposureId)
            .Select(x => data.EvidenceById[x.EvidenceId!.Value])
            .Select(x => ToEvidenceSummary(x, data.SourcesById[x.SourceDocumentId!.Value], asOf)).ToList();
        var supporting = evidence.Where(x => x.Stance == "supports").ToList();
        var contradicting = evidence.Where(x => x.Stance == "contradicts").ToList();
        var context = evidence.Where(x => x.Stance != "supports" && x.Stance != "contradicts").ToList();
        return new CompanyExposureDetail
        {
            ExposureId = exposure.CompanyExposureId!.Value,
            Part = exposure.PhysicalPartId is int partId && data.PartsById.TryGetValue(partId, out var part)
                ? new ResearchNamedLink(part.StableId, part.Name) : null,
            ChainNode = exposure.IndustryChainNodeId is int nodeId && data.NodesById.TryGetValue(nodeId, out var node)
                ? new ResearchNamedLink(node.StableId, node.Name) : null,
            Role = exposure.Role,
            Relevance = exposure.Relevance,
            Confidence = exposure.Confidence,
            VerificationState = exposure.VerificationState,
            ScopeNote = exposure.ScopeNote,
            SupportingEvidence = supporting,
            ContradictingEvidence = contradicting,
            ContextEvidence = context,
            MeetsVerifiedPolicy = CompanyExposurePolicy.HasReviewedSupportingEvidence(evidence.Select(x =>
                new ExposurePolicyEvidence(x.ReviewState, x.SourceLevel, x.Stance,
                    x.ReviewedBy is int reviewerId && data.UsersById.TryGetValue(reviewerId, out var reviewer) &&
                    reviewer.ActorType == UserActorTypes.Human))),
            InsertDate = exposure.InsertDate,
            InsertUserId = exposure.InsertUserId,
            UpdateDate = exposure.UpdateDate,
            UpdateUserId = exposure.UpdateUserId
        };
    }

    private static CompanyEvidenceSummary ToEvidenceSummary(EvidenceRow evidence, SourceDocumentRow source, DateTime asOf) => new()
    {
        EvidenceRecordId = evidence.EvidenceId!.Value,
        EvidenceId = evidence.StableId,
        Version = evidence.Version!.Value,
        Proposition = evidence.Proposition,
        Stance = evidence.Stance,
        ReviewState = evidence.ReviewState,
        SourceLevel = source.SourceLevel,
        SourceTitle = source.Title,
        Publisher = source.Publisher,
        OriginalUrl = source.OriginalUrl,
        Locator = evidence.Locator,
        PublicationTime = source.PublicationTime,
        CaptureTime = source.CaptureTime!.Value,
        Freshness = CalculateFreshness(source.CaptureTime.Value, asOf, evidenceCategory: null),
        ReviewedAt = evidence.ReviewedAt,
        ReviewedBy = evidence.ReviewedBy
    };

    public static string CalculateFreshness(DateTime captureTime, DateTime asOfUtc, string evidenceCategory)
    {
        if (string.IsNullOrWhiteSpace(evidenceCategory))
            return "unknown";
        if (evidenceCategory == "historical_financial")
            return "historical";
        var thresholdDays = evidenceCategory switch
        {
            "news" or "event" or "product_roadmap" or "management_outlook" => 90,
            "product_page" or "presentation" or "industry_material" => 180,
            "standard" => 365,
            "annual_report" => 450,
            _ => (int?)null
        };
        if (thresholdDays is null)
            return "unknown";
        return asOfUtc - captureTime <= TimeSpan.FromDays(thresholdDays.Value) ? "fresh" : "review_due";
    }

    private static int FreshnessSeverity(string state) => state switch
    {
        "fresh" => 1,
        "historical" => 1,
        "review_due" => 2,
        _ => 0
    };

    private static bool Matches(CompanyUniverseItem company, CompanyUniverseRequest request)
    {
        bool EqualsFilter(string value, string filter) => string.IsNullOrWhiteSpace(filter) || string.Equals(value, filter, StringComparison.OrdinalIgnoreCase);
        if (!string.IsNullOrWhiteSpace(request.SearchText))
        {
            var search = request.SearchText.Trim();
            if (!(company.CompanyId.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                company.Name.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                (company.EnglishName?.Contains(search, StringComparison.OrdinalIgnoreCase) ?? false) ||
                (company.Ticker?.Contains(search, StringComparison.OrdinalIgnoreCase) ?? false)))
                return false;
        }
        return (string.IsNullOrWhiteSpace(request.PartId) || company.Exposures.Any(x => x.Part?.Id == request.PartId)) &&
            (string.IsNullOrWhiteSpace(request.ChainNodeId) || company.Exposures.Any(x => x.ChainNode?.Id == request.ChainNodeId)) &&
            (string.IsNullOrWhiteSpace(request.Role) || company.Roles.Contains(request.Role, StringComparer.Ordinal)) &&
            EqualsFilter(company.Exchange, request.Exchange) && EqualsFilter(company.CountryRegion, request.CountryRegion) &&
            EqualsFilter(company.UniverseLayer, request.UniverseLayer) && EqualsFilter(company.CoveragePriority, request.CoveragePriority) &&
            (string.IsNullOrWhiteSpace(request.VerificationState) || company.VerificationStates.Contains(request.VerificationState, StringComparer.Ordinal)) &&
            EqualsFilter(company.EvidenceCoverage, request.EvidenceCoverage) && EqualsFilter(company.Freshness, request.Freshness);
    }

    private static CompanyFilterOptions BuildFilterOptions(LoadedData data) => new()
    {
        Parts = data.Parts.OrderBy(x => x.Name).Select(x => new ResearchNamedLink(x.StableId, x.Name)).ToList(),
        ChainNodes = data.Nodes.OrderBy(x => x.SortOrder).Select(x => new ResearchNamedLink(x.StableId, x.Name)).ToList(),
        Roles = data.Exposures.Select(x => x.Role).Distinct(StringComparer.Ordinal).OrderBy(x => x).ToList(),
        Exchanges = data.Companies.Select(x => x.Exchange).Where(x => !string.IsNullOrWhiteSpace(x)).Distinct(StringComparer.Ordinal).OrderBy(x => x).ToList(),
        CountriesRegions = data.Companies.Select(x => x.CountryRegion).Distinct(StringComparer.Ordinal).OrderBy(x => x).ToList(),
        UniverseLayers = data.Companies.Select(x => x.UniverseLayer).Distinct(StringComparer.Ordinal).OrderBy(x => x).ToList(),
        CoveragePriorities = data.Companies.Select(x => x.CoveragePriority).Distinct(StringComparer.Ordinal).OrderBy(x => x).ToList(),
        VerificationStates = data.Exposures.Select(x => x.VerificationState).Append("unmapped").Distinct(StringComparer.Ordinal).OrderBy(x => x).ToList()
    };

    private static List<(EvidenceRow Evidence, SourceDocumentRow Source, bool ReviewedByHuman)> LoadExposureEvidence(IDbConnection connection, int exposureId)
    {
        var links = connection.List<CompanyExposureEvidenceRow>(q => q.SelectTableFields()
            .Where(CompanyExposureEvidenceRow.Fields.CompanyExposureId == exposureId));
        return links.Select(link =>
        {
            var evidence = connection.ById<EvidenceRow>(link.EvidenceId!.Value);
            var reviewer = evidence.ReviewedBy is int reviewerId ? connection.ById<UserRow>(reviewerId) : null;
            return (evidence, connection.ById<SourceDocumentRow>(evidence.SourceDocumentId!.Value),
                reviewer?.ActorType == UserActorTypes.Human);
        }).ToList();
    }

    private static LoadedData LoadData(IDbConnection connection, DateTime asOf) => new(
        connection.List<CompanyRow>(q => q.SelectTableFields()),
        connection.List<CompanyExposureRow>(q => q.SelectTableFields()),
        connection.List<PhysicalPartRow>(q => q.SelectTableFields()),
        connection.List<IndustryChainNodeRow>(q => q.SelectTableFields()),
        connection.List<EvidenceRow>(q => q.SelectTableFields()),
        connection.List<SourceDocumentRow>(q => q.SelectTableFields()),
        connection.List<CompanyExposureEvidenceRow>(q => q.SelectTableFields()),
        connection.List<EventRow>(q => q.SelectTableFields()),
        connection.List<ResearchConclusionRow>(q => q.SelectTableFields()),
        connection.List<ConclusionEvidenceRow>(q => q.SelectTableFields()),
        connection.List<UserRow>(q => q.SelectTableFields()));

    private sealed class LoadedData(
        List<CompanyRow> companies,
        List<CompanyExposureRow> exposures,
        List<PhysicalPartRow> parts,
        List<IndustryChainNodeRow> nodes,
        List<EvidenceRow> evidence,
        List<SourceDocumentRow> sources,
        List<CompanyExposureEvidenceRow> exposureEvidence,
        List<EventRow> events,
        List<ResearchConclusionRow> conclusions,
        List<ConclusionEvidenceRow> conclusionEvidence,
        List<UserRow> users)
    {
        public List<CompanyRow> Companies { get; } = companies;
        public List<CompanyExposureRow> Exposures { get; } = exposures;
        public List<PhysicalPartRow> Parts { get; } = parts;
        public List<IndustryChainNodeRow> Nodes { get; } = nodes;
        public List<EvidenceRow> Evidence { get; } = evidence;
        public List<CompanyExposureEvidenceRow> ExposureEvidence { get; } = exposureEvidence;
        public List<EventRow> Events { get; } = events;
        public List<ResearchConclusionRow> Conclusions { get; } = conclusions;
        public List<ConclusionEvidenceRow> ConclusionEvidence { get; } = conclusionEvidence;
        public Dictionary<int, PhysicalPartRow> PartsById { get; } = parts.ToDictionary(x => x.PhysicalPartId!.Value);
        public Dictionary<int, IndustryChainNodeRow> NodesById { get; } = nodes.ToDictionary(x => x.IndustryChainNodeId!.Value);
        public Dictionary<int, EvidenceRow> EvidenceById { get; } = evidence.ToDictionary(x => x.EvidenceId!.Value);
        public Dictionary<int, SourceDocumentRow> SourcesById { get; } = sources.ToDictionary(x => x.SourceDocumentId!.Value);
        public Dictionary<int, UserRow> UsersById { get; } = users.ToDictionary(x => x.UserId!.Value);
    }
}
