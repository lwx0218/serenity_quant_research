import test from "node:test";
import assert from "node:assert/strict";
import {
    activePartId,
    clearSelection,
    hoverPart,
    isSelectionKey,
    layerState,
    lockPart
} from "../Modules/Research/Diagram/PartSelectionState.ts";
import {
    LatestRequest,
    RetryablePromiseCache
} from "../Modules/Research/Diagram/ResearchRequestState.ts";

test("hover previews a part and dims unrelated module layers", () => {
    const state = hoverPart({}, "cpo.part.pic.modulator");
    assert.equal(activePartId(state), "cpo.part.pic.modulator");
    assert.equal(layerState("cpo.mod.pic", "cpo.mod.pic"), "active");
    assert.equal(layerState("cpo.mod.thermal", "cpo.mod.pic"), "dimmed");
});

test("click lock survives pointer leave until explicitly cleared", () => {
    let state = lockPart({}, "cpo.part.host-asic.switch-die");
    state = hoverPart(state, undefined);
    assert.equal(activePartId(state), "cpo.part.host-asic.switch-die");
    assert.equal(state.selectedId, "cpo.part.host-asic.switch-die");
    assert.deepEqual(clearSelection(state), {});
});

test("Enter and Space are keyboard selection keys", () => {
    assert.equal(isSelectionKey("Enter"), true);
    assert.equal(isSelectionKey(" "), true);
    assert.equal(isSelectionKey("Spacebar"), true);
    assert.equal(isSelectionKey("Escape"), false);
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
