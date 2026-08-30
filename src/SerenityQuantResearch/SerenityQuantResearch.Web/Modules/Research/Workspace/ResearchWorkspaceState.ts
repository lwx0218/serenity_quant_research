export type WorkspaceObjectType = "component" | "part" | "company" | "technology" | "chainNode";

export interface WorkspaceSourceContext {
    objectType: WorkspaceObjectType;
    objectId: string;
    source?: string;
    componentId?: string;
    partId?: string;
    chainNodeId?: string;
    companyId?: string;
    view?: string;
}

export function normalizeWorkspaceObjectType(value?: string | null): WorkspaceObjectType | undefined {
    switch (value) {
        case "component":
        case "module":
            return "component";
        case "part":
            return "part";
        case "company":
            return "company";
        case "technology":
        case "tech":
            return "technology";
        case "chainNode":
        case "chain":
        case "node":
            return "chainNode";
        default:
            return undefined;
    }
}

export function readWorkspaceContext(search: string): WorkspaceSourceContext {
    const params = new URLSearchParams(search);
    const explicitType = normalizeWorkspaceObjectType(params.get("objectType") || params.get("ObjectType"));
    const companyId = params.get("companyId") || params.get("CompanyId") || undefined;
    const partId = params.get("partId") || params.get("PartId") || undefined;
    const componentId = params.get("componentId") || params.get("ComponentId") || undefined;
    const chainNodeId = params.get("chainNodeId") || params.get("ChainNodeId") || undefined;
    const objectType = explicitType ?? (companyId ? "company" : partId ? "part" : chainNodeId ? "chainNode" : "component");
    const objectId = params.get("objectId") || params.get("ObjectId") ||
        (objectType === "company" ? companyId : objectType === "part" ? partId : objectType === "chainNode" ? chainNodeId : componentId) || "cpo.mod.pic";
    return {
        objectType,
        objectId,
        source: params.get("source") || undefined,
        componentId,
        partId,
        chainNodeId,
        companyId,
        view: params.get("view") || undefined
    };
}

export function workspaceHref(objectType: WorkspaceObjectType, objectId: string, context?: Partial<WorkspaceSourceContext>) {
    const params = new URLSearchParams();
    params.set("objectType", objectType);
    params.set("objectId", objectId);
    if (objectType === "component")
        params.set("componentId", objectId);
    if (objectType === "part")
        params.set("partId", objectId);
    if (objectType === "company")
        params.set("companyId", objectId);
    if (objectType === "chainNode")
        params.set("chainNodeId", objectId);
    for (const [key, value] of Object.entries(context ?? {})) {
        if (value && !params.has(key))
            params.set(key, String(value));
    }
    return `/Research/Workspace?${params.toString()}`;
}

export function workspaceStateLabel(state?: string | null) {
    const value = (state || "unknown").toLowerCase();
    switch (value) {
        case "verified":
        case "reviewed":
        case "published":
            return `${state} / reviewed state`;
        case "candidate":
        case "discovery":
            return "Candidate / 候选（未核验）";
        case "draft":
        case "in_review":
            return `${state} / Not reviewed（未审核）`;
        case "none":
            return "None / 无结论";
        default:
            return `${state || "Unknown"} / Unknown（不可视为已核验）`;
    }
}

export function isForbiddenWorkspaceControlLabel(value: string) {
    return /\b(Graph|New Note|ResearchNote|OpenQuestion|Backlink|Save|Create|Publish|Assign|Resolve)\b/i.test(value);
}
