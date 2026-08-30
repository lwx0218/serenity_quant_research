import test from "node:test";
import assert from "node:assert/strict";
import {
    isForbiddenWorkspaceControlLabel,
    normalizeWorkspaceObjectType,
    readWorkspaceContext,
    workspaceHref,
    workspaceStateLabel
} from "../Modules/Research/Workspace/ResearchWorkspaceState.ts";

test("R6 Workspace URL context preserves Explorer component and selected part", () => {
    const context = readWorkspaceContext("?objectType=part&source=cpo-explorer&componentId=cpo.mod.host-asic&partId=cpo.part.host-asic.switch-die&chainNodeId=cpo.chain.asic&view=list");
    assert.equal(context.objectType, "part");
    assert.equal(context.objectId, "cpo.part.host-asic.switch-die");
    assert.equal(context.source, "cpo-explorer");
    assert.equal(context.componentId, "cpo.mod.host-asic");
    assert.equal(context.partId, "cpo.part.host-asic.switch-die");
    assert.equal(context.chainNodeId, "cpo.chain.asic");
    assert.equal(context.view, "list");
});

test("R6 Workspace URL context opens company object from Company Detail", () => {
    const context = readWorkspaceContext("?objectType=company&companyId=global.broadcom&source=company-detail&componentId=cpo.mod.host-asic&partId=cpo.part.host-asic.switch-die");
    assert.equal(context.objectType, "company");
    assert.equal(context.objectId, "global.broadcom");
    assert.equal(context.companyId, "global.broadcom");
    assert.equal(context.source, "company-detail");
});

test("Workspace href builder keeps object identity plus source context", () => {
    const href = workspaceHref("company", "global.broadcom", {
        source: "cpo-explorer",
        componentId: "cpo.mod.host-asic",
        partId: "cpo.part.host-asic.switch-die",
        chainNodeId: "cpo.chain.asic"
    });
    assert.match(href, /\/Research\/Workspace\?/);
    assert.match(href, /objectType=company/);
    assert.match(href, /companyId=global.broadcom/);
    assert.match(href, /componentId=cpo.mod.host-asic/);
    assert.match(href, /partId=cpo.part.host-asic.switch-die/);
    assert.match(href, /chainNodeId=cpo.chain.asic/);
});

test("Workspace state labels keep unsupported values unverified or unreviewed", () => {
    assert.match(workspaceStateLabel("Candidate"), /候选/);
    assert.match(workspaceStateLabel("draft"), /Not reviewed|未审核/);
    assert.match(workspaceStateLabel("none"), /无结论/);
    assert.match(workspaceStateLabel(undefined), /Unknown|不可视为已核验/);
    assert.equal(normalizeWorkspaceObjectType("module"), "component");
    assert.equal(normalizeWorkspaceObjectType("note"), undefined);
});

test("Workspace forbidden-control guard covers deferred writing and graph concepts", () => {
    for (const label of ["Graph", "New Note", "ResearchNote", "OpenQuestion", "Backlink", "Save", "Create", "Publish", "Assign", "Resolve"])
        assert.equal(isForbiddenWorkspaceControlLabel(label), true, label);
    assert.equal(isForbiddenWorkspaceControlLabel("Open in Research Workspace"), false);
    assert.equal(isForbiddenWorkspaceControlLabel("Derived relationship context"), false);
});
