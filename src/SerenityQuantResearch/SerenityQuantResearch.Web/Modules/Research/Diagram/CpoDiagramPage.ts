import { notifyError, resolveUrl } from "@serenity-is/corelib";
import { PartResearchService } from "../../ServerTypes/Research/PartResearchService";
import type { CompanyExposureSummary } from "../../ServerTypes/Research/Services.CompanyExposureSummary";
import type { EvidenceSummary } from "../../ServerTypes/Research/Services.EvidenceSummary";
import type { PartCatalogResponse } from "../../ServerTypes/Research/Services.PartCatalogResponse";
import type { PartResearchResponse } from "../../ServerTypes/Research/Services.PartResearchResponse";
import type { ResearchModuleSummary } from "../../ServerTypes/Research/Services.ResearchModuleSummary";
import type { ResearchNamedLink } from "../../ServerTypes/Research/Services.ResearchNamedLink";
import type { ResearchPartSummary } from "../../ServerTypes/Research/Services.ResearchPartSummary";
import type { ResearchSectionSummary } from "../../ServerTypes/Research/Services.ResearchSectionSummary";
import "./CpoDiagramPage.css";
import {
    ExplorerViewMode,
    PartSelectionState,
    activePartId,
    clearSelection,
    hoverPart,
    interactionState,
    isSelectionKey,
    relatedCompanyCountLabel,
    researchEmptyStateText,
    switchExplorerView,
    togglePartSelection
} from "./PartSelectionState";
import { LatestRequest, RetryablePromiseCache } from "./ResearchRequestState";

const siPhComponentId = "cpo.mod.pic";
const companyPoolContextUrl = "~/Research/Companies?source=cpo-explorer&componentId=cpo.mod.pic";

interface SliceChildResearch {
    part: ResearchPartSummary;
    response?: PartResearchResponse;
    error?: unknown;
}

interface SliceModel {
    module: ResearchModuleSummary;
    children: ResearchPartSummary[];
}

export default async function pageInit(options?: { mode?: "diagram" | "detail"; partId?: string }) {
    if (options?.mode === "detail") {
        await initDetail(options.partId ?? document.querySelector<HTMLElement>("#cpo-research-app")?.dataset.partId);
        return;
    }

    await initDiagram();
}

async function listParts(): Promise<PartCatalogResponse> {
    return await PartResearchService.ListParts({});
}

async function retrievePart(partId: string): Promise<PartResearchResponse> {
    return await PartResearchService.RetrieveCompleteChain({ PartId: partId });
}

async function initDetail(partId?: string) {
    const target = document.querySelector<HTMLElement>("#cpo-detail-content");
    if (!target || !partId)
        return;

    try {
        target.setAttribute("aria-busy", "true");
        const response = await retrievePart(partId);
        renderPartDetail(target, response, false);
        document.title = `${response.Part?.Name ?? "部件研究详情"} - SerenityQuantResearch`;
    }
    catch (error) {
        renderError(target, `无法读取部件 ${partId}`, error);
    }
    finally {
        target.removeAttribute("aria-busy");
    }
}

