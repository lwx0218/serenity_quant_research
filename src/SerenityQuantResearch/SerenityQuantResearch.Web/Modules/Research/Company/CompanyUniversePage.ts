import { notifyError, resolveUrl } from "@serenity-is/corelib";
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
    compareText,
    defaultCompanyBrowseView,
    isCompanyBrowseView,
    meaningfulStateLabel,
    normalizeCompanyFilters,
    stateTrustTone
} from "./CompanyUniverseState";
import type { CompanyBrowseView } from "./CompanyUniverseState";

interface PageOptions {
    mode?: "universe" | "detail" | "chain";
    companyId?: string;
    chainNodeId?: string;
}

interface SourceContext {
    source?: string;
    componentId?: string;
    partId?: string;
    chainNodeId?: string;
    searchText?: string;
    role?: string;
    countryRegion?: string;
    verificationState?: string;
    view?: CompanyBrowseView;
}

const componentLabels: Record<string, string> = {
    "cpo.mod.thermal": "Thermal / 散热",
    "cpo.mod.host-asic": "Host ASIC",
    "cpo.mod.eic": "EIC",
    "cpo.mod.pic": "SiPh PIC",
    "cpo.mod.laser": "Laser",
    "cpo.mod.receiver": "Receiver / TIA",
    "cpo.mod.fiber-interface": "Fiber Interface",
    "cpo.mod.cpa-substrate": "CPA / Substrate",
    "cpo.mod.host-board": "Host Board / PCB"
};

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
    const app = document.querySelector<HTMLElement>("#company-research-app");
    const form = document.querySelector<HTMLFormElement>("#company-filters");
    const cardPanel = document.querySelector<HTMLElement>("#company-card-panel");
    const cardList = document.querySelector<HTMLElement>("#company-card-list");
    const listPanel = document.querySelector<HTMLElement>("#company-list-panel");
    const listBody = document.querySelector<HTMLElement>("#company-list-body");
    const count = document.querySelector<HTMLElement>("#company-result-count");
    const status = document.querySelector<HTMLElement>("#company-pool-status");
    const clearFilters = document.querySelector<HTMLButtonElement>("#company-clear-filters");
    const contextNodes = document.querySelectorAll<HTMLElement>("[data-company-source-context]");
    const viewButtons = document.querySelectorAll<HTMLButtonElement>("[data-company-view]");
    const drawer = document.querySelector<HTMLElement>("#company-quick-drawer");
    const drawerContent = document.querySelector<HTMLElement>("#company-quick-drawer-content");
    const drawerClose = document.querySelector<HTMLButtonElement>("#company-quick-drawer-close");
    if (!app || !form || !cardPanel || !cardList || !listPanel || !listBody || !status || !clearFilters || !drawer || !drawerContent || !drawerClose)
        return;

    let companies: CompanyUniverseItem[] = [];
    let activeView: CompanyBrowseView = defaultCompanyBrowseView;
    let filterOptionsLoaded = false;
    let requestGeneration = 0;
    let searchTimer: ReturnType<typeof setTimeout> | undefined;
    let drawerOpen = false;
    let returnFocus: HTMLElement | undefined;
    let pendingActivationScrollY: number | undefined;
    let useSourceFilterDefaults = true;
    const sourceContext = readSourceContext(location.search);
    if (sourceContext.view)
        activeView = sourceContext.view;

    const refreshContext = () => {
        const text = sourceContextLabel(sourceContext, form);
        for (const node of contextNodes)
            node.textContent = text;
        app.dataset.sourceContext = text;
    };

    const setView = (view: CompanyBrowseView) => {
        activeView = view;
        app.dataset.view = view;
        cardPanel.hidden = view !== "card";
        listPanel.hidden = view !== "list";
        for (const button of viewButtons) {
            const active = button.dataset.companyView === view;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-pressed", String(active));
        }
        status.textContent = view === "card"
            ? `${companies.length} 家公司 · Card View 默认浏览`
            : `${companies.length} 家公司 · List View 使用相同筛选与来源 context`;
    };

    const closeDrawer = () => {
        if (!drawerOpen)
            return;
        drawerOpen = false;
        drawer.classList.remove("is-open");
        drawer.setAttribute("aria-hidden", "true");
        drawer.hidden = true;
        app.classList.remove("has-company-drawer");
        app.dataset.drawerCompanyId = "";
        returnFocus?.focus({ preventScroll: true });
        returnFocus = undefined;
    };

    const restoreScroll = (scrollY: number) => {
        const restore = () => window.scrollTo({ top: scrollY });
        restore();
        requestAnimationFrame(restore);
        setTimeout(restore, 0);
        setTimeout(restore, 80);
        setTimeout(restore, 180);
    };

    const openDrawer = async (companyId: string, trigger?: HTMLElement, activationScrollY = window.scrollY) => {
        const scrollY = activationScrollY;
        drawerOpen = true;
        returnFocus = trigger;
        drawer.hidden = false;
        drawer.setAttribute("aria-hidden", "false");
        drawer.classList.add("is-open");
        app.classList.add("has-company-drawer");
        app.dataset.drawerCompanyId = companyId;
        drawerContent.replaceChildren(el("p", "正在读取 Quick Company Drawer…", "company-loading"));
        drawerClose.focus({ preventScroll: true });
        restoreScroll(scrollY);
        try {
            const response = await CompanyUniverseService.Retrieve({ CompanyId: companyId });
            if (app.dataset.drawerCompanyId === companyId) {
                renderQuickDrawer(drawerContent, response, sourceContext, form, activeView);
                restoreScroll(scrollY);
            }
        }
        catch (error) {
            renderPageError(drawerContent, `无法读取 ${companyId} 的 Quick Drawer`, error);
            restoreScroll(scrollY);
        }
    };

    const rememberActivationScroll = () => {
        pendingActivationScrollY = window.scrollY;
    };

    const activateCompany = (companyId: string, trigger: HTMLElement) => {
        const activationScrollY = pendingActivationScrollY ?? window.scrollY;
        pendingActivationScrollY = undefined;
        void openDrawer(companyId, trigger, activationScrollY);
    };

    const renderPool = () => {
        refreshContext();
        renderCards(cardList, companies, sourceContext, form, activateCompany, rememberActivationScroll);
        renderList(listBody, companies, sourceContext, form, activateCompany, rememberActivationScroll);
        setView(activeView);
    };

    const load = async () => {
        const generation = ++requestGeneration;
        closeDrawer();
        status.textContent = "正在筛选公司池…";
        form.setAttribute("aria-busy", "true");
        try {
            const response = await CompanyUniverseService.List(readFilters(form, useSourceFilterDefaults ? sourceContext : undefined));
            if (generation !== requestGeneration)
                return;
            companies = response.Companies ?? [];
            if (!filterOptionsLoaded) {
                populateFilters(form, response.Filters);
                applySourceDefaults(form, sourceContext);
                filterOptionsLoaded = true;
            }
            useSourceFilterDefaults = false;
            companies.sort((left, right) => compareText(left.Name, right.Name));
            if (count)
                count.textContent = `${companies.length} / ${response.TotalCount ?? companies.length} 家公司 · as of ${formatDate(response.AsOfUtc)}`;
            renderPool();
        }
        catch (error) {
            if (generation !== requestGeneration)
                return;
            companies = [];
            renderPool();
            status.textContent = "读取失败";
            notifyError("CompanyUniverseService 读取失败");
            const alert = el("div", undefined, "alert alert-warning");
            alert.append(el("strong", "公司池读取失败"), document.createTextNode(`：${serviceErrorMessage(error, "请检查服务与权限")}`));
            cardList.replaceChildren(alert);
        }
        finally {
            if (generation === requestGeneration)
                form.removeAttribute("aria-busy");
        }
    };

    form.addEventListener("change", () => {
        useSourceFilterDefaults = false;
        void load();
    });
    form.querySelector<HTMLInputElement>('input[name="SearchText"]')?.addEventListener("input", () => {
        useSourceFilterDefaults = false;
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => void load(), 180);
    });
    clearFilters.addEventListener("click", () => {
        form.reset();
        useSourceFilterDefaults = false;
        void load();
        form.querySelector<HTMLInputElement>('input[name="SearchText"]')?.focus();
    });
    for (const button of viewButtons) {
        const view = button.dataset.companyView;
        if (!isCompanyBrowseView(view))
            continue;
        button.addEventListener("click", () => setView(view));
    }
    drawerClose.addEventListener("click", closeDrawer);
    document.addEventListener("keydown", event => {
        if (event.key === "Escape")
            closeDrawer();
    });
    document.addEventListener("pointerdown", event => {
        const target = event.target as Node | null;
        if (!drawerOpen || !target || drawer.contains(target) || isCompanyActivationTarget(target))
            return;
        closeDrawer();
    });

    refreshContext();
    setView(activeView);
    await load();
}

