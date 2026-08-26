import { notifyError, notifySuccess, resolveUrl } from "@serenity-is/corelib";
import { Column, FrozenLayout, SleekGrid } from "@serenity-is/sleekgrid";
import { hasPermission, userDefinition } from "../../Administration/User/Authentication/Authorization";
import { CompanyExposureService } from "../../ServerTypes/Research/CompanyExposureService";
import { CompanyUniverseService } from "../../ServerTypes/Research/CompanyUniverseService";
import type { ChainNodeResearchResponse } from "../../ServerTypes/Research/Services.ChainNodeResearchResponse";
import type { CompanyEvidenceSummary } from "../../ServerTypes/Research/Services.CompanyEvidenceSummary";
import type { CompanyExposureDetail } from "../../ServerTypes/Research/Services.CompanyExposureDetail";
import type { CompanyFilterOptions } from "../../ServerTypes/Research/Services.CompanyFilterOptions";
import type { CompanyResearchResponse } from "../../ServerTypes/Research/Services.CompanyResearchResponse";
import type { CompanyUniverseItem } from "../../ServerTypes/Research/Services.CompanyUniverseItem";
import type { CompanyUniverseRequest } from "../../ServerTypes/Research/Services.CompanyUniverseRequest";
import type { ResearchNamedLink } from "../../ServerTypes/Research/Services.ResearchNamedLink";
import "./CompanyUniversePage.css";
import {
    CompanyTab,
    compareText,
    companyTabLabels,
    companyTabs,
    meaningfulStateLabel,
    nextTab,
    normalizeCompanyFilters,
    toggleComparison
} from "./CompanyUniverseState";

interface PageOptions {
    mode?: "universe" | "detail" | "chain";
    companyId?: string;
    chainNodeId?: string;
}

export default async function pageInit(options?: PageOptions) {
    const app = document.querySelector<HTMLElement>("#company-research-app");
    const mode = options?.mode ?? app?.dataset.mode;
    if (mode === "detail") {
        await initCompanyDetail(options?.companyId ?? app?.dataset.companyId);
        return;
    }
    if (mode === "chain") {
        await initChainNode(options?.chainNodeId ?? app?.dataset.chainNodeId);
        return;
    }
    await initUniverse();
}

