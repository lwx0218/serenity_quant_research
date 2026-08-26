import test from "node:test";
import assert from "node:assert/strict";
import {
    compareText,
    companyTabLabels,
    companyTabs,
    meaningfulStateLabel,
    nextTab,
    normalizeCompanyFilters,
    toggleComparison
} from "../Modules/Research/Company/CompanyUniverseState.ts";

test("company filter request preserves explicit relationship dimensions and trims values", () => {
    const request = normalizeCompanyFilters([
        ["PartId", " cpo.part.host-asic.switch-die "],
        ["ChainNodeId", "cpo.chain.asic"],
        ["VerificationState", "candidate"],
        ["EvidenceCoverage", "unreviewed"],
        ["Freshness", "fresh"]
    ]);
    assert.deepEqual(request, {
        PartId: "cpo.part.host-asic.switch-die",
        ChainNodeId: "cpo.chain.asic",
        VerificationState: "candidate",
        EvidenceCoverage: "unreviewed",
        Freshness: "fresh"
    });
});

test("comparison selection toggles by stable company ID and remains bounded", () => {
    let selected = [];
    for (const id of ["global.nvidia", "global.broadcom", "global.cisco", "global.intel", "global.marvell"])
        selected = toggleComparison(selected, id);
    assert.equal(selected.length, 5);
    assert.deepEqual(toggleComparison(selected, "global.arista"), selected);
    selected = toggleComparison(selected, "global.broadcom");
    assert.equal(selected.includes("global.broadcom"), false);
    assert.equal(toggleComparison(selected, "global.arista").includes("global.arista"), true);
});

test("all seven frozen company detail tabs support cyclic arrow, Home and End navigation", () => {
    assert.equal(companyTabs.length, 7);
    assert.deepEqual(Object.values(companyTabLabels), [
        "Overview",
        "Industry-chain Exposure",
        "Earnings & Financial Evidence",
        "Capex & Investment",
        "Events",
        "Research Conclusions",
        "Sources & Audit"
    ]);
    assert.equal(nextTab("overview", "ArrowRight"), "exposure");
    assert.equal(nextTab("overview", "ArrowLeft"), "sources");
    assert.equal(nextTab("capex", "Home"), "overview");
    assert.equal(nextTab("capex", "End"), "sources");
});

test("candidate and draft labels explicitly remain unverified and unreviewed", () => {
    assert.match(meaningfulStateLabel("candidate"), /未核验/);
    assert.match(meaningfulStateLabel("discovery"), /未核验/);
    assert.match(meaningfulStateLabel("draft"), /未审核/);
    assert.match(meaningfulStateLabel("rejected"), /保留审计/);
    assert.notEqual(meaningfulStateLabel("candidate"), meaningfulStateLabel("verified"));
});

test("identity sorting is deterministic and has no market-performance input", () => {
    assert.ok(compareText("300308", "688498", true) < 0);
    assert.ok(compareText("中际旭创", "英伟达", false) !== 0);
});
