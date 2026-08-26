export const companyTabs = [
    "overview",
    "exposure",
    "financial",
    "capex",
    "events",
    "conclusions",
    "sources"
] as const;

export type CompanyTab = typeof companyTabs[number];

export const companyTabLabels: Record<CompanyTab, string> = {
    overview: "Overview",
    exposure: "Industry-chain Exposure",
    financial: "Earnings & Financial Evidence",
    capex: "Capex & Investment",
    events: "Events",
    conclusions: "Research Conclusions",
    sources: "Sources & Audit"
};

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
    unknown: "Unknown / 无可用时间数据"
};

export function meaningfulStateLabel(state?: string): string {
    if (!state)
        return "Unknown / 未记录";
    return stateLabels[state] ?? state.replaceAll("_", " ");
}

export function nextTab(current: CompanyTab, key: string): CompanyTab {
    const index = companyTabs.indexOf(current);
    if (key === "Home")
        return companyTabs[0];
    if (key === "End")
        return companyTabs[companyTabs.length - 1];
    if (key === "ArrowRight" || key === "ArrowDown")
        return companyTabs[(index + 1) % companyTabs.length];
    if (key === "ArrowLeft" || key === "ArrowUp")
        return companyTabs[(index - 1 + companyTabs.length) % companyTabs.length];
    return current;
}

export function toggleComparison(selected: readonly string[], companyId: string, limit = 5): string[] {
    if (selected.includes(companyId))
        return selected.filter(id => id !== companyId);
    if (selected.length >= limit)
        return [...selected];
    return [...selected, companyId];
}

export function normalizeCompanyFilters(entries: Iterable<[string, FormDataEntryValue]>): Record<string, string> {
    const request: Record<string, string> = {};
    for (const [key, value] of entries)
        request[key] = String(value).trim();
    return request;
}

export function compareText(left?: string, right?: string, ascending = true): number {
    const result = (left ?? "").localeCompare(right ?? "", "zh-CN", { numeric: true, sensitivity: "base" });
    return ascending ? result : -result;
}
