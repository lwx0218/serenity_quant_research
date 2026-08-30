export const companyBrowseViews = ["card", "list"] as const;
export type CompanyBrowseView = typeof companyBrowseViews[number];
export const defaultCompanyBrowseView: CompanyBrowseView = "card";

const stateLabels: Record<string, string> = {
    discovery: "Discovery / 发现线索（未核验）",
    candidate: "Candidate / 候选（未核验）",
    verified: "Verified / 已核验",
    rejected: "Rejected / 已否定（保留审计）",
    stale: "Stale / 已过期（待复核）",
    unmapped: "Research gap / 尚无暴露记录",
    draft: "Draft / 草稿（未审核）",
    in_review: "In review / 人工审核中",
    reviewed: "Reviewed / 已审核",
    superseded: "Superseded / 已取代",
    none: "None / 无证据覆盖",
    unreviewed: "Unreviewed only / 仅未审核证据",
    mixed: "Mixed / 审核状态混合",
    fresh: "Fresh / 180 天内捕获",
    review_due: "Review due / 需复核",
    historical: "Historical fact / 历史事实（不自动失效）",
    unknown: "Unknown / 未知（不可视为已核验）"
};

const unverifiedStates = new Set(["discovery", "candidate", "draft", "in_review", "unknown", "unmapped", "none", "unreviewed", "mixed"]);
const verifiedStates = new Set(["verified", "reviewed"]);
const rejectedStates = new Set(["rejected", "stale", "superseded"]);

export function meaningfulStateLabel(state?: string): string {
    if (!state)
        return "Unknown / 未记录（不可视为已核验）";
    return stateLabels[state] ?? state.replaceAll("_", " ");
}

export function stateTrustTone(state?: string): "verified" | "unverified" | "rejected" | "neutral" {
    if (!state)
        return "unverified";
    if (verifiedStates.has(state))
        return "verified";
    if (rejectedStates.has(state))
        return "rejected";
    if (unverifiedStates.has(state))
        return "unverified";
    return "neutral";
}

export function isCompanyBrowseView(value?: string): value is CompanyBrowseView {
    return companyBrowseViews.includes(value as CompanyBrowseView);
}

export function normalizeCompanyFilters(
    entries: Iterable<[string, FormDataEntryValue]>,
    defaults: Partial<Record<string, string | undefined>> = {}
): Record<string, string> {
    const request: Record<string, string> = {};
    for (const [key, value] of entries)
        request[key] = String(value).trim();
    for (const [key, value] of Object.entries(defaults)) {
        if (value && !request[key])
            request[key] = value;
    }
    return request;
}

export function compareText(left?: string, right?: string, ascending = true): number {
    const result = (left ?? "").localeCompare(right ?? "", "zh-CN", { numeric: true, sensitivity: "base" });
    return ascending ? result : -result;
}