async function initUniverse() {
    const form = document.querySelector<HTMLFormElement>("#company-filters");
    const gridHost = document.querySelector<HTMLElement>("#company-grid");
    const gridError = document.querySelector<HTMLElement>("#company-grid-error");
    const tableBody = document.querySelector<HTMLTableSectionElement>("#company-table-body");
    const count = document.querySelector<HTMLElement>("#company-result-count");
    const status = document.querySelector<HTMLElement>("#company-grid-status");
    const comparison = document.querySelector<HTMLElement>("#company-comparison-content");
    const comparisonStatus = document.querySelector<HTMLElement>("#company-comparison-status");
    const clearComparison = document.querySelector<HTMLButtonElement>("#company-clear-comparison");
    const clearFilters = document.querySelector<HTMLButtonElement>("#company-clear-filters");
    if (!form || !gridHost || !gridError || !tableBody || !status || !comparison || !comparisonStatus || !clearComparison || !clearFilters)
        return;

    let companies: CompanyUniverseItem[] = [];
    let selected: string[] = [];
    let grid: SleekGrid<CompanyUniverseItem> | undefined;
    let filterOptionsLoaded = false;
    let requestGeneration = 0;
    let searchTimer: ReturnType<typeof setTimeout> | undefined;
    const forceTable = new URLSearchParams(location.search).get("view") === "table";

    const updateComparison = () => {
        comparison.replaceChildren();
        clearComparison.disabled = selected.length === 0;
        comparisonStatus.textContent = selected.length === 0
            ? "尚未选择公司。可在 SleekGrid 或 fallback 表格中用复选框选择。"
            : `已选择 ${selected.length}/5 家公司；比较不包含股价、涨跌幅或市场表现排名。`;
        if (selected.length) {
            const selectedCompanies = selected.map(id => companies.find(x => x.CompanyId === id)).filter(Boolean) as CompanyUniverseItem[];
            const table = document.createElement("table");
            table.className = "table table-sm company-comparison-table";
            const head = document.createElement("thead");
            head.innerHTML = "<tr><th>公司</th><th>层级 / 优先级</th><th>角色</th><th>核验状态</th><th>证据覆盖</th><th>新鲜度</th><th>详情</th></tr>";
            const body = document.createElement("tbody");
            for (const company of selectedCompanies) {
                const row = document.createElement("tr");
                row.append(td(company.Name), td(`${company.UniverseLayer} / ${company.CoveragePriority}`),
                    td(joinOrGap(company.Roles)), stateCell(company.VerificationStates),
                    td(`${meaningfulStateLabel(company.EvidenceCoverage)} (${company.ReviewedEvidenceCount}/${company.EvidenceCount})`),
                    td(meaningfulStateLabel(company.Freshness)), linkCell(companyUrl(company.CompanyId), "打开详情"));
                body.append(row);
            }
            table.append(head, body);
            const wrap = el("div", undefined, "table-responsive");
            wrap.append(table);
            comparison.append(wrap);
        }
        syncCheckboxes(selected);
        grid?.invalidate();
    };

    const toggle = (companyId: string, checked: boolean) => {
        const before = selected;
        selected = checked ? toggleComparison(selected, companyId) : selected.filter(id => id !== companyId);
        if (checked && before.length === selected.length && !selected.includes(companyId))
            notifyError("一次最多比较 5 家公司");
        updateComparison();
    };

    const renderFallback = () => {
        tableBody.replaceChildren();
        if (!companies.length) {
            const row = document.createElement("tr");
            const cell = td("没有公司符合当前筛选；该空缺不表示研究对象不存在。");
            cell.colSpan = 9;
            cell.className = "company-gap";
            row.append(cell);
            tableBody.append(row);
            return;
        }
        for (const company of companies) {
            const row = document.createElement("tr");
            row.dataset.companyId = company.CompanyId;
            const selectCell = document.createElement("td");
            selectCell.append(comparisonCheckbox(company, selected.includes(company.CompanyId), toggle, "fallback"));
            const identity = document.createElement("td");
            const link = document.createElement("a");
            link.href = companyUrl(company.CompanyId);
            link.textContent = company.Name ?? company.CompanyId;
            link.dataset.companyId = company.CompanyId;
            identity.append(link, el("code", company.CompanyId, "company-stable-id"));
            row.append(selectCell, identity, td(company.Ticker), td(company.Exchange), td(company.CountryRegion),
                td(joinOrGap(company.Roles)), stateCell(company.VerificationStates),
                td(`${meaningfulStateLabel(company.EvidenceCoverage)} (${company.ReviewedEvidenceCount}/${company.EvidenceCount})`),
                td(meaningfulStateLabel(company.Freshness)));
            tableBody.append(row);
        }
    };

    const renderGrid = () => {
        grid?.destroy();
        grid = undefined;
        gridHost.replaceChildren();
        if (forceTable) {
            gridHost.hidden = true;
            gridError.hidden = false;
            gridError.textContent = "当前使用显式原生表格 fallback 模式；所有公司仍可通过键盘访问。";
            status.textContent = "表格 fallback 模式";
            return;
        }
        try {
            gridHost.hidden = false;
            gridError.hidden = true;
            const columns: Column<CompanyUniverseItem>[] = [
                { id: "compare", name: "比较", width: 58, minWidth: 58, frozen: true, sortable: false,
                    format: ctx => comparisonCheckbox(ctx.item!, selected.includes(ctx.item!.CompanyId!), toggle, "grid") },
                { id: "Name", field: "Name", name: "公司", width: 220, minWidth: 170, frozen: true, sortable: true,
                    format: ctx => companyLink(ctx.item!) },
                { id: "Ticker", field: "Ticker", name: "Ticker", width: 88, frozen: true, sortable: true },
                { id: "Exchange", field: "Exchange", name: "市场", width: 92, sortable: true },
                { id: "CountryRegion", field: "CountryRegion", name: "地区", width: 85, sortable: true },
                { id: "UniverseLayer", field: "UniverseLayer", name: "公司池层级", width: 125, sortable: true },
                { id: "CoveragePriority", field: "CoveragePriority", name: "覆盖优先级", width: 105, sortable: true },
                { id: "Roles", name: "角色", width: 145, sortable: true, format: ctx => joinOrGap(ctx.item?.Roles) },
                { id: "VerificationStates", name: "核验状态", width: 180, sortable: true,
                    format: ctx => meaningfulStateLabel(ctx.item?.VerificationStates?.[0]) },
                { id: "EvidenceCoverage", field: "EvidenceCoverage", name: "证据覆盖", width: 150, sortable: true,
                    format: ctx => `${meaningfulStateLabel(ctx.item?.EvidenceCoverage)} (${ctx.item?.ReviewedEvidenceCount}/${ctx.item?.EvidenceCount})` },
                { id: "Freshness", field: "Freshness", name: "新鲜度", width: 145, sortable: true,
                    format: ctx => meaningfulStateLabel(ctx.item?.Freshness) },
                { id: "CoverageNote", field: "CoverageNote", name: "范围 / 研究缺口", width: 340, sortable: false }
            ];
            grid = new SleekGrid(gridHost, companies, columns, {
                enableCellNavigation: true,
                enableTabKeyNavigation: true,
                enableTextSelectionOnCells: true,
                frozenColumns: 3,
                layoutEngine: new FrozenLayout(),
                forceFitColumns: false,
                autoHeight: false,
                rowHeight: 42
            });
            grid.onSort.subscribe((_event, args) => {
                const columnId = args.sortCol.id ?? "Name";
                companies.sort((left, right) => compareCompanyField(left, right, columnId, args.sortAsc));
                grid?.setData(companies, true);
                grid?.invalidate();
                grid?.render();
                renderFallback();
            });
            status.textContent = `${companies.length} 行 · 前 3 列冻结 · 可排序`;
        }
        catch (error) {
            gridHost.hidden = true;
            gridError.hidden = false;
            gridError.textContent = `SleekGrid 无法初始化：${error instanceof Error ? error.message : "未知错误"}。请使用下方原生表格。`;
            status.textContent = "SleekGrid 初始化失败，fallback 可用";
        }
    };

    const load = async () => {
        const generation = ++requestGeneration;
        status.textContent = "正在筛选…";
        form.setAttribute("aria-busy", "true");
        try {
            const response = await CompanyUniverseService.List(readFilters(form));
            if (generation !== requestGeneration)
                return;
            companies = response.Companies ?? [];
            selected = selected.filter(id => companies.some(x => x.CompanyId === id));
            if (!filterOptionsLoaded) {
                populateFilters(form, response.Filters);
                filterOptionsLoaded = true;
            }
            if (count)
                count.textContent = `${companies.length} / ${response.TotalCount ?? 20} 家公司 · as of ${formatDate(response.AsOfUtc)}`;
            renderGrid();
            renderFallback();
            updateComparison();
        }
        catch (error) {
            if (generation !== requestGeneration)
                return;
            companies = [];
            renderFallback();
            gridHost.hidden = true;
            gridError.hidden = false;
            gridError.textContent = `公司池读取失败：${error instanceof Error ? error.message : "请检查服务与权限"}。`;
            status.textContent = "读取失败";
            notifyError("CompanyUniverseService 读取失败");
        }
        finally {
            if (generation === requestGeneration)
                form.removeAttribute("aria-busy");
        }
    };

    form.addEventListener("change", () => void load());
    form.querySelector<HTMLInputElement>('input[name="SearchText"]')?.addEventListener("input", () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => void load(), 180);
    });
    clearFilters.addEventListener("click", () => {
        form.reset();
        void load();
        form.querySelector<HTMLInputElement>('input[name="SearchText"]')?.focus();
    });
    clearComparison.addEventListener("click", () => {
        selected = [];
        updateComparison();
    });
    await load();
}