function renderCards(target: HTMLElement, companies: CompanyUniverseItem[], context: SourceContext, form: HTMLFormElement,
    onOpen: (companyId: string, trigger: HTMLElement) => void, onActivationStart: () => void) {
    target.replaceChildren();
    if (!companies.length) {
        target.append(gap("没有公司符合当前轻量筛选；该空缺不表示研究对象不存在。"));
        return;
    }
    for (const company of companies) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "company-card";
        button.dataset.companyCard = "true";
        button.dataset.companyId = company.CompanyId;
        button.setAttribute("aria-label", `打开 ${company.Name ?? company.CompanyId} Quick Company Drawer`);
        button.addEventListener("pointerdown", event => {
            onActivationStart();
            event.preventDefault();
            event.stopPropagation();
        });
        button.addEventListener("click", event => {
            event.preventDefault();
            event.stopPropagation();
            onOpen(company.CompanyId!, button);
        });

        const heading = el("span", undefined, "company-card-heading");
        const identity = el("span", undefined, "company-card-identity");
        identity.append(el("strong", company.Name ?? company.CompanyId), el("code", company.CompanyId, "company-stable-id"));
        heading.append(identity, el("span", tickerMarket(company), "company-card-market"));
        button.append(heading);

        const badges = el("span", undefined, "company-badges");
        for (const state of company.VerificationStates?.length ? company.VerificationStates : ["unknown"])
            badges.append(badge(meaningfulStateLabel(state), state));
        for (const role of company.Roles?.slice(0, 3) ?? [])
            badges.append(badge(role));
        button.append(badges,
            el("span", evidenceCoverageText(company), "company-evidence-line"),
            el("span", whyCompanyAppears(company, context, form), "company-why"));
        target.append(button);
    }
}

