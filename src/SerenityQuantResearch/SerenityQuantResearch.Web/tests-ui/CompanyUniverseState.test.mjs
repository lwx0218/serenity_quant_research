import test from "node:test";
import assert from "node:assert/strict";
import {
    compareText,
    companyBrowseViews,
    defaultCompanyBrowseView,
    isCompanyBrowseView,
    meaningfulStateLabel,
    normalizeCompanyFilters,
    stateTrustTone
} from "../Modules/Research/Company/CompanyUniverseState.ts";

test("R5 Company Pool defaults to card browse with list as the only peer view", () => {
    assert.equal(defaultCompanyBrowseView, "card");
    assert.deepEqual(companyBrowseViews, ["card", "list"]);
    assert.equal(isCompanyBrowseView("card"), true);
    assert.equal(isCompanyBrowseView("list"), true);
    assert.equal(isCompanyBrowseView("grid"), false);
    assert.equal(isCompanyBrowseView("comparison"), false);
});

test("company filter request preserves lightweight relationship dimensions and trims values", () => {
    const request = normalizeCompanyFilters([
        ["SearchText", "  nvidia  "],
        ["PartId", " cpo.part.host-asic.switch-die "],
        ["ChainNodeId", ""],
        ["Role", " chip_vendor "],
        ["CountryRegion", " US "],
        ["VerificationState", "candidate"]
    ]);
    assert.deepEqual(request, {
        SearchText: "nvidia",
        PartId: "cpo.part.host-asic.switch-die",
        ChainNodeId: "",
        Role: "chip_vendor",
        CountryRegion: "US",
        VerificationState: "candidate"
    });
});

test("Explorer source defaults apply only when the visible filter is empty", () => {
    const request = normalizeCompanyFilters([
        ["PartId", ""],
        ["ChainNodeId", "cpo.chain.pic"]
    ], {
        PartId: "cpo.part.pic.modulator",
        ChainNodeId: "cpo.chain.laser"
    });
    assert.equal(request.PartId, "cpo.part.pic.modulator");
    assert.equal(request.ChainNodeId, "cpo.chain.pic");
});

test("candidate, draft and unknown labels explicitly remain unverified and unreviewed", () => {
    assert.match(meaningfulStateLabel("candidate"), /未核验/);
    assert.match(meaningfulStateLabel("discovery"), /未核验/);
    assert.match(meaningfulStateLabel("draft"), /未审核/);
    assert.match(meaningfulStateLabel("unknown"), /不可视为已核验/);
    assert.match(meaningfulStateLabel(), /不可视为已核验/);
    assert.equal(stateTrustTone("candidate"), "unverified");
    assert.equal(stateTrustTone("draft"), "unverified");
    assert.equal(stateTrustTone("unknown"), "unverified");
    assert.equal(stateTrustTone("verified"), "verified");
    assert.notEqual(meaningfulStateLabel("candidate"), meaningfulStateLabel("verified"));
});

test("identity sorting is deterministic and has no market-performance input", () => {
    assert.ok(compareText("300308", "688498", true) < 0);
    assert.ok(compareText("中际旭创", "英伟达", false) !== 0);
});
