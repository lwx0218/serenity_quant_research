import { notifyError, resolveUrl } from "@serenity-is/corelib";
import { PartResearchService } from "../../ServerTypes/Research/PartResearchService";
import type { CompanyExposureSummary } from "../../ServerTypes/Research/Services.CompanyExposureSummary";
import type { EvidenceSummary } from "../../ServerTypes/Research/Services.EvidenceSummary";
import type { PartCatalogResponse } from "../../ServerTypes/Research/Services.PartCatalogResponse";
import type { PartResearchResponse } from "../../ServerTypes/Research/Services.PartResearchResponse";
import type { ResearchModuleSummary } from "../../ServerTypes/Research/Services.ResearchModuleSummary";
import type { ResearchNamedLink } from "../../ServerTypes/Research/Services.ResearchNamedLink";
import type { ResearchSectionSummary } from "../../ServerTypes/Research/Services.ResearchSectionSummary";
import "./CpoDiagramPage.css";
import {
    PartSelectionState,
    activePartId,
    clearSelection,
    hoverPart,
    isSelectionKey,
    layerState,
    lockPart
} from "./PartSelectionState";
import { LatestRequest, RetryablePromiseCache } from "./ResearchRequestState";

const svgNs = "http://www.w3.org/2000/svg";

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
        renderResearch(target, response, false);
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
    const svg = document.querySelector<SVGSVGElement>("#cpo-diagram");
    const tree = document.querySelector<HTMLElement>("#cpo-part-tree");
    const coverage = document.querySelector<HTMLElement>("#cpo-coverage");
    const preview = document.querySelector<HTMLElement>("#cpo-hover-preview");
    const drawer = document.querySelector<HTMLElement>("#cpo-research-drawer");
    const drawerContent = document.querySelector<HTMLElement>("#cpo-drawer-content");
    const closeButton = document.querySelector<HTMLButtonElement>("#cpo-close-drawer");
    const clearButton = document.querySelector<HTMLButtonElement>("#cpo-clear-selection");
    if (!svg || !tree || !preview || !drawer || !drawerContent || !closeButton || !clearButton)
        return;

    try {
        svg.setAttribute("aria-busy", "true");
        const catalog = await listParts();
        const modules = [...(catalog.Modules ?? [])].sort((a, b) => (a.SortOrder ?? 0) - (b.SortOrder ?? 0));
        const parts = modules.flatMap(module => module.Parts ?? []);
        if (!modules.length || !parts.length) {
            renderCatalogUnavailable(svg, tree, coverage, preview,
                "部件目录为空", "研究服务没有返回可选择的物理部件。", "info");
            return;
        }

        const partById = new Map(parts.map(part => [part.Id!, part]));
        const responseCache = new RetryablePromiseCache<string, PartResearchResponse>(retrievePart);
        const drawerRequests = new LatestRequest();
        let state: PartSelectionState = {};
        let previewRequest = 0;
        let selectionSource: HTMLElement | SVGElement | undefined;
        let restoringFocus = false;

        if (coverage)
            coverage.textContent = `${modules.length} 个物理模块 · ${parts.length} 个可研究部件`;

        const getResearch = (partId: string) => responseCache.get(partId);

        const updateVisualState = () => {
            const currentId = activePartId(state);
            const activeModuleId = currentId ? partById.get(currentId)?.ModuleId : undefined;
            svg.querySelectorAll<SVGGElement>(".cpo-module-layer").forEach(group => {
                const visual = layerState(group.dataset.moduleId ?? "", activeModuleId);
                group.classList.toggle("is-active", visual === "active");
                group.classList.toggle("is-dimmed", visual === "dimmed");
            });
            svg.querySelectorAll<SVGGElement>("[data-part-id]").forEach(group => {
                const id = group.dataset.partId;
                group.classList.toggle("is-current", id === currentId);
                group.classList.toggle("is-locked", id === state.selectedId);
                group.setAttribute("aria-pressed", String(id === state.selectedId));
                group.setAttribute("aria-expanded", String(id === state.selectedId));
            });
            tree.querySelectorAll<HTMLButtonElement>("[data-part-id]").forEach(button => {
                const id = button.dataset.partId;
                button.classList.toggle("is-current", id === currentId);
                button.setAttribute("aria-pressed", String(id === state.selectedId));
                button.setAttribute("aria-expanded", String(id === state.selectedId));
            });
            clearButton.disabled = !state.selectedId;
        };

        const showPreview = async (partId?: string) => {
            const request = ++previewRequest;
            if (!partId) {
                replaceChildren(preview,
                    el("strong", "选择一个部件开始研究"),
                    el("span", `${parts.length} 个 seed part 均可通过图形或下方表格访问。`));
                return;
            }
            const part = partById.get(partId);
            replaceChildren(preview,
                el("strong", part?.Name ?? partId),
                el("span", `${part?.FunctionSummary ?? "正在读取研究摘要…"} · 正在读取候选公司`));
            try {
                const response = await getResearch(partId);
                if (request !== previewRequest)
                    return;
                replaceChildren(preview,
                    el("strong", response.Part?.Name ?? partId),
                    el("span", `${response.Part?.FunctionSummary ?? "暂无功能摘要"} · ${response.Companies?.length ?? 0} 家候选公司`));
            }
            catch (error) {
                if (request === previewRequest)
                    replaceChildren(preview, el("strong", part?.Name ?? partId), el("span", "研究摘要读取失败"));
            }
        };

        const hover = (partId?: string) => {
            state = hoverPart(state, partId);
            updateVisualState();
            void showPreview(activePartId(state));
        };

        const focus = (partId?: string) => {
            if (!restoringFocus)
                hover(partId);
        };

        const select = async (partId: string, source?: HTMLElement | SVGElement) => {
            const request = drawerRequests.begin();
            selectionSource = source;
            state = lockPart(state, partId);
            updateVisualState();
            void showPreview(partId);
            drawer.hidden = false;
            drawer.classList.add("is-open");
            drawerContent.setAttribute("aria-busy", "true");
            replaceChildren(drawerContent, el("div", "正在读取部件研究链…", "cpo-loading"));
            try {
                const response = await getResearch(partId);
                if (!drawerRequests.isCurrent(request) || state.selectedId !== partId)
                    return;
                renderResearch(drawerContent, response, true);
                drawer.querySelector<HTMLElement>("h2")?.focus();
            }
            catch (error) {
                if (drawerRequests.isCurrent(request) && state.selectedId === partId)
                    renderError(drawerContent, `无法读取部件 ${partId}`, error);
            }
            finally {
                if (drawerRequests.isCurrent(request) && state.selectedId === partId)
                    drawerContent.removeAttribute("aria-busy");
            }
        };

        renderDiagram(svg, modules, hover, focus, select);
        renderFallback(tree, modules, hover, focus, select);
        updateVisualState();

        const clear = () => {
            const source = selectionSource;
            drawerRequests.cancel();
            selectionSource = undefined;
            state = clearSelection(state);
            updateVisualState();
            void showPreview();
            drawerContent.removeAttribute("aria-busy");
            drawer.classList.remove("is-open");
            drawer.hidden = true;
            if (source?.isConnected) {
                restoringFocus = true;
                source.focus({ preventScroll: true });
                restoringFocus = false;
            }
        };
        closeButton.addEventListener("click", clear);
        clearButton.addEventListener("click", clear);
        document.addEventListener("keydown", event => {
            if (event.key === "Escape" && state.selectedId)
                clear();
        });
    }
    catch (error) {
        renderCatalogUnavailable(svg, tree, coverage, preview,
            "无法读取 CPO 部件目录", error instanceof Error ? error.message : "请检查服务状态与访问权限。", "danger");
        notifyError("CPO 部件目录读取失败");
    }
    finally {
        svg.removeAttribute("aria-busy");
    }
}