async function initDiagram() {
    const app = document.querySelector<HTMLElement>("#cpo-explorer-app");
    const coverage = document.querySelector<HTMLElement>("#cpo-coverage");
    const stateLine = document.querySelector<HTMLElement>("#cpo-state-line");
    const canvas = document.querySelector<HTMLElement>("#cpo-canvas-frame");
    const drawer = document.querySelector<HTMLElement>("#cpo-research-drawer");
    const drawerContent = document.querySelector<HTMLElement>("#cpo-drawer-content");
    const closeButton = document.querySelector<HTMLButtonElement>("#cpo-close-drawer");
    const flatButton = document.querySelector<HTMLButtonElement>("#cpo-view-flat");
    const threeButton = document.querySelector<HTMLButtonElement>("#cpo-view-three");
    const flatScene = document.querySelector<SVGSVGElement>("#cpo-scene-flat");
    const threeScene = document.querySelector<SVGSVGElement>("#cpo-scene-three");

    if (!app || !stateLine || !canvas || !drawer || !drawerContent || !closeButton || !flatButton || !threeButton || !flatScene || !threeScene)
        return;

    const drawerRequests = new LatestRequest();
    let state: PartSelectionState = { viewMode: "three" };
    let model: SliceModel | undefined;
    let selectedChildId: string | undefined;
    let selectionSource: HTMLElement | SVGElement | undefined;
    let restoringFocus = false;

    const responseCache = new RetryablePromiseCache<string, PartResearchResponse>(retrievePart);

    try {
        app.setAttribute("aria-busy", "true");
        const catalog = await listParts();
        model = resolveSiPhSlice(catalog);
        if (!model) {
            markUnavailable(app, coverage, stateLine, "SiPh PIC component not found", "未在研究服务返回的 module/part 目录中找到 cpo.mod.pic；页面不会使用非权威示例数据替代。");
            return;
        }

        if (coverage)
            coverage.textContent = `SiPh PIC · ${model.children.length} 个真实子部件 · 材料数据缺口显式`;
        updateStateLine(stateLine, model, state);
        app.dataset.ready = "true";
    }
    catch (error) {
        markUnavailable(app, coverage, stateLine, "无法读取 SiPh PIC 目录", error instanceof Error ? error.message : "请检查服务状态与访问权限。");
        notifyError("CPO Explorer 目录读取失败");
        return;
    }
    finally {
        app.removeAttribute("aria-busy");
    }

    const reset = (restoreFocus: boolean = true) => {
        const source = selectionSource;
        drawerRequests.cancel();
        selectedChildId = undefined;
        selectionSource = undefined;
        state = clearSelection(state);
        syncVisualState(app, [flatScene, threeScene], state);
        updateStateLine(stateLine, model, undefined);
        closeDrawer(app, drawer, drawerContent);
        updateStateLine(stateLine, model, state);
        if (restoreFocus && source?.isConnected) {
            restoringFocus = true;
            source.focus({ preventScroll: true });
            restoringFocus = false;
        }
    };

    const renderSelected = async (source?: HTMLElement | SVGElement) => {
        if (!model)
            return;
        const request = drawerRequests.begin();
        selectionSource = source;
        selectedChildId = undefined;
        syncVisualState(app, [flatScene, threeScene], state);
        updateStateLine(stateLine, model, state);
        openDrawer(app, drawer, drawerContent, el("div", "正在读取 SiPh PIC 子部件研究链…", "cpo-loading"));

        const childResearch = await Promise.all(model.children.map(async part => {
            if (!part.Id)
                return { part } satisfies SliceChildResearch;
            try {
                return { part, response: await responseCache.get(part.Id) } satisfies SliceChildResearch;
            }
            catch (error) {
                return { part, error } satisfies SliceChildResearch;
            }
        }));

        if (!drawerRequests.isCurrent(request) || state.selectedId !== siPhComponentId)
            return;

        const rerender = (childId: string) => {
            selectedChildId = selectedChildId === childId ? undefined : childId;
            renderSliceDrawer(drawerContent, model!, childResearch, selectedChildId, rerender);
        };
        renderSliceDrawer(drawerContent, model, childResearch, selectedChildId, rerender);
    };

    const setHover = (componentId?: string) => {
        state = hoverPart(state, componentId);
        syncVisualState(app, [flatScene, threeScene], state);
        updateStateLine(stateLine, model, state);
    };

    const select = (componentId: string, source?: HTMLElement | SVGElement) => {
        state = togglePartSelection(state, componentId);
        if (state.selectedId)
            void renderSelected(source);
        else
            reset(false);
    };

    bindInteractiveObjects(document, setHover, select, () => restoringFocus);

    canvas.addEventListener("click", event => {
        if ((event.target as Element).closest(".cpo-component,.cpo-callout"))
            return;
        if (state.selectedId)
            reset(false);
    });
    drawer.addEventListener("click", event => event.stopPropagation());
    closeButton.addEventListener("click", event => {
        event.stopPropagation();
        reset();
    });
    document.addEventListener("keydown", event => {
        if (event.key === "Escape" && state.selectedId)
            reset();
    });

    const setView = (viewMode: ExplorerViewMode) => {
        state = switchExplorerView(state, viewMode);
        syncView(app, flatScene, threeScene, flatButton, threeButton, viewMode);
        syncVisualState(app, [flatScene, threeScene], state);
    };

    flatButton.addEventListener("click", () => setView("flat"));
    threeButton.addEventListener("click", () => setView("three"));

    syncView(app, flatScene, threeScene, flatButton, threeButton, state.viewMode ?? "three");
    syncVisualState(app, [flatScene, threeScene], state);
}