function renderList(target: HTMLElement, companies: CompanyUniverseItem[], context: SourceContext, form: HTMLFormElement,
    onOpen: (companyId: string, trigger: HTMLElement) => void, onActivationStart: () => void) {
    target.replaceChildren();
    if (!companies.length) {
        target.append(gap("没有公司符合当前轻量筛选；List View 与 Card View 使用同一公司集合。"));
        return;
    }
    for (const company of companies) {
        const row = document.createElement("button");
        row.type = "button";
        row.className = "company-list-row";
        row.dataset.companyRow = "true";
        row.dataset.companyId = company.CompanyId;
        row.setAttribute("aria-label", `打开 ${company.Name ?? company.CompanyId} Quick Company Drawer`);
        row.addEventListener("pointerdown", event => {
            onActivationStart();
            event.preventDefault();
            event.stopPropagation();
        });
        row.addEventListener("click", event => {
            event.preventDefault();
            event.stopPropagation();
            onOpen(company.CompanyId!, row);
        });
        row.append(el("strong", company.Name ?? company.CompanyId), el("span", tickerMarket(company)),
            el("span", joinOrGap(company.Roles)), stateSummary(company.VerificationStates),
            el("span", evidenceCoverageText(company)), el("span", whyCompanyAppears(company, context, form)));
        target.append(row);
    }
}