function renderDiagram(svg: SVGSVGElement, modules: ResearchModuleSummary[], onHover: (partId?: string) => void,
    onFocus: (partId?: string) => void, onSelect: (partId: string, source?: SVGElement) => void) {
    svg.replaceChildren();

    const defs = svgElement("defs");
    const gradient = svgElement("linearGradient", { id: "cpo-board-gradient", x1: "0", y1: "0", x2: "1", y2: "1" });
    gradient.append(svgElement("stop", { offset: "0", "stop-color": "#0e3340" }),
        svgElement("stop", { offset: "1", "stop-color": "#071e2a" }));
    defs.append(gradient);
    svg.append(defs);

    svg.append(svgElement("rect", { x: "8", y: "8", width: "984", height: "704", rx: "30", class: "cpo-board" }));
    const bus = svgElement("g", { class: "cpo-signal-bus", "aria-hidden": "true" });
    bus.append(svgElement("path", { d: "M 168 238 H 832 M 168 478 H 832 M 333 112 V 608 M 667 112 V 608" }));
    for (const [x, y] of [[333, 238], [667, 238], [333, 478], [667, 478]])
        bus.append(svgElement("circle", { cx: String(x), cy: String(y), r: "7" }));
    svg.append(bus);

    modules.forEach((module, index) => {
        const col = index % 3;
        const row = Math.floor(index / 3);
        const x = 25 + col * 325;
        const y = 25 + row * 232;
        const group = svgElement("g", {
            class: "cpo-module-layer",
            transform: `translate(${x} ${y})`,
            "data-module-id": module.Id ?? ""
        });
        group.append(svgElement("rect", { width: "300", height: "208", rx: "18", class: "cpo-module-frame" }));
        const number = svgElement("text", { x: "18", y: "31", class: "cpo-module-number" });
        number.textContent = String(index + 1).padStart(2, "0");
        const title = svgElement("text", { x: "58", y: "31", class: "cpo-module-title" });
        title.textContent = shortModuleName(module.Name);
        group.append(number, title);

        (module.Parts ?? []).forEach((part, partIndex) => {
            if (!part.Id)
                return;
            const partGroup = svgElement("g", {
                class: "cpo-part-node",
                transform: `translate(14 ${55 + partIndex * 47})`,
                tabindex: "0",
                role: "button",
                "aria-label": `${part.Name}，${part.FunctionSummary}`,
                "aria-pressed": "false",
                "aria-expanded": "false",
                "data-part-id": part.Id,
                "data-module-id": module.Id ?? ""
            });
            partGroup.append(svgElement("rect", { width: "272", height: "38", rx: "9", class: "cpo-part-surface" }));
            partGroup.append(svgElement("circle", { cx: "17", cy: "19", r: "5", class: "cpo-part-status" }));
            const label = svgElement("text", { x: "31", y: "24", class: "cpo-part-label" });
            label.textContent = part.Name ?? part.Id;
            partGroup.append(label);
            partGroup.addEventListener("mouseenter", () => onHover(part.Id));
            partGroup.addEventListener("mouseleave", () => onHover());
            partGroup.addEventListener("focus", () => onFocus(part.Id));
            partGroup.addEventListener("blur", () => onFocus());
            partGroup.addEventListener("click", () => void onSelect(part.Id!, partGroup));
            partGroup.addEventListener("keydown", event => {
                if (!isSelectionKey(event.key))
                    return;
                event.preventDefault();
                void onSelect(part.Id!, partGroup);
            });
            group.append(partGroup);
        });
        svg.append(group);
    });
}

