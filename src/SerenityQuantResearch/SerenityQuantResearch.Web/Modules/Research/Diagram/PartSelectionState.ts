export type ExplorerViewMode = "flat" | "three";

export interface PartSelectionState {
    hoveredId?: string;
    selectedId?: string;
    viewMode?: ExplorerViewMode;
}

export function hoverPart(state: PartSelectionState, partId?: string): PartSelectionState {
    return { ...state, hoveredId: partId };
}

export function lockPart(state: PartSelectionState, partId: string): PartSelectionState {
    return { ...state, hoveredId: undefined, selectedId: partId };
}

export function togglePartSelection(state: PartSelectionState, partId: string): PartSelectionState {
    if (state.selectedId === partId)
        return { ...state, hoveredId: undefined, selectedId: undefined };

    return lockPart(state, partId);
}

export function clearSelection(state: PartSelectionState): PartSelectionState {
    return { viewMode: state.viewMode };
}

export function switchExplorerView(state: PartSelectionState, viewMode: ExplorerViewMode): PartSelectionState {
    return { ...state, viewMode };
}

export function activePartId(state: PartSelectionState): string | undefined {
    return state.selectedId ?? state.hoveredId;
}

export function isSelectionKey(key: string): boolean {
    return key === "Enter" || key === " " || key === "Spacebar";
}

export function interactionState(state: PartSelectionState, partId: string): "active" | "hovered" | "dimmed" | "normal" {
    if (state.selectedId === partId)
        return "active";

    if (!state.selectedId && state.hoveredId === partId)
        return "hovered";

    if (activePartId(state))
        return "dimmed";

    return "normal";
}

export function layerState(moduleId: string, activeModuleId?: string): "normal" | "active" | "dimmed" {
    if (!activeModuleId)
        return "normal";
    return moduleId === activeModuleId ? "active" : "dimmed";
}

export function researchEmptyStateText(hasRetrievalFailure: boolean, confirmedEmptyText: string, unknownText: string): string {
    return hasRetrievalFailure ? unknownText : confirmedEmptyText;
}

export function relatedCompanyCountLabel(count: number, hasRetrievalFailure: boolean): string {
    return hasRetrievalFailure && count === 0 ? "unknown" : String(count);
}
