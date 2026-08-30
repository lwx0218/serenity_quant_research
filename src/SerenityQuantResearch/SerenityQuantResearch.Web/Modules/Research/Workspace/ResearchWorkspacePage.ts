import { notifyError } from "@serenity-is/corelib";
import { ResearchWorkspaceService } from "../../ServerTypes/Research/ResearchWorkspaceService";
import type { ResearchSectionSummary } from "../../ServerTypes/Research/Services.ResearchSectionSummary";
import type { ResearchWorkspaceRequest } from "../../ServerTypes/Research/Services.ResearchWorkspaceRequest";
import type { ResearchWorkspaceResponse } from "../../ServerTypes/Research/Services.ResearchWorkspaceResponse";
import type { WorkspaceBacklink } from "../../ServerTypes/Research/Services.WorkspaceBacklink";
import type { WorkspaceEvidenceContext } from "../../ServerTypes/Research/Services.WorkspaceEvidenceContext";
import type { WorkspaceObjectSummary } from "../../ServerTypes/Research/Services.WorkspaceObjectSummary";
import type { WorkspaceTreeGroup } from "../../ServerTypes/Research/Services.WorkspaceTreeGroup";
import "./ResearchWorkspacePage.css";
import { readWorkspaceContext, workspaceHref, workspaceStateLabel, type WorkspaceSourceContext } from "./ResearchWorkspaceState";

export default async function pageInit() {
    const app = document.querySelector<HTMLElement>("#research-workspace-app");
    if (!app)
        return;

    try {
        app.setAttribute("aria-busy", "true");
        const context = readWorkspaceContext(location.search);
        const response = await ResearchWorkspaceService.Retrieve(toRequest(context));
        renderWorkspace(app, response, context);
        document.title = `${response.CurrentObject?.Name ?? "Research Workspace"} - Research Workspace`;
    }
    catch (error) {
        notifyError(error as any);
        app.replaceChildren(errorBlock("Unable to load the read-only Workspace projection.", error));
    }
    finally {
        app.removeAttribute("aria-busy");
    }
}

function toRequest(context: WorkspaceSourceContext): ResearchWorkspaceRequest {
    return {
        ObjectType: context.objectType,
        ObjectId: context.objectId,
        Source: context.source,
        ComponentId: context.componentId,
        PartId: context.partId,
        ChainNodeId: context.chainNodeId,
        CompanyId: context.companyId,
        View: context.view
    };
}

function renderWorkspace(app: HTMLElement, response: ResearchWorkspaceResponse, context: WorkspaceSourceContext) {
    app.dataset.objectType = response.CurrentObject?.ObjectType ?? context.objectType;
    app.dataset.objectId = response.CurrentObject?.Id ?? context.objectId;
    app.dataset.readOnly = response.IsReadOnly ? "true" : "false";
    app.replaceChildren(renderTree(response.Tree ?? [], response.CurrentObject, context), renderCurrent(response), renderContext(response, context));
}

function renderTree(groups: WorkspaceTreeGroup[], current: WorkspaceObjectSummary | undefined, context: WorkspaceSourceContext) {
    const aside = el("aside", undefined, "workspace-tree");
    aside.setAttribute("aria-label", "Research object tree");
    aside.append(el("div", "Existing object tree", "workspace-kicker"));
    for (const group of groups) {
        const section = el("section", undefined, "workspace-tree-group");
        section.append(el("h2", group.Name ?? "Objects"));
        for (const item of group.Items ?? []) {
            const link = document.createElement("a");
            link.className = "workspace-tree-item";
            if (item.Id === current?.Id && item.ObjectType === current.ObjectType)
                link.classList.add("is-active");
            link.href = workspaceHref(item.ObjectType as any, item.Id ?? "", context);
            link.dataset.workspaceObject = item.ObjectType ?? "unknown";
            link.dataset.workspaceObjectId = item.Id ?? "";
            link.append(el("span", item.Name ?? item.Id ?? "Unknown object"), el("small", item.Id ?? "Unknown"));
            section.append(link);
        }
        aside.append(section);
    }
    return aside;
}

function renderCurrent(response: ResearchWorkspaceResponse) {
    const article = el("article", undefined, "workspace-current-object");
    const current = response.CurrentObject;
    const header = el("header", undefined, "workspace-object-header");
    header.append(el("span", current?.ObjectType ?? "object", "workspace-eyebrow"), el("h2", current?.Name ?? "Unknown research object"));
    header.append(el("p", current?.Subtitle ?? current?.Id ?? "No subtitle", "workspace-subtitle"));
    const meta = el("dl", undefined, "workspace-meta-grid");
    appendDefinition(meta, "Stable ID", current?.Id ?? "Unknown");
    appendDefinition(meta, "State", workspaceStateLabel(current?.State));
    appendDefinition(meta, "Mode", response.IsReadOnly ? "Read-only projection" : "Unknown");
    header.append(meta);
    article.append(header);

    const understanding = section("Current understanding");
    understanding.append(el("p", current?.Description || "Unknown; current data does not provide a sourced description."));
    understanding.append(callout("Read-only boundary", "This Workspace only projects existing rows and derived relationships. It does not create notes, questions, backlinks, graph data, or write endpoints."));
    article.append(understanding);

    article.append(objectListSection("Linked objects", response.LinkedObjects ?? [], "No existing linked objects are available; this is a gap, not a conclusion."));
    article.append(evidenceSection(response.Evidence ?? []));
    article.append(sectionsBlock("Existing conclusions", response.Conclusions ?? [], "No existing conclusion resolves through this object's evidence relationships."));
    article.append(sectionsBlock("Read-only gaps / unresolved questions", response.Gaps ?? [], "No derived gaps were returned."));
    return article;
}

