import test from "node:test";
import assert from "node:assert/strict";
import {
    activePartId,
    approvedCpoModuleIds,
    approvedCpoPartCount,
    clearSelection,
    componentCoverageState,
    hoverPart,
    interactionState,
    isSelectionKey,
    layerState,
    lockPart,
    relatedCompanyCountLabel,
    researchEmptyStateText,
    switchExplorerView,
    togglePartSelection
} from "../Modules/Research/Diagram/PartSelectionState.ts";
import {
    LatestRequest,
    RetryablePromiseCache
} from "../Modules/Research/Diagram/ResearchRequestState.ts";

test("approved full CPO taxonomy coverage helper requires all 9 stable module IDs", () => {
    assert.equal(approvedCpoModuleIds.length, 9);
    assert.equal(approvedCpoPartCount, 21);
    assert.deepEqual(componentCoverageState([...approvedCpoModuleIds], [...approvedCpoModuleIds]), {
        missingCatalogIds: [],
        extraRenderedIds: [],
        complete: true
    });
    assert.deepEqual(componentCoverageState(["cpo.mod.pic", "cpo.mod.laser"], ["cpo.mod.pic", "unexpected"]), {
        missingCatalogIds: ["cpo.mod.laser"],
        extraRenderedIds: ["unexpected"],
        complete: false
    });
});

test("hover focuses the SiPh PIC slice without selecting it", () => {
    const state = hoverPart({ viewMode: "three" }, "cpo.mod.pic");
    assert.equal(activePartId(state), "cpo.mod.pic");
    assert.equal(state.selectedId, undefined);
    assert.equal(interactionState(state, "cpo.mod.pic"), "hovered");
    assert.equal(interactionState(state, "cpo.mod.host-asic"), "dimmed");
});

test("click selection locks and same-object click resets while preserving view", () => {
    let state = togglePartSelection({ viewMode: "flat" }, "cpo.mod.pic");
    assert.equal(activePartId(state), "cpo.mod.pic");
    assert.equal(state.selectedId, "cpo.mod.pic");
    assert.equal(interactionState(state, "cpo.mod.pic"), "active");

    state = hoverPart(state, undefined);
    assert.equal(activePartId(state), "cpo.mod.pic");

    state = togglePartSelection(state, "cpo.mod.pic");
    assert.equal(state.selectedId, undefined);
    assert.equal(state.hoveredId, undefined);
    assert.equal(state.viewMode, "flat");
});

test("view switch preserves locked selection and reset preserves current view", () => {
    let state = lockPart({ viewMode: "three" }, "cpo.mod.pic");
    state = switchExplorerView(state, "flat");
    assert.equal(state.selectedId, "cpo.mod.pic");
    assert.equal(activePartId(state), "cpo.mod.pic");
    assert.equal(state.viewMode, "flat");
    assert.deepEqual(clearSelection(state), { viewMode: "flat" });
});

test("Enter and Space are keyboard selection keys", () => {
    assert.equal(isSelectionKey("Enter"), true);
    assert.equal(isSelectionKey(" "), true);
    assert.equal(isSelectionKey("Spacebar"), true);
    assert.equal(isSelectionKey("Escape"), false);
});

test("module layer helper still marks unrelated layers dimmed", () => {
    assert.equal(layerState("cpo.mod.pic", "cpo.mod.pic"), "active");
    assert.equal(layerState("cpo.mod.thermal", "cpo.mod.pic"), "dimmed");
    assert.equal(layerState("cpo.mod.pic", undefined), "normal");
});

test("research retrieval failure is rendered as unknown instead of confirmed empty", () => {
    assert.equal(researchEmptyStateText(false, "尚无技术链接", "读取失败，未知"), "尚无技术链接");
    assert.equal(researchEmptyStateText(true, "尚无技术链接", "读取失败，未知"), "读取失败，未知");
    assert.equal(relatedCompanyCountLabel(0, false), "0");
    assert.equal(relatedCompanyCountLabel(0, true), "unknown");
    assert.equal(relatedCompanyCountLabel(2, true), "2");
});

test("only the latest drawer request may update UI state", () => {
    const requests = new LatestRequest();
    const first = requests.begin();
    const second = requests.begin();
    assert.equal(requests.isCurrent(first), false);
    assert.equal(requests.isCurrent(second), true);
    requests.cancel();
    assert.equal(requests.isCurrent(second), false);
});

test("failed research requests are evicted and can be retried", async () => {
    let attempts = 0;
    const cache = new RetryablePromiseCache(async key => {
        attempts++;
        if (attempts === 1)
            throw new Error(`temporary ${key}`);
        return `resolved ${key}`;
    });

    await assert.rejects(cache.get("part-a"), /temporary part-a/);
    assert.equal(await cache.get("part-a"), "resolved part-a");
    assert.equal(attempts, 2);
});