function renderQuickDrawer(target: HTMLElement, response: CompanyResearchResponse, context: SourceContext, form: HTMLFormElement, view: CompanyBrowseView) {
    target.replaceChildren();
    const company = response.Company!;
    const header = el("header", undefined, "company-drawer-header");
    header.append(el("code", company.CompanyId, "company-stable-id"), el("h2", company.Name ?? company.CompanyId),
        el("p", `${tickerMarket(company)} · ${company.CountryRegion || "地区未记录"}`));
    const badges = el("div", undefined, "company-badges");
    for (const state of company.VerificationStates?.length ? company.VerificationStates : ["unknown"])
        badges.append(badge(meaningfulStateLabel(state), state));
    header.append(badges);

    const summary = el("section", undefined, "company-drawer-section");
    summary.append(el("h3", "Why it appears here"), el("p", whyCompanyAppears(company, context, form)),
        el("p", company.CoverageNote || "Coverage note 未记录；不得补写供应、客户、份额或产能事实。", "company-scope-note"));

    const metrics = el("dl", undefined, "company-drawer-metrics");
    appendDefinition(metrics, "Evidence coverage", evidenceCoverageText(company));
    appendDefinition(metrics, "Evidence review states", evidenceReviewStateText(response));
    appendDefinition(metrics, "Unknown-state rule", meaningfulStateLabel("unknown"));
    appendDefinition(metrics, "Open questions", String(response.ResearchGaps?.length ?? 0));
    appendDefinition(metrics, "Source context", sourceContextLabel(context, form, response.LinkOptions));
    summary.append(metrics);

    const exposure = el("section", undefined, "company-drawer-section");
    exposure.append(el("h3", "Exposure tags"));
    appendExposurePreview(exposure, company.Exposures, response.LinkOptions);

    const links = el("section", undefined, "company-drawer-section company-drawer-actions");
    links.append(el("h3", "Quick links / sections"));
    const sectionList = el("ul", undefined, "company-drawer-section-list");
    for (const label of ["Company Overview", "Industry-chain Exposure", "Key Evidence", "Open Questions", "Material Events / Financial Evidence"])
        sectionList.append(el("li", label));
    const expand = nativeLink(companyUrl(company.CompanyId, contextFromForm(context, form, view)), "↗ Expand to Full Company Detail");
    expand.className = "btn btn-primary btn-sm company-expand-link";
    expand.setAttribute("aria-label", `Expand ${company.Name ?? company.CompanyId} to Full Company Detail`);
    links.append(sectionList, expand, nativeLink("#company-card-panel", "返回 Company Pool 当前筛选"));

    target.append(header, summary, exposure, links);
}