async function initCompanyDetail(companyId?: string) {
    const target = document.querySelector<HTMLElement>("#company-detail-content");
    if (!target || !companyId)
        return;
    try {
        const response = await CompanyUniverseService.Retrieve({ CompanyId: companyId });
        renderCompanyDetail(target, response);
        document.title = `${response.Company?.Name ?? companyId} - 公司研究详情`;
    }
    catch (error) {
        renderPageError(target, `无法读取公司 ${companyId}`, error);
    }
    finally {
        target.removeAttribute("aria-busy");
    }
}

async function initChainNode(chainNodeId?: string) {
    const target = document.querySelector<HTMLElement>("#company-detail-content");
    if (!target || !chainNodeId)
        return;
    try {
        const response = await CompanyUniverseService.RetrieveChainNode({ ChainNodeId: chainNodeId });
        renderChainNode(target, response);
    }
    catch (error) {
        renderPageError(target, `无法读取产业链节点 ${chainNodeId}`, error);
    }
    finally {
        target.removeAttribute("aria-busy");
    }
}

function renderCompanyDetail(target: HTMLElement, response: CompanyResearchResponse) {
    target.replaceChildren();
    const company = response.Company!;
    const header = el("header", undefined, "company-detail-header");
    header.append(el("code", company.CompanyId, "company-stable-id"), el("h2", company.Name),
        el("p", `${company.EnglishName || "英文名未记录"} · ${company.Ticker || "ticker 未记录"} · ${company.Exchange || "市场未记录"} · ${company.CountryRegion}`));
    const badges = el("div", undefined, "company-badges");
    badges.append(badge(company.UniverseLayer), badge(company.CoveragePriority));
    for (const state of company.VerificationStates ?? [])
        badges.append(badge(meaningfulStateLabel(state), state));
    header.append(badges, el("p", company.CoverageNote, "company-scope-note"));
    target.append(header);

    const tabs = el("div", undefined, "company-tabs");
    tabs.setAttribute("role", "tablist");
    tabs.setAttribute("aria-label", "公司研究详情栏目");
    const panels = el("div", undefined, "company-tab-panels");
    const activate = (tab: CompanyTab, focus = false) => {
        tabs.querySelectorAll<HTMLButtonElement>("[role=tab]").forEach(button => {
            const active = button.dataset.tab === tab;
            button.setAttribute("aria-selected", String(active));
            button.tabIndex = active ? 0 : -1;
            if (active && focus)
                button.focus();
        });
        panels.querySelectorAll<HTMLElement>("[role=tabpanel]").forEach(panel => panel.hidden = panel.dataset.tab !== tab);
    };
    for (const tab of companyTabs) {
        const button = el("button", companyTabLabels[tab], "company-tab");
        button.type = "button";
        button.id = `company-tab-${tab}`;
        button.dataset.tab = tab;
        button.setAttribute("role", "tab");
        button.setAttribute("aria-controls", `company-panel-${tab}`);
        button.setAttribute("aria-selected", String(tab === "overview"));
        button.tabIndex = tab === "overview" ? 0 : -1;
        button.addEventListener("click", () => activate(tab));
        button.addEventListener("keydown", event => {
            const destination = nextTab(tab, event.key);
            if (destination === tab)
                return;
            event.preventDefault();
            activate(destination, true);
        });
        tabs.append(button);
        const panel = el("section", undefined, "company-tab-panel");
        panel.id = `company-panel-${tab}`;
        panel.dataset.tab = tab;
        panel.setAttribute("role", "tabpanel");
        panel.setAttribute("aria-labelledby", button.id);
        panel.tabIndex = 0;
        panel.hidden = tab !== "overview";
        renderTab(panel, tab, response);
        panels.append(panel);
    }
    target.append(tabs, panels);
}