function resolveSiPhSlice(catalog: PartCatalogResponse): SliceModel | undefined {
    const modules = [...(catalog.Modules ?? [])].sort((a, b) => (a.SortOrder ?? 0) - (b.SortOrder ?? 0));
    const module = modules.find(x => x.Id === siPhComponentId);
    if (!module)
        return undefined;

    return {
        module,
        children: [...(module.Parts ?? [])].sort((a, b) => (a.PartSortOrder ?? 0) - (b.PartSortOrder ?? 0))
    };
}

function bindInteractiveObjects(root: ParentNode, onHover: (componentId?: string) => void,
    onSelect: (componentId: string, source?: HTMLElement | SVGElement) => void, isRestoringFocus: () => boolean) {
    root.querySelectorAll<HTMLElement | SVGElement>(".cpo-component[data-component-id],.cpo-callout[data-component-id]").forEach(element => {
        element.addEventListener("mouseenter", () => onHover(element.dataset.componentId));
        element.addEventListener("mouseleave", () => onHover(undefined));
        element.addEventListener("focus", () => {
            if (!isRestoringFocus())
                onHover(element.dataset.componentId);
        });
        element.addEventListener("blur", () => {
            if (!isRestoringFocus())
                onHover(undefined);
        });
        element.addEventListener("click", event => {
            event.stopPropagation();
            onSelect(element.dataset.componentId!, element);
        });
        element.addEventListener("keydown", event => {
            if (!isSelectionKey(event.key))
                return;
            event.preventDefault();
            event.stopPropagation();
            onSelect(element.dataset.componentId!, element);
        });
    });
}

function syncVisualState(app: HTMLElement, scenes: SVGSVGElement[], state: PartSelectionState) {
    const activeId = activePartId(state);
    app.dataset.selected = state.selectedId ?? "";
    app.classList.toggle("is-drawer-open", !!state.selectedId);
    for (const scene of scenes) {
        scene.classList.toggle("is-focused", !!activeId);
        scene.querySelectorAll<HTMLElement | SVGElement>("[data-component-id]").forEach(element => {
            const visual = interactionState(state, element.dataset.componentId ?? "");
            element.classList.toggle("is-active", visual === "active");
            element.classList.toggle("is-hovered", visual === "hovered");
            element.classList.toggle("is-dimmed", visual === "dimmed");
            if (element.classList.contains("cpo-component") || element.classList.contains("cpo-callout")) {
                element.setAttribute("aria-pressed", String(visual === "active"));
                element.setAttribute("aria-expanded", String(visual === "active"));
            }
        });
    }
}

function syncView(app: HTMLElement, flatScene: SVGSVGElement, threeScene: SVGSVGElement,
    flatButton: HTMLButtonElement, threeButton: HTMLButtonElement, viewMode: ExplorerViewMode) {
    app.dataset.view = viewMode;
    flatScene.classList.toggle("is-active", viewMode === "flat");
    threeScene.classList.toggle("is-active", viewMode === "three");
    flatButton.classList.toggle("is-active", viewMode === "flat");
    threeButton.classList.toggle("is-active", viewMode === "three");
    flatButton.setAttribute("aria-pressed", String(viewMode === "flat"));
    threeButton.setAttribute("aria-pressed", String(viewMode === "three"));
}

function updateStateLine(target: HTMLElement, model?: SliceModel, state: PartSelectionState = {}) {
    if (!model) {
        replaceChildren(target, el("strong", "目录不可用"), el("span", "研究服务未返回可验证 SiPh PIC 目录。"));
        return;
    }

    if (state.selectedId === siPhComponentId) {
        replaceChildren(target,
            el("strong", `${model.module.Name ?? "SiPh PIC"} selected`),
            el("span", `${model.children.length} 个真实 child parts；材料采用显式缺口，相关公司仅由显式 exposure 显示。`));
        return;
    }

    if (state.hoveredId === siPhComponentId) {
        replaceChildren(target,
            el("strong", `${model.module.Name ?? "SiPh PIC"} hover preview`),
            el("span", "当前只是悬停聚焦；单击组件或 callout 后才会锁定选择并打开研究抽屉。"));
        return;
    }

    replaceChildren(target,
        el("strong", "Overview"),
        el("span", "当前版本聚焦 SiPh PIC；其他器件仅作空间上下文，不承载公司或材料事实。"));
}