function renderContext(response: ResearchWorkspaceResponse, context: WorkspaceSourceContext) {
    const aside = el("aside", undefined, "workspace-context");
    aside.setAttribute("aria-label", "Linked objects and derived backlinks");
    const path = section("Source context");
    path.append(el("p", (response.SourcePath ?? []).join(" → ") || "Research Workspace", "workspace-path"));
    aside.append(path);
    aside.append(backlinkSection(response.Backlinks ?? [], context));
    aside.append(sectionsBlock("Evidence / status context", response.Status ?? [], "Status Unknown"));
    const safety = section("Safety boundary");
    safety.append(el("p", "Unsupported values remain Unknown / Not reviewed / Candidate or are omitted. Candidate and draft records are never shown as verified conclusions."));
    aside.append(safety);
    return aside;
}

function objectListSection(title: string, items: WorkspaceObjectSummary[], emptyText: string) {
    const block = section(title);
    const list = el("div", undefined, "workspace-linked-list");
    if (!items.length)
        list.append(empty(emptyText));
    for (const item of uniqueObjects(items)) {
        const link = document.createElement("a");
        link.href = workspaceHref(item.ObjectType as any, item.Id ?? "", currentContext());
        link.className = "workspace-linked-object";
        link.dataset.workspaceLinkedObject = item.ObjectType ?? "unknown";
        link.dataset.workspaceLinkedObjectId = item.Id ?? "";
        link.append(el("strong", item.Name ?? item.Id ?? "Unknown"), el("span", `${item.ObjectType ?? "object"} · ${workspaceStateLabel(item.State)}`), el("small", item.Description ?? item.Subtitle ?? ""));
        list.append(link);
    }
    block.append(list);
    return block;
}

function evidenceSection(items: WorkspaceEvidenceContext[]) {
    const block = section("Evidence context");
    if (!items.length) {
        block.append(empty("No explicit evidence link is available. Absence is an unresolved research gap."));
        return block;
    }
    const list = el("div", undefined, "workspace-evidence-list");
    for (const item of items) {
        const card = el("article", undefined, "workspace-evidence-card");
        card.append(el("strong", `${item.EvidenceId}@v${item.Version}`), badge(workspaceStateLabel(item.ReviewState)), el("p", item.Proposition ?? "Unknown proposition"), el("small", `${item.Stance ?? "Unknown stance"} · Level ${item.SourceLevel ?? "Unknown"} · ${item.SourceTitle ?? "Unknown source"} · ${item.Locator ?? "locator Unknown"}`));
        list.append(card);
    }
    block.append(list);
    return block;
}

function backlinkSection(items: WorkspaceBacklink[], context: WorkspaceSourceContext) {
    const block = section("Derived relationship context");
    if (!items.length) {
        block.append(empty("No derived backlinks are available from existing relationships."));
        return block;
    }
    const list = el("div", undefined, "workspace-backlink-list");
    for (const item of items) {
        const backlink = item.ObjectType === "evidence"
            ? document.createElement("article")
            : document.createElement("a");
        backlink.className = "workspace-backlink";
        if (backlink instanceof HTMLAnchorElement)
            backlink.href = workspaceHref(item.ObjectType as any, item.ObjectId ?? "", context);
        else
            backlink.setAttribute("aria-label", "Read-only evidence context; no evidence detail route exists in Workspace v1");
        backlink.dataset.workspaceBacklink = item.ObjectType ?? "unknown";
        backlink.dataset.workspaceBacklinkId = item.ObjectId ?? "";
        backlink.append(el("strong", item.Label ?? item.ObjectId ?? "Unknown backlink"), el("span", item.Context ?? "Derived from existing relationships."), badge(workspaceStateLabel(item.State)));
        list.append(backlink);
    }
    block.append(list);
    return block;
}

function sectionsBlock(title: string, items: ResearchSectionSummary[], emptyText: string) {
    const block = section(title);
    if (!items.length) {
        block.append(empty(emptyText));
        return block;
    }
    const list = document.createElement("ul");
    list.className = "workspace-section-list";
    for (const item of items) {
        const row = document.createElement("li");
        row.append(badge(workspaceStateLabel(item.State)), document.createTextNode(item.Text ?? "Unknown"));
        list.append(row);
    }
    block.append(list);
    return block;
}

function currentContext(): WorkspaceSourceContext {
    return readWorkspaceContext(location.search);
}

function uniqueObjects(items: WorkspaceObjectSummary[]) {
    const seen = new Set<string>();
    return items.filter(item => {
        const key = `${item.ObjectType}:${item.Id}`;
        if (seen.has(key))
            return false;
        seen.add(key);
        return true;
    });
}

function section(title: string) {
    const node = el("section", undefined, "workspace-section");
    node.append(el("h3", title));
    return node;
}

function callout(title: string, text: string) {
    const node = el("div", undefined, "workspace-callout");
    node.append(el("strong", title), el("p", text));
    return node;
}

function badge(text: string) {
    return el("span", text, "workspace-badge");
}

function empty(text: string) {
    return el("p", text, "workspace-empty");
}

function appendDefinition(list: HTMLElement, term: string, value?: string) {
    list.append(el("dt", term), el("dd", value || "Unknown"));
}

function errorBlock(message: string, error: unknown) {
    const node = el("section", undefined, "workspace-error");
    node.append(el("h2", message), el("pre", String((error as any)?.message ?? error ?? "Unknown error")));
    return node;
}

function el<K extends keyof HTMLElementTagNameMap>(tag: K, text?: string, className?: string): HTMLElementTagNameMap[K] {
    const node = document.createElement(tag);
    if (className)
        node.className = className;
    if (text !== undefined)
        node.textContent = text;
    return node;
}