function renderTab(panel: HTMLElement, tab: CompanyTab, response: CompanyResearchResponse) {
    const company = response.Company!;
    if (tab === "overview") {
        panel.append(sectionTitle("Overview / 公司身份与覆盖"));
        const dl = el("dl", undefined, "company-overview-grid");
        appendDefinition(dl, "Stable company ID", company.CompanyId);
        appendDefinition(dl, "证券 / 市场", `${company.Ticker || "未记录"} · ${company.Exchange || "未记录"}`);
        appendDefinition(dl, "地区", company.CountryRegion);
        appendDefinition(dl, "公司池层级", company.UniverseLayer);
        appendDefinition(dl, "覆盖优先级", company.CoveragePriority);
        appendDefinition(dl, "Evidence coverage", `${meaningfulStateLabel(company.EvidenceCoverage)} · reviewed ${company.ReviewedEvidenceCount}/${company.EvidenceCount}`);
        appendDefinition(dl, "Freshness", meaningfulStateLabel(company.Freshness));
        panel.append(dl);
        if (company.OfficialUrl) {
            const official = document.createElement("a");
            official.href = company.OfficialUrl;
            official.target = "_blank";
            official.rel = "noopener noreferrer";
            official.textContent = "打开官方研究入口 ↗";
            panel.append(official);
        }
        panel.append(gapsBlock(response.ResearchGaps ?? []));
        return;
    }
    if (tab === "exposure") {
        panel.append(sectionTitle("Industry-chain Exposure / 显式关系"));
        if (!company.Exposures?.length) {
            panel.append(gap("尚无 CompanyExposure 记录。不得由公司名称、产品分类或关键词推导 part / chain 关系。"));
            return;
        }
        for (const exposure of company.Exposures)
            panel.append(exposureCard(company.CompanyId!, exposure, response.LinkOptions));
        return;
    }
    if (tab === "financial") {
        panel.append(sectionTitle("Earnings & Financial Evidence"));
        renderEvidenceList(panel, response.EarningsFinancialEvidence, "当前没有经类型化关系确认的 earnings / financial evidence；不做关键词分类。 ");
        return;
    }
    if (tab === "capex") {
        panel.append(sectionTitle("Capex & Investment"));
        renderEvidenceList(panel, response.CapexInvestmentEvidence, "当前没有经类型化关系确认的 Capex / investment evidence；不推断投资、订单或收入。 ");
        return;
    }
    if (tab === "events") {
        panel.append(sectionTitle("Events"));
        if (!response.Events?.length)
            panel.append(gap("尚无与该 stable company ID 显式关联的事件记录。"));
        else
            response.Events.forEach(item => panel.append(record(`${item.EventId} · ${item.EventType}`, item.Title, `${formatDate(item.EventTime)} · ${item.Description || "无描述"}`)));
        return;
    }
    if (tab === "conclusions") {
        panel.append(sectionTitle("Research Conclusions"));
        if (!response.Conclusions?.length)
            panel.append(gap("尚无通过 evidence 关系解析到该公司的 research conclusion；P3 不创建或发布结论。"));
        else
            response.Conclusions.forEach(item => panel.append(record(`${item.ConclusionId}@v${item.Version}`, item.Statement, `${item.PublicationState} · ${item.Confidence}`)));
        return;
    }
    panel.append(sectionTitle("Sources & Audit"));
    renderEvidenceList(panel, response.SourcesAudit, "尚无显式关联的 source / evidence audit 记录。");
    const audit = el("div", undefined, "company-audit");
    audit.append(el("strong", "Company audit metadata"), el("p", `insert user ${company.InsertUserId ?? "—"} · ${formatDate(company.InsertDate)}; update user ${company.UpdateUserId ?? "—"} · ${formatDate(company.UpdateDate)}`));
    panel.append(audit);
}