function renderFallback(target: HTMLElement, modules: ResearchModuleSummary[], onHover: (partId?: string) => void,
    onFocus: (partId?: string) => void, onSelect: (partId: string, source?: HTMLElement) => void) {
    target.replaceChildren();
    modules.forEach((module, index) => {
        const details = document.createElement("details");
        details.className = "cpo-tree-module";
        details.open = index === 0;
        const summary = document.createElement("summary");
        summary.append(el("strong", shortModuleName(module.Name)), el("span", `${module.Parts?.length ?? 0} 个部件`));
        details.append(summary);
        const table = document.createElement("table");
        table.className = "table table-sm cpo-part-table";
        table.innerHTML = "<thead><tr><th>部件</th><th>功能</th><th>研究状态</th></tr></thead>";
        const body = document.createElement("tbody");
        for (const part of module.Parts ?? []) {
            if (!part.Id)
                continue;
            const row = document.createElement("tr");
            const name = document.createElement("td");
            const button = document.createElement("button");
            button.type = "button";
            button.className = "cpo-table-part";
            button.dataset.partId = part.Id;
            button.setAttribute("aria-pressed", "false");
            button.setAttribute("aria-expanded", "false");
            button.textContent = part.Name ?? part.Id;
            button.addEventListener("mouseenter", () => onHover(part.Id));
            button.addEventListener("mouseleave", () => onHover());
            button.addEventListener("focus", () => onFocus(part.Id));
            button.addEventListener("blur", () => onFocus());
            button.addEventListener("click", () => void onSelect(part.Id!, button));
            name.append(button);
            row.append(name, td(part.FunctionSummary), td(part.ResearchStatus));
            body.append(row);
        }
        table.append(body);
        const scroll = el("div", undefined, "table-responsive");
        scroll.append(table);
        details.append(scroll);
        target.append(details);
    });
}