function openDrawer(app: HTMLElement, drawer: HTMLElement, drawerContent: HTMLElement, content: Node) {
    drawer.hidden = false;
    drawer.setAttribute("aria-hidden", "false");
    drawer.classList.add("is-open");
    app.classList.add("is-drawer-open");
    replaceChildren(drawerContent, content);
}

function closeDrawer(app: HTMLElement, drawer: HTMLElement, drawerContent: HTMLElement) {
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    drawer.hidden = true;
    app.classList.remove("is-drawer-open");
    replaceChildren(drawerContent,
        el("span", "Research Context", "cpo-kicker"),
        Object.assign(el("h2", "SiPh PIC"), { id: "cpo-drawer-title", tabIndex: -1 }),
        el("p", "选择组件后显示真实子部件、权威技术关系与公司映射缺口。"));
}

function renderSliceDrawer(target: HTMLElement, model: SliceModel, childResearch: SliceChildResearch[], selectedChildId: string | undefined,
    onChildSelect: (childId: string) => void) {
    const selectedChild = selectedChildId ? childResearch.find(x => x.part.Id === selectedChildId) : undefined;
    const visibleResearch = selectedChild ? [selectedChild] : childResearch;
    const retrievalFailures = visibleResearch.filter(x => x.error);
    const hasRetrievalFailure = retrievalFailures.length > 0;
    const technologies = dedupeNamedLinks(visibleResearch.flatMap(x => x.response?.Technologies ?? []));
    const companies = dedupeCompanies(visibleResearch.flatMap(x => x.response?.Companies ?? []));
    const evidence = visibleResearch.flatMap(x => x.response?.Evidence ?? []);
    const warnings = visibleResearch.flatMap(x => x.response?.StatusWarnings ?? []);

    const header = el("header", undefined, "cpo-drawer-header");
    header.append(
        el("span", "Research Context", "cpo-kicker"),
        Object.assign(el("h2", model.module.Name ?? "SiPh PIC"), { id: "cpo-drawer-title", tabIndex: -1 }),
        el("p", "当前选择：CPO → SiPh PIC。该组件使用 stable module ID cpo.mod.pic；下方子部件来自现有研究目录中的 PhysicalPart 记录。"));
    const badges = el("div", undefined, "cpo-badge-row");
    badges.append(badge("stable: cpo.mod.pic", "stable"), badge(`${model.children.length} child parts`, "count"), badge("material gap explicit", "gap"));
    header.append(badges);

    const childSection = researchSection("真实子部件");
    const childList = el("div", undefined, "cpo-child-list");
    for (const item of childResearch) {
        const part = item.part;
        const button = document.createElement("button");
        button.type = "button";
        button.className = `cpo-child-card${selectedChildId === part.Id ? " is-active" : ""}`;
        button.dataset.childPartId = part.Id ?? "";
        button.setAttribute("aria-pressed", String(selectedChildId === part.Id));
        button.append(
            el("strong", part.Name ?? part.Id ?? "未命名子部件"),
            el("span", part.FunctionSummary ?? "暂无功能摘要"),
            badge(item.error ? "research_chain_unknown" : (part.ResearchStatus ?? "unknown"), item.error ? "gap" : "status"));
        button.addEventListener("click", event => {
            event.stopPropagation();
            if (part.Id)
                onChildSelect(part.Id);
        });
        childList.append(button);
    }
    childSection.append(childList);

    const failureSection = hasRetrievalFailure ? researchRetrievalFailureSection(retrievalFailures) : undefined;

    const technologySection = researchSection(selectedChild ? "当前子部件技术 context" : "SiPh PIC 技术 context");
    if (technologies.length) {
        const chips = el("div", undefined, "cpo-chip-list");
        for (const technology of technologies)
            chips.append(badge(technology.Name ?? technology.Id ?? "未命名技术", "link"));
        technologySection.append(chips, el("p", "这些是现有数据中明确的 part→technology link；不等同于已核验离散材料目录。", "cpo-footnote"));
    }
    else {
        technologySection.append(el("p", researchEmptyStateText(hasRetrievalFailure,
            "尚无当前层级的技术链接。",
            "部分子部件研究链读取失败；当前不能确认是否没有技术链接。"), `cpo-empty${hasRetrievalFailure ? " is-unknown" : ""}`));
    }

    const materialSection = researchSection("材料数据状态");
    materialSection.append(el("p", hasRetrievalFailure
        ? "部分子部件研究链读取失败；材料数据状态不能完整确认。已返回记录未提供已核验离散材料目录。"
        : "暂无已核验材料数据。页面不会把示例材料名称呈现为已核验事实。", "cpo-empty"));

    const companySection = researchSection(`Related Companies (${relatedCompanyCountLabel(companies.length, hasRetrievalFailure)})`);
    if (companies.length) {
        const list = el("div", undefined, "cpo-record-list");
        for (const company of companies)
            list.append(companyCard(company));
        companySection.append(list);
    }
    else {
        companySection.append(el("p", researchEmptyStateText(hasRetrievalFailure,
            "尚无 SiPh PIC 或其子部件的显式公司暴露映射。不得由硅光类别或图形位置推导供应关系。",
            "部分子部件研究链读取失败；当前不能确认是否没有显式公司暴露映射。不得把服务失败解释为供应关系不存在。"), `cpo-empty${hasRetrievalFailure ? " is-unknown" : ""}`));
    }

    const action = document.createElement("a");
    action.className = "cpo-company-pool-link";
    action.href = resolveUrl(companyPoolContextUrl);
    action.textContent = "进入 Company Pool（保留 CPO → SiPh PIC context） →";

    const evidenceSectionNode = evidenceSummarySection(evidence, warnings, hasRetrievalFailure);

    replaceChildren(target, ...[header, childSection, failureSection, technologySection, materialSection, companySection, evidenceSectionNode, action].filter((x): x is Node => !!x));
}