function exposureCard(companyId: string, exposure: CompanyExposureDetail, options?: CompanyFilterOptions) {
    const card = el("article", undefined, "company-exposure-card");
    const heading = el("div", undefined, "company-record-heading");
    heading.append(el("h3", `${exposure.Role} · ${exposure.Relevance}`), badge(meaningfulStateLabel(exposure.VerificationState), exposure.VerificationState));
    card.append(heading, el("p", `Confidence: ${exposure.Confidence} · verified-policy evidence: ${exposure.MeetsVerifiedPolicy ? "满足" : "不满足"}`, "company-meta"));
    const links = el("div", undefined, "company-cross-links");
    if (exposure.Part)
        links.append(nativeLink(partUrl(exposure.Part.Id), `物理部件：${exposure.Part.Name}`));
    else
        links.append(gap("未关联物理部件"));
    if (exposure.ChainNode)
        links.append(nativeLink(chainUrl(exposure.ChainNode.Id), `产业链节点：${exposure.ChainNode.Name}`));
    else
        links.append(gap("未关联产业链节点"));
    card.append(links, el("p", exposure.ScopeNote || "范围说明缺失", "company-scope-note"));
    card.append(evidenceGroup("Supporting evidence", exposure.SupportingEvidence),
        evidenceGroup("Contradicting evidence", exposure.ContradictingEvidence),
        evidenceGroup("Context evidence", exposure.ContextEvidence));
    card.append(el("p", `Audit: insert user ${exposure.InsertUserId ?? "—"} · ${formatDate(exposure.InsertDate)}; update user ${exposure.UpdateUserId ?? "—"} · ${formatDate(exposure.UpdateDate)}`, "company-audit"));
    if (hasPermission("Research:Review") && userDefinition().ActorType === "human")
        card.append(exposureEditor(companyId, exposure, options));
    return card;
}