function renderResearch(target: HTMLElement, response: PartResearchResponse, showDetailAction: boolean) {
    target.replaceChildren();
    const part = response.Part;
    const header = el("header", undefined, "cpo-research-header");
    const title = el("h2", part?.Name ?? "未知部件");
    title.id = "cpo-drawer-title";
    title.tabIndex = -1;
    header.append(el("span", part?.Id ?? "", "cpo-stable-id"), title,
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
    target.append(researchItemsSection("关键规格", response.KeySpecifications));
    target.append(namedLinksSection("产业链节点", response.ChainNodes, "尚无产业链节点映射"));
    target.append(namedLinksSection("技术链接", response.Technologies, "尚无技术链接"));
    target.append(companiesSection(response.Companies ?? []));
    target.append(evidenceSection(response.Evidence ?? []));
    target.append(researchItemsSection("研究结论", response.Conclusions));
    target.append(researchItemsSection("风险", response.Risks));
    target.append(messageSection("状态警告", response.StatusWarnings ?? [], "warning"));
    target.append(messageSection("未决问题", response.UnresolvedQuestions ?? [], "question"));
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

function companiesSection(companies: CompanyExposureSummary[]) {
    const section = researchSection(`候选公司 (${companies.length})`);
    if (!companies.length) {
        section.append(el("p", "尚无候选公司映射。不得由图形或部件名称推导供应关系。", "cpo-empty"));
        return section;
    }
    const list = el("div", undefined, "cpo-record-list");
    for (const company of companies) {
        const article = el("article", undefined, "cpo-record");
        const heading = el("div", undefined, "cpo-record-heading");
        const companyLink = document.createElement("a");
        companyLink.href = resolveUrl(`~/Research/Companies/${encodeURIComponent(company.CompanyId ?? "")}`);
        companyLink.textContent = company.CompanyName ?? company.CompanyId ?? "未知公司";
        companyLink.setAttribute("aria-label", `打开公司详情：${company.CompanyName ?? company.CompanyId}`);
        heading.append(companyLink, badge(company.VerificationState ?? "unknown", "verification"));
        article.append(heading,
            el("div", `${company.Role ?? "role unknown"} · relevance ${company.Relevance ?? "unknown"} · confidence ${company.Confidence ?? "unknown"}`, "cpo-record-meta"),
            el("p", company.ScopeNote || "暂无范围说明"));
        list.append(article);
    }
    section.append(list);
    return section;
}

function evidenceSection(evidence: EvidenceSummary[]) {
    const section = researchSection(`证据 (${evidence.length})`);
    if (!evidence.length) {
        section.append(el("p", "尚无直接关联证据。", "cpo-empty"));
        return section;
    }
    const list = el("div", undefined, "cpo-record-list");
    for (const item of evidence) {
        const article = el("article", undefined, "cpo-record");
        const heading = el("div", undefined, "cpo-record-heading");
        heading.append(el("strong", `${item.EvidenceId}@v${item.Version}`), badge(item.ReviewState ?? "unknown", "review"));
        article.append(heading,
            el("div", `Level ${item.SourceLevel ?? "?"} · ${item.Stance ?? "stance unknown"}`, "cpo-record-meta"),
            el("p", item.Proposition || "暂无命题"),
            el("small", `${item.SourceTitle ?? "来源未知"} · ${item.Locator ?? "locator 未记录"}`));
        list.append(article);
    }
    section.append(list);
    return section;
}

function messageSection(title: string, messages: string[], kind: "warning" | "question") {
    const section = researchSection(title);
    const list = document.createElement("ul");
    list.className = `cpo-message-list is-${kind}`;
    if (!messages.length)
        list.append(el("li", "无"));
    else
        messages.forEach(message => list.append(el("li", message)));
    section.append(list);
    return section;
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

function shortModuleName(name?: string) {
    return (name ?? "未命名模块").split("/")[0].trim();
}

function renderCatalogUnavailable(svg: SVGSVGElement, tree: HTMLElement, coverage: HTMLElement | null,
    preview: HTMLElement, title: string, detail: string, kind: "info" | "danger") {
    svg.replaceChildren();
    svg.setAttribute("hidden", "");
    svg.setAttribute("aria-label", title);
    if (coverage)
        coverage.textContent = kind === "info" ? "0 个可研究部件" : "部件目录读取失败";
    replaceChildren(preview, el("strong", title), el("span", detail));
    const alert = el("div", undefined, `alert alert-${kind}`);
    alert.append(el("strong", title), document.createTextNode(`：${detail}`));
    const retry = el("button", "重试", "btn btn-sm btn-outline-secondary ms-2");
    retry.type = "button";
    retry.addEventListener("click", () => window.location.reload());
    alert.append(retry);
    replaceChildren(tree, alert);
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

function td(text?: string) {
    return el("td", text || "—");
}

function svgElement<K extends keyof SVGElementTagNameMap>(tag: K, attributes: Record<string, string> = {}): SVGElementTagNameMap[K] {
    const node = document.createElementNS(svgNs, tag);
    for (const [name, value] of Object.entries(attributes))
        node.setAttribute(name, value);
    return node;
}