async function initCompanyDetail(companyId?: string) {
    const target = document.querySelector<HTMLElement>("#company-detail-content");
    if (!target || !companyId)
        return;
    try {
        const response = await CompanyUniverseService.Retrieve({ CompanyId: companyId });
        const context = readSourceContext(location.search);
        renderCompanyDetail(target, response, context);
        syncCompanyBackLink(context);
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

function renderCompanyDetail(target: HTMLElement, response: CompanyResearchResponse, context: SourceContext) {
    target.replaceChildren();
    const company = response.Company!;
    const header = el("header", undefined, "company-detail-header");
    header.append(el("code", company.CompanyId, "company-stable-id"), el("h2", company.Name ?? company.CompanyId),
        el("p", `${company.EnglishName || "英文名未记录"} · ${tickerMarket(company)} · ${company.CountryRegion || "地区未记录"}`));
    const badges = el("div", undefined, "company-badges");
    badges.append(badge(company.UniverseLayer), badge(company.CoveragePriority));
    for (const state of company.VerificationStates?.length ? company.VerificationStates : ["unknown"])
        badges.append(badge(meaningfulStateLabel(state), state));
    header.append(badges, el("p", company.CoverageNote || "Coverage note 未记录；不得补写未来源化事实。", "company-scope-note"));
    target.append(header);

    const contextSection = detailSection("Current Research Context");
    contextSection.append(el("p", sourceContextLabel(context, undefined, response.LinkOptions)), gap("R5 保留 Explorer/Company Pool 来源路径，但不创建 Workspace 写入、比较视图或新的研究实体。"));

    const overview = detailSection("Company Overview");
    const dl = el("dl", undefined, "company-overview-grid");
    appendDefinition(dl, "Stable company ID", company.CompanyId);
    appendDefinition(dl, "证券 / 市场", tickerMarket(company));
    appendDefinition(dl, "地区", company.CountryRegion);
    appendDefinition(dl, "公司池层级", company.UniverseLayer);
    appendDefinition(dl, "覆盖优先级", company.CoveragePriority);
    appendDefinition(dl, "Evidence coverage", evidenceCoverageText(company));
    appendDefinition(dl, "Evidence review states", evidenceReviewStateText(response));
    appendDefinition(dl, "Unknown-state rule", meaningfulStateLabel("unknown"));
    appendDefinition(dl, "Freshness", meaningfulStateLabel(company.Freshness));
    overview.append(dl);
    if (company.OfficialUrl) {
        const official = nativeLink(company.OfficialUrl, "打开官方研究入口 ↗");
        official.target = "_blank";
        official.rel = "noopener noreferrer";
        overview.append(official);
    }

    const exposure = detailSection("Industry-chain Exposure");
    if (!company.Exposures?.length)
        exposure.append(gap("尚无 CompanyExposure 记录。不得由公司名称、产品分类或关键词推导 part / chain 关系。"));
    else
        company.Exposures.forEach(item => exposure.append(exposureCard(item, response.LinkOptions)));

    const keyEvidence = detailSection("Key Evidence");
    renderEvidenceList(keyEvidence, response.SourcesAudit?.slice(0, 6), "尚无显式关联 source/evidence audit 记录。空缺不表示已经确认无风险或无关系。 ");

    const openQuestions = detailSection("Open Questions");
    openQuestions.append(gapsBlock(response.ResearchGaps ?? []));

    const eventsFinancial = detailSection("Material Events / Financial Evidence");
    if (!response.Events?.length)
        eventsFinancial.append(gap("尚无与该 stable company ID 显式关联的事件记录。"));
    else
        response.Events.forEach(item => eventsFinancial.append(record(`${item.EventId} · ${item.EventType}`, item.Title, `${formatDate(item.EventTime)} · ${item.Description || "无描述"}`)));
    renderEvidenceList(eventsFinancial, response.EarningsFinancialEvidence, "当前没有经类型化关系确认的 earnings / financial evidence；不做关键词分类。 ");
    renderEvidenceList(eventsFinancial, response.CapexInvestmentEvidence, "当前没有经类型化关系确认的 Capex / investment evidence；不推断投资、订单或收入。 ");

    const workspace = detailSection("Link to Research Workspace");
    workspace.append(gap("Workspace implementation remains out of scope for R5；此处仅提供上下文跳转，不提供写入。"), nativeLink(resolveUrl("~/Research/Workspace"), "打开 Research Workspace placeholder"));

    target.append(contextSection, overview, exposure, keyEvidence, openQuestions, eventsFinancial, workspace);
}

function renderChainNode(target: HTMLElement, response: ChainNodeResearchResponse) {
    target.replaceChildren();
    const header = el("header", undefined, "company-detail-header");
    header.append(el("code", response.Node?.Id ?? "", "company-stable-id"), el("h2", response.Node?.Name ?? "产业链节点"),
        el("p", "该页面仅提供 stable cross-navigation；关系来自数据库显式映射。"));
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

function exposureCard(exposure: CompanyExposureDetail, options?: CompanyFilterOptions) {
    const card = el("article", undefined, "company-exposure-card");
    const heading = el("div", undefined, "company-record-heading");
    heading.append(el("h3", `${exposure.Role || "role unknown"} · ${exposure.Relevance || "relevance unknown"}`),
        badge(meaningfulStateLabel(exposure.VerificationState), exposure.VerificationState));
    card.append(heading, el("p", `Confidence: ${exposure.Confidence || "unknown"} · verified-policy evidence: ${exposure.MeetsVerifiedPolicy ? "满足" : "不满足"}`, "company-meta"));
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
    if (options?.Parts || options?.ChainNodes) {
        // options are accepted for service contract continuity; R5 deliberately provides no write editor.
    }
    return card;
}

function appendExposurePreview(target: HTMLElement, exposures?: CompanyExposureDetail[], options?: CompanyFilterOptions) {
    if (!exposures?.length) {
        target.append(gap("尚无 CompanyExposure 记录；unknown/discovery 不会被显示成 verified。"));
        return;
    }
    const list = el("div", undefined, "company-drawer-exposures");
    for (const exposure of exposures.slice(0, 4)) {
        const item = el("article", undefined, "company-drawer-exposure");
        item.append(el("strong", `${exposure.Role || "role unknown"} · ${exposure.Relevance || "unknown"}`),
            badge(meaningfulStateLabel(exposure.VerificationState), exposure.VerificationState),
            el("p", exposure.ScopeNote || "Scope note 未记录"));
        if (exposure.Part || exposure.ChainNode)
            item.append(el("small", [exposure.Part?.Name, exposure.ChainNode?.Name].filter(Boolean).join(" → ")));
        list.append(item);
    }
    target.append(list);
    if ((exposures.length ?? 0) > 4)
        target.append(el("p", `另有 ${exposures.length - 4} 条显式 exposure；请展开 Full Detail 查看。`, "company-meta"));
    if (options?.Roles) {
        // keep generated DTO referenced without creating additional UI semantics.
    }
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

function readFilters(form: HTMLFormElement, context?: SourceContext): CompanyUniverseRequest {
    return normalizeCompanyFilters(new FormData(form).entries(), {
        SearchText: context?.searchText,
        PartId: context?.partId,
        ChainNodeId: context?.chainNodeId,
        Role: context?.role,
        CountryRegion: context?.countryRegion,
        VerificationState: context?.verificationState
    }) as CompanyUniverseRequest;
}

function populateFilters(form: HTMLFormElement, options?: CompanyFilterOptions) {
    setNamedLinkOptions(form, "PartId", options?.Parts);
    setNamedLinkOptions(form, "ChainNodeId", options?.ChainNodes);
    setStringOptions(form, "Role", options?.Roles);
    setStringOptions(form, "CountryRegion", options?.CountriesRegions);
    setStringOptions(form, "VerificationState", options?.VerificationStates, meaningfulStateLabel);
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

function applySourceDefaults(form: HTMLFormElement, context: SourceContext) {
    setInputIfPresent(form, "SearchText", context.searchText);
    setSelectIfPresent(form, "PartId", context.partId);
    setSelectIfPresent(form, "ChainNodeId", context.chainNodeId);
    setSelectIfPresent(form, "Role", context.role);
    setSelectIfPresent(form, "CountryRegion", context.countryRegion);
    setSelectIfPresent(form, "VerificationState", context.verificationState);
}

function setInputIfPresent(form: HTMLFormElement, name: string, value?: string) {
    if (!value)
        return;
    const input = form.elements.namedItem(name) as HTMLInputElement | null;
    if (input)
        input.value = value;
}

function setSelectIfPresent(form: HTMLFormElement, name: string, value?: string) {
    if (!value)
        return;
    const select = form.elements.namedItem(name) as HTMLSelectElement | null;
    if (select && [...select.options].some(item => item.value === value))
        select.value = value;
}

function readSourceContext(search: string): SourceContext {
    const params = new URLSearchParams(search);
    return {
        source: params.get("source") || undefined,
        componentId: params.get("componentId") || undefined,
        partId: params.get("partId") || params.get("PartId") || undefined,
        chainNodeId: params.get("chainNodeId") || params.get("ChainNodeId") || undefined,
        searchText: params.get("SearchText") || params.get("searchText") || undefined,
        role: params.get("Role") || params.get("role") || undefined,
        countryRegion: params.get("CountryRegion") || params.get("countryRegion") || undefined,
        verificationState: params.get("VerificationState") || params.get("verificationState") || undefined,
        view: isCompanyBrowseView(params.get("view") || undefined) ? params.get("view") as CompanyBrowseView : undefined
    };
}

function contextFromForm(context: SourceContext, form: HTMLFormElement, view?: CompanyBrowseView): SourceContext {
    return {
        ...context,
        searchText: ((form.elements.namedItem("SearchText") as HTMLInputElement | null)?.value || context.searchText),
        partId: ((form.elements.namedItem("PartId") as HTMLSelectElement | null)?.value || context.partId),
        chainNodeId: ((form.elements.namedItem("ChainNodeId") as HTMLSelectElement | null)?.value || context.chainNodeId),
        role: ((form.elements.namedItem("Role") as HTMLSelectElement | null)?.value || context.role),
        countryRegion: ((form.elements.namedItem("CountryRegion") as HTMLSelectElement | null)?.value || context.countryRegion),
        verificationState: ((form.elements.namedItem("VerificationState") as HTMLSelectElement | null)?.value || context.verificationState),
        view: view ?? context.view
    };
}

function sourceContextLabel(context?: SourceContext, form?: HTMLFormElement, options?: CompanyFilterOptions) {
    const parts = [context?.source === "cpo-explorer" ? "CPO Explorer" : "Company Pool"];
    if (context?.componentId)
        parts.push(componentLabels[context.componentId] ?? context.componentId);
    const partId = selectedOptionValue(form, "PartId") || context?.partId;
    const chainNodeId = selectedOptionValue(form, "ChainNodeId") || context?.chainNodeId;
    const partLabel = selectedOptionLabel(form, "PartId", namedLinkLabel(options?.Parts, partId) ?? partId);
    const chainLabel = selectedOptionLabel(form, "ChainNodeId", namedLinkLabel(options?.ChainNodes, chainNodeId) ?? chainNodeId);
    if (partId || partLabel)
        parts.push(contextPathSegment(partLabel, partId));
    if (chainNodeId || chainLabel)
        parts.push(contextPathSegment(chainLabel, chainNodeId));
    return parts.join(" → ");
}

function selectedOptionValue(form: HTMLFormElement | undefined, name: string) {
    const select = form?.elements.namedItem(name) as HTMLSelectElement | null;
    return select?.value || undefined;
}

function contextPathSegment(label?: string, stableId?: string) {
    if (!label)
        return stableId ?? "";
    if (!stableId || label === stableId)
        return label;
    return `${label} (${stableId})`;
}

function selectedOptionLabel(form: HTMLFormElement | undefined, name: string, fallback?: string) {
    const select = form?.elements.namedItem(name) as HTMLSelectElement | null;
    if (select?.value) {
        const label = select.selectedOptions[0]?.textContent?.trim();
        if (label && label !== "全部")
            return label;
    }
    return fallback;
}

function namedLinkLabel(items: ResearchNamedLink[] | undefined, id?: string) {
    return items?.find(item => item.Id === id)?.Name;
}

function whyCompanyAppears(company: CompanyUniverseItem, context: SourceContext, form: HTMLFormElement) {
    const partId = (form.elements.namedItem("PartId") as HTMLSelectElement | null)?.value || context.partId;
    const chainNodeId = (form.elements.namedItem("ChainNodeId") as HTMLSelectElement | null)?.value || context.chainNodeId;
    const matchingExposure = company.Exposures?.find(item =>
        (partId && item.Part?.Id === partId) || (chainNodeId && item.ChainNode?.Id === chainNodeId));
    if (matchingExposure)
        return `因显式 CompanyExposure 连接到当前来源 context：${[matchingExposure.Part?.Name, matchingExposure.ChainNode?.Name].filter(Boolean).join(" → ")}；状态 ${meaningfulStateLabel(matchingExposure.VerificationState)}。`;
    return company.CoverageNote || "来自 CompanyUniverseService 的稳定 company ID；未由 prototype/mock 推导事实。";
}

function queryForContext(context?: SourceContext) {
    const params = new URLSearchParams();
    if (context?.source)
        params.set("source", context.source);
    if (context?.componentId)
        params.set("componentId", context.componentId);
    if (context?.partId)
        params.set("partId", context.partId);
    if (context?.chainNodeId)
        params.set("chainNodeId", context.chainNodeId);
    if (context?.searchText)
        params.set("SearchText", context.searchText);
    if (context?.role)
        params.set("Role", context.role);
    if (context?.countryRegion)
        params.set("CountryRegion", context.countryRegion);
    if (context?.verificationState)
        params.set("VerificationState", context.verificationState);
    if (context?.view)
        params.set("view", context.view);
    const query = params.toString();
    return query ? `?${query}` : "";
}

function tickerMarket(company: CompanyUniverseItem) {
    return `${company.Ticker || "ticker 未记录"} · ${company.Exchange || "市场未记录"}`;
}

function evidenceCoverageText(company: CompanyUniverseItem) {
    return `${meaningfulStateLabel(company.EvidenceCoverage)} · reviewed ${company.ReviewedEvidenceCount ?? 0}/${company.EvidenceCount ?? 0}`;
}

function evidenceReviewStateText(response: CompanyResearchResponse) {
    const states = new Set<string>();
    for (const item of response.SourcesAudit ?? [])
        states.add(item.ReviewState || "unknown");
    for (const item of response.EarningsFinancialEvidence ?? [])
        states.add(item.ReviewState || "unknown");
    for (const item of response.CapexInvestmentEvidence ?? [])
        states.add(item.ReviewState || "unknown");
    for (const exposure of response.Company?.Exposures ?? []) {
        for (const item of exposure.SupportingEvidence ?? [])
            states.add(item.ReviewState || "unknown");
        for (const item of exposure.ContradictingEvidence ?? [])
            states.add(item.ReviewState || "unknown");
        for (const item of exposure.ContextEvidence ?? [])
            states.add(item.ReviewState || "unknown");
    }
    return states.size ? [...states].sort().map(meaningfulStateLabel).join(" · ") : "Unknown / 未记录（不可视为已核验）";
}

function stateSummary(states?: string[]) {
    const wrap = el("span", undefined, "company-state-list");
    for (const state of states?.length ? states : ["unknown"])
        wrap.append(badge(meaningfulStateLabel(state), state));
    return wrap;
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

function detailSection(title: string) {
    const section = el("section", undefined, "company-detail-section");
    section.append(sectionTitle(title));
    return section;
}

function badge(text?: string, state?: string) {
    const node = el("span", text || "Unknown / 未记录", `company-badge state-${state || "unknown"}`);
    node.dataset.trustTone = stateTrustTone(state);
    return node;
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

function nativeLink(href: string, text?: string) {
    const link = document.createElement("a");
    link.href = href;
    link.textContent = text || href;
    return link;
}

function joinOrGap(values?: string[]) {
    return values?.length ? values.join(", ") : "研究缺口";
}

function companyUrl(companyId?: string, context?: SourceContext) {
    return resolveUrl(`~/Research/Companies/${encodeURIComponent(companyId ?? "")}${queryForContext(context)}`);
}

function syncCompanyBackLink(context: SourceContext) {
    const link = document.querySelector<HTMLAnchorElement>(".company-back-link");
    if (link)
        link.href = resolveUrl(`~/Research/Companies${queryForContext(context)}`);
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

function isCompanyActivationTarget(target: Node) {
    return target instanceof Element && !!target.closest('[data-company-card="true"], [data-company-row="true"]');
}

function el<K extends keyof HTMLElementTagNameMap>(tag: K, text?: string, className?: string): HTMLElementTagNameMap[K] {
    const node = document.createElement(tag);
    if (text !== undefined)
        node.textContent = text;
    if (className)
        node.className = className;
    return node;
}