function companyCard(company: CompanyExposureSummary) {
    const article = el("article", undefined, "cpo-record cpo-company-card");
    const heading = el("div", undefined, "cpo-record-heading");
    const companyLink = document.createElement("a");
    companyLink.href = resolveUrl(`~/Research/Companies/${encodeURIComponent(company.CompanyId ?? "")}?source=cpo-explorer&componentId=${encodeURIComponent(siPhComponentId)}`);
    companyLink.textContent = company.CompanyName ?? company.CompanyId ?? "未知公司";
    heading.append(companyLink, badge(company.VerificationState ?? "unknown", "verification"));
    article.append(heading,
        el("div", `${company.Role ?? "role unknown"} · relevance ${company.Relevance ?? "unknown"} · confidence ${company.Confidence ?? "unknown"}`, "cpo-record-meta"),
        el("p", company.ScopeNote || "暂无范围说明"));
    return article;
}

function researchRetrievalFailureSection(failures: SliceChildResearch[]) {
    const section = researchSection("Research chain status");
    const list = document.createElement("ul");
    list.className = "cpo-message-list";
    for (const item of failures)
        list.append(el("li", `${item.part.Name ?? item.part.Id ?? "未知子部件"} 研究链读取失败；下游技术、公司和 evidence 状态为 unknown。`));
    section.append(el("p", "部分子部件研究链读取失败；以下空状态不能解释为确认没有技术、公司或 evidence 映射。", "cpo-empty is-unknown"), list);
    return section;
}

function evidenceSummarySection(evidence: EvidenceSummary[], warnings: string[], hasRetrievalFailure = false) {
    const section = researchSection("Evidence safety");
    if (!evidence.length)
        section.append(el("p", researchEmptyStateText(hasRetrievalFailure,
            "当前 SiPh PIC 未返回直接 evidence；页面只展示 taxonomy/service 中已有的 child 与 technology context。",
            "部分子部件研究链读取失败；当前不能确认是否没有直接 evidence。"), `cpo-empty${hasRetrievalFailure ? " is-unknown" : ""}`));
    else {
        const list = el("div", undefined, "cpo-record-list");
        for (const item of evidence) {
            const article = el("article", undefined, "cpo-record");
            article.append(el("strong", `${item.EvidenceId}@v${item.Version}`), badge(item.ReviewState ?? "unknown", "review"), el("p", item.Proposition ?? "暂无命题"));
            list.append(article);
        }
        section.append(list);
    }
    if (warnings.length) {
        const list = document.createElement("ul");
        list.className = "cpo-message-list";
        for (const warning of Array.from(new Set(warnings)).slice(0, 4))
            list.append(el("li", warning));
        section.append(list);
    }
    return section;
}