function exposureEditor(companyId: string, exposure: CompanyExposureDetail, options?: CompanyFilterOptions) {
    const details = document.createElement("details");
    details.className = "company-exposure-editor";
    const summary = document.createElement("summary");
    summary.textContent = "编辑暴露记录（Research:Review）";
    const form = document.createElement("form");
    form.className = "company-exposure-form";
    form.append(selectField("物理部件", "PartId", options?.Parts, exposure.Part?.Id, true),
        selectField("产业链节点", "ChainNodeId", options?.ChainNodes, exposure.ChainNode?.Id, true),
        stringSelectField("角色", "Role", ["demand_owner", "platform_vendor", "chip_vendor", "component_vendor", "module_vendor", "substrate_pcb", "thermal_structure", "test_equipment", "system_vendor"], exposure.Role),
        stringSelectField("相关性", "Relevance", ["direct", "adjacent", "industry_anchor", "context", "unknown"], exposure.Relevance),
        stringSelectField("置信度", "Confidence", ["low", "medium", "high"], exposure.Confidence),
        stringSelectField("核验状态", "VerificationState", ["discovery", "candidate", "verified", "rejected", "stale"], exposure.VerificationState));
    const noteLabel = el("label", "Scope note");
    const note = document.createElement("textarea");
    note.name = "ScopeNote";
    note.className = "form-control form-control-sm";
    note.maxLength = 2000;
    note.required = true;
    note.value = exposure.ScopeNote ?? "";
    noteLabel.append(note);
    const status = el("div", "候选/发现不得显示为已核验；verified 由服务端强制要求 reviewed Level A/B supporting evidence。", "company-editor-policy");
    status.setAttribute("role", "status");
    const submit = el("button", "保存并写入审计", "btn btn-primary btn-sm");
    submit.type = "submit";
    form.append(noteLabel, status, submit);
    form.addEventListener("submit", async event => {
        event.preventDefault();
        submit.disabled = true;
        status.textContent = "正在验证 exposure policy…";
        const data = new FormData(form);
        try {
            await CompanyExposureService.Update({
                ExposureId: exposure.ExposureId,
                CompanyId: companyId,
                PartId: String(data.get("PartId") ?? "") || null,
                ChainNodeId: String(data.get("ChainNodeId") ?? "") || null,
                Role: String(data.get("Role") ?? ""),
                Relevance: String(data.get("Relevance") ?? ""),
                Confidence: String(data.get("Confidence") ?? ""),
                VerificationState: String(data.get("VerificationState") ?? ""),
                ScopeNote: String(data.get("ScopeNote") ?? "")
            });
            notifySuccess("公司暴露记录已按权限与审计约定更新");
            await initCompanyDetail(companyId);
        }
        catch (error) {
            status.textContent = serviceErrorMessage(error, "服务端拒绝了本次状态或字段更新。");
            status.classList.add("is-error");
        }
        finally {
            submit.disabled = false;
        }
    });
    details.append(summary, form);
    return details;
}

function renderChainNode(target: HTMLElement, response: ChainNodeResearchResponse) {
    target.replaceChildren();
    const header = el("header", undefined, "company-detail-header");
    header.append(el("code", response.Node?.Id ?? "", "company-stable-id"), el("h2", response.Node?.Name ?? "产业链节点"),
        el("p", "该页面仅提供 P3 稳定 cross-navigation；关系来自数据库显式映射。"));
    target.append(header, sectionTitle(`相关物理部件 (${response.Parts?.length ?? 0})`));
    const parts = el("div", undefined, "company-cross-links");
    if (!response.Parts?.length)
        parts.append(gap("尚无显式 part mapping。"));
    else
        response.Parts.forEach(part => parts.append(nativeLink(partUrl(part.Id), part.Name)));
    target.append(parts, sectionTitle(`相关公司暴露 (${response.Companies?.length ?? 0})`));
    const companies = el("div", undefined, "company-record-list");
    if (!response.Companies?.length)
        companies.append(gap("尚无显式 CompanyExposure；不得由节点名推导公司关系。"));
    else {
        response.Companies.forEach(company => {
            const item = record(`${company.CompanyId} · ${company.Role}`, company.CompanyName,
                `${meaningfulStateLabel(company.VerificationState)} · confidence ${company.Confidence} · ${company.ScopeNote}`);
            item.append(nativeLink(companyUrl(company.CompanyId), "打开公司详情"));
            companies.append(item);
        });
    }
    target.append(companies, gapsBlock(response.ResearchGaps ?? []));
}

