export interface PartSelectionState {
    hoveredId?: string;
    selectedId?: string;
}

export function hoverPart(state: PartSelectionState, partId?: string): PartSelectionState {
    return { ...state, hoveredId: partId };
}

export function lockPart(state: PartSelectionState, partId: string): PartSelectionState {
    return { hoveredId: partId, selectedId: partId };
}

export function clearSelection(state: PartSelectionState): PartSelectionState {
    return {};
}

export function activePartId(state: PartSelectionState): string | undefined {
    return state.selectedId ?? state.hoveredId;
}

export function isSelectionKey(key: string): boolean {
    return key === "Enter" || key === " " || key === "Spacebar";
}

export function layerState(moduleId: string, activeModuleId?: string): "normal" | "active" | "dimmed" {
    if (!activeModuleId)
        return "normal";
    return moduleId === activeModuleId ? "active" : "dimmed";
}