function renderPartDetail(target: HTMLElement, response: PartResearchResponse, showDetailAction: boolean) {
    target.replaceChildren();
    const part = response.Part;
    const header = el("header", undefined, "cpo-drawer-header");
    header.append(el("span", part?.Id ?? "", "cpo-stable-id"), el("h2", part?.Name ?? "未知部件"),
        el("p", part?.FunctionSummary || "暂无功能摘要"));
    const badges = el("div", undefined, "cpo-badge-row");
    badges.append(badge(part?.ResearchStatus ?? "status_unknown", "status"), badge(part?.ModuleName ?? "未关联模块", "module"));
    header.append(badges);
    if (showDetailAction && part?.Id) {
        const link = document.createElement("a");
        link.className = "btn btn-primary cpo-detail-link";
        link.href = resolveUrl(`~/Research/Parts/${encodeURIComponent(part.Id)}`);
        link.textContent = "打开完整部件详情 →";
        header.append(link);
    }
    target.append(header);

    target.append(researchItemsSection("边界", response.Boundaries));
    target.append(researchItemsSection("上游 / 下游", response.UpstreamDownstream));
    target.append(namedLinksSection("产业链节点", response.ChainNodes, "尚无产业链节点映射"));
    target.append(namedLinksSection("技术链接", response.Technologies, "尚无技术链接"));
    target.append(evidenceSummarySection(response.Evidence ?? [], response.StatusWarnings ?? []));
    target.append(researchItemsSection("研究结论", response.Conclusions));
    target.append(researchItemsSection("风险", response.Risks));
}

function researchItemsSection(title: string, items?: ResearchSectionSummary[]) {
    const section = researchSection(title);
    const list = el("div", undefined, "cpo-record-list");
    if (!items?.length)
        list.append(el("p", "尚无记录；该空缺不表示已核验为不存在。", "cpo-empty"));
    else {
        for (const item of items) {
            const article = el("article", undefined, "cpo-record cpo-section-record");
            article.append(badge(item.State ?? "unknown", "section-state"), el("p", item.Text ?? "尚无说明"));
            list.append(article);
        }
    }
    section.append(list);
    return section;
}

function namedLinksSection(title: string, items: ResearchNamedLink[] | undefined, empty: string) {
    const section = researchSection(title);
    const list = el("div", undefined, "cpo-chip-list");
    if (!items?.length)
        list.append(el("span", empty, "cpo-empty"));
    else
        items.forEach(item => list.append(badge(item.Name ?? item.Id ?? "未命名", "link")));
    section.append(list);
    return section;
}

function dedupeNamedLinks(items: ResearchNamedLink[]) {
    const map = new Map<string, ResearchNamedLink>();
    for (const item of items) {
        const key = item.Id ?? item.Name;
        if (key && !map.has(key))
            map.set(key, item);
    }
    return [...map.values()];
}

function dedupeCompanies(items: CompanyExposureSummary[]) {
    const map = new Map<string, CompanyExposureSummary>();
    for (const item of items) {
        const key = item.CompanyId ?? item.CompanyName;
        if (key && !map.has(key))
            map.set(key, item);
    }
    return [...map.values()];
}

function researchSection(title: string) {
    const section = document.createElement("section");
    section.className = "cpo-research-section";
    section.append(el("h3", title));
    return section;
}

function badge(text: string, kind: string) {
    return el("span", text, `cpo-badge is-${kind}`);
}

function markUnavailable(app: HTMLElement, coverage: HTMLElement | null, stateLine: HTMLElement, title: string, detail: string) {
    app.dataset.ready = "error";
    if (coverage)
        coverage.textContent = "SiPh PIC 目录不可用";
    replaceChildren(stateLine, el("strong", title), el("span", detail));
}

function renderError(target: HTMLElement, title: string, error: unknown) {
    const message = error instanceof Error ? error.message : "请检查服务状态与访问权限。";
    replaceChildren(target, el("div", undefined, "alert alert-danger"));
    target.firstElementChild?.append(el("strong", title), document.createTextNode(`：${message}`));
}

function replaceChildren(target: HTMLElement, ...children: Node[]) {
    target.replaceChildren(...children);
}

function el<K extends keyof HTMLElementTagNameMap>(tag: K, text?: string, className?: string): HTMLElementTagNameMap[K] {
    const node = document.createElement(tag);
    if (text !== undefined)
        node.textContent = text;
    if (className)
        node.className = className;
    return node;
}