function renderEvidenceList(target: HTMLElement, items: CompanyEvidenceSummary[] | undefined, empty: string) {
    if (!items?.length) {
        target.append(gap(empty));
        return;
    }
    for (const item of items) {
        const article = record(`${item.EvidenceId}@v${item.Version} · Level ${item.SourceLevel}`,
            item.Proposition, `${meaningfulStateLabel(item.ReviewState)} · ${item.Stance} · capture ${formatDate(item.CaptureTime)} · ${meaningfulStateLabel(item.Freshness)}`);
        article.append(el("small", `${item.Publisher} · ${item.SourceTitle} · ${item.Locator}`));
        if (item.OriginalUrl) {
            const source = nativeLink(item.OriginalUrl, "原始来源 ↗");
            source.target = "_blank";
            source.rel = "noopener noreferrer";
            article.append(source);
        }
        target.append(article);
    }
}

function evidenceGroup(title: string, items?: CompanyEvidenceSummary[]) {
    const section = el("section", undefined, "company-evidence-group");
    section.append(el("h4", `${title} (${items?.length ?? 0})`));
    if (!items?.length)
        section.append(gap("无记录；空缺不表示反证或支持已完成。"));
    else
        items.forEach(item => section.append(record(`${item.EvidenceId}@v${item.Version} · Level ${item.SourceLevel}`, item.Proposition,
            `${meaningfulStateLabel(item.ReviewState)} · ${item.Stance}`)));
    return section;
}

function readFilters(form: HTMLFormElement): CompanyUniverseRequest {
    return normalizeCompanyFilters(new FormData(form).entries()) as CompanyUniverseRequest;
}

function populateFilters(form: HTMLFormElement, options?: CompanyFilterOptions) {
    setNamedLinkOptions(form, "PartId", options?.Parts);
    setNamedLinkOptions(form, "ChainNodeId", options?.ChainNodes);
    setStringOptions(form, "Role", options?.Roles);
    setStringOptions(form, "Exchange", options?.Exchanges);
    setStringOptions(form, "CountryRegion", options?.CountriesRegions);
    setStringOptions(form, "UniverseLayer", options?.UniverseLayers);
    setStringOptions(form, "CoveragePriority", options?.CoveragePriorities);
    setStringOptions(form, "VerificationState", options?.VerificationStates, meaningfulStateLabel);
    setStringOptions(form, "EvidenceCoverage", options?.EvidenceCoverageStates, meaningfulStateLabel);
    setStringOptions(form, "Freshness", options?.FreshnessStates, meaningfulStateLabel);
}

function setNamedLinkOptions(form: HTMLFormElement, name: string, items?: ResearchNamedLink[]) {
    const select = form.elements.namedItem(name) as HTMLSelectElement | null;
    if (!select)
        return;
    for (const item of items ?? [])
        select.append(option(item.Id, item.Name));
}

function setStringOptions(form: HTMLFormElement, name: string, items?: string[], label = (value: string) => value) {
    const select = form.elements.namedItem(name) as HTMLSelectElement | null;
    if (!select)
        return;
    for (const item of items ?? [])
        select.append(option(item, label(item)));
}

function comparisonCheckbox(company: CompanyUniverseItem, checked: boolean,
    onChange: (companyId: string, checked: boolean) => void, source: string) {
    const input = document.createElement("input");
    input.type = "checkbox";
    input.className = "form-check-input company-compare-check";
    input.checked = checked;
    input.dataset.companyId = company.CompanyId;
    input.dataset.source = source;
    input.setAttribute("aria-label", `比较 ${company.Name}`);
    input.addEventListener("change", () => onChange(company.CompanyId!, input.checked));
    return input;
}

function syncCheckboxes(selected: string[]) {
    document.querySelectorAll<HTMLInputElement>(".company-compare-check").forEach(input =>
        input.checked = selected.includes(input.dataset.companyId ?? ""));
}

function companyLink(company: CompanyUniverseItem) {
    const wrap = el("span", undefined, "company-grid-identity");
    wrap.append(nativeLink(companyUrl(company.CompanyId), company.Name), el("small", company.CompanyId));
    return wrap;
}

function compareCompanyField(left: CompanyUniverseItem, right: CompanyUniverseItem, field: string, ascending: boolean) {
    const value = (item: CompanyUniverseItem): string => {
        if (field === "Roles") return joinOrGap(item.Roles);
        if (field === "VerificationStates") return item.VerificationStates?.[0] ?? "";
        return String((item as unknown as Record<string, unknown>)[field] ?? "");
    };
    return compareText(value(left), value(right), ascending);
}

function selectField(label: string, name: string, items: ResearchNamedLink[] | undefined, selected?: string, optional = false) {
    const wrapper = el("label", label);
    const select = document.createElement("select");
    select.name = name;
    select.className = "form-select form-select-sm";
    if (optional)
        select.append(option("", "未关联"));
    for (const item of items ?? [])
        select.append(option(item.Id, item.Name, item.Id === selected));
    wrapper.append(select);
    return wrapper;
}

function stringSelectField(label: string, name: string, values: string[], selected?: string) {
    return selectField(label, name, values.map(value => ({ Id: value, Name: meaningfulStateLabel(value) })), selected);
}

function option(value?: string, text?: string, selected = false) {
    const item = document.createElement("option");
    item.value = value ?? "";
    item.textContent = text ?? value ?? "";
    item.selected = selected;
    return item;
}

function appendDefinition(list: HTMLElement, term: string, value?: string) {
    list.append(el("dt", term), el("dd", value || "—"));
}

function sectionTitle(text: string) {
    return el("h2", text, "company-section-title");
}

function stateCell(states?: string[]) {
    const cell = document.createElement("td");
    const list = el("div", undefined, "company-state-list");
    for (const state of states ?? ["unknown"])
        list.append(badge(meaningfulStateLabel(state), state));
    cell.append(list);
    return cell;
}

function badge(text?: string, state?: string) {
    return el("span", text || "Unknown / 未记录", `company-badge state-${state || "unknown"}`);
}

function gap(text: string) {
    return el("p", text, "company-gap");
}

function gapsBlock(gaps: string[]) {
    const section = el("section", undefined, "company-gaps");
    section.append(el("h3", "显式研究缺口"));
    const list = document.createElement("ul");
    if (!gaps.length)
        list.append(el("li", "当前服务未返回额外缺口。"));
    else
        gaps.forEach(item => list.append(el("li", item)));
    section.append(list);
    return section;
}

function record(kicker?: string, title?: string, meta?: string) {
    const article = el("article", undefined, "company-record");
    article.append(el("code", kicker || "", "company-record-kicker"), el("h3", title || "未命名记录"), el("p", meta || "", "company-meta"));
    return article;
}

function linkCell(href: string, text: string) {
    const cell = document.createElement("td");
    cell.append(nativeLink(href, text));
    return cell;
}

function nativeLink(href: string, text?: string) {
    const link = document.createElement("a");
    link.href = href;
    link.textContent = text || href;
    return link;
}

function td(text?: string) {
    return el("td", text || "—");
}

function joinOrGap(values?: string[]) {
    return values?.length ? values.join(", ") : "研究缺口";
}

function companyUrl(companyId?: string) {
    return resolveUrl(`~/Research/Companies/${encodeURIComponent(companyId ?? "")}`);
}

function partUrl(partId?: string) {
    return resolveUrl(`~/Research/Parts/${encodeURIComponent(partId ?? "")}`);
}

function chainUrl(nodeId?: string) {
    return resolveUrl(`~/Research/ChainNodes/${encodeURIComponent(nodeId ?? "")}`);
}

function formatDate(value?: string | Date) {
    if (!value)
        return "未记录";
    const date = value instanceof Date ? value : new Date(value);
    return Number.isNaN(date.getTime()) ? String(value) : date.toISOString().slice(0, 10);
}

function renderPageError(target: HTMLElement, title: string, error: unknown) {
    const alert = el("div", undefined, "alert alert-danger");
    alert.append(el("strong", title), document.createTextNode(`：${serviceErrorMessage(error, "请检查服务与权限。")}`));
    target.replaceChildren(alert);
}

function serviceErrorMessage(error: unknown, fallback: string) {
    if (error instanceof Error && error.message)
        return error.message;
    const response = error as { Error?: { Message?: string; Code?: string }; error?: { message?: string; code?: string } } | null;
    return response?.Error?.Message ?? response?.error?.message ?? response?.Error?.Code ?? response?.error?.code ?? fallback;
}

function el<K extends keyof HTMLElementTagNameMap>(tag: K, text?: string, className?: string): HTMLElementTagNameMap[K] {
    const node = document.createElement(tag);
    if (text !== undefined)
        node.textContent = text;
    if (className)
        node.className = className;
    return node;
}
