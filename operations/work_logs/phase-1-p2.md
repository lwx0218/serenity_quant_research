# Phase 1 P2 Work Log — Interactive SVG and Part Research UI

## Status

- Date: 2026-08-24
- Route: continue existing `plan`
- Result: completed and independently reviewed (`approved with minor findings`)
- P3 status: ready but not started

## Implemented

### Data-driven CPO composition

- Added an original abstract 3×3 system-board composition under `Modules/Research/Diagram/`.
- Geometry is generated presentation data; it contains no company, chain, technology, or evidence relationship.
- No JPEG, extracted pixel, traced geometry, static hotspot map, or runtime image dependency is shipped.
- `PartResearchService.ListParts` reads the nine modules and all 21 parts from the database.
- Each rendered SVG part group uses its stable domain key as `data-part-id`.
- The same service catalog drives the tree/table fallback, so visual and non-pointer paths cannot silently diverge from the seeded parts.

### Selection and accessibility

- Hover and keyboard focus highlight the active part and dim unrelated module layers.
- Click, Enter, and Space lock a part selection and open its research drawer.
- Escape, the close button, and the clear-lock button release selection.
- SVG part groups expose `role=button`, `tabindex=0`, accessible labels, pressed state, and focus styling.
- The table/tree fallback exposes every seeded part as a native button.

### Research drawer and detail

- Drawer and detail requests use `PartResearchService.RetrieveCompleteChain`; no relationship is parsed from SVG.
- Content includes part function, physical module, explicit boundaries, upstream/downstream gap state, key-specification gap state, industry-chain nodes, technology links, candidate companies and verification state, evidence and review state, conclusion gap state, risks, status warnings, and unresolved questions.
- Empty/unverified sections are shown as explicit research gaps rather than inferred facts.
- The seeded Broadcom exposure remains `candidate`; `EVD-2026-0001@v1` remains `draft`.
- Added full detail navigation at `/Research/Parts/{partId}` and a navigation entry at `/Research/Cpo`.

### Independent-review remediation

- Resolved H-01 by adding every frozen drawer/detail section to the service contract and both render paths without inventing product facts.
- Resolved M-01 with latest-request generation guards and retryable promise caching that evicts rejected requests.
- Resolved M-02 by mirroring `aria-expanded`, cancelling pending requests, tracking the exact initiating element, and restoring focus without reapplying dimming.
- Resolved M-03 by adding a fresh-database Kestrel + Firefox WebDriver BiDi browser suite over the real page wiring.
- Replaced local duplicate DTOs/service URLs with generated Serenity ServerTypes.
- Added coherent catalog empty/error states with a retry action.
- A fresh `pi -p` focused independent re-review resolved H-01, M-01 through M-03, and L-01/L-02; P2 is now independently reviewed.
- Remaining L-03 concerns browser-test assertion precision/fault injection only and does not block the P2 gate.

## Verify

Passed:

```text
dotnet build SerenityQuantResearch.slnx --no-restore
  0 warnings, 0 errors

dotnet test SerenityQuantResearch.slnx --no-build
  13 passed, 0 failed

cd src/SerenityQuantResearch/SerenityQuantResearch.Web
npm run test:ui
  5 Node state/request tests passed
  fresh Kestrel + Firefox browser smoke passed
npm run build
  passed
```

Authenticated Kestrel HTTP/UI smoke at `http://127.0.0.1:5000`:

- anonymous `/Research/Cpo`: expected `302` to login
- authenticated `/Research/Cpo`: `200`
- authenticated part detail example: `200`
- generated diagram JS/CSS: `200`
- `PartResearch/ListParts`: `200`, 9 modules and 21 unique parts
- `PartResearch/RetrieveCompleteChain`: `200`, complete drawer contract
- candidate company and draft evidence states preserved in JSON response
- application log contained no failed/unhandled request

The UI smoke covers the real rendered page, generated frontend assets, authenticated service responses, all 21 SVG/table bindings, pointer and keyboard selection, drawer contract sections, ARIA/focus reset, fallback navigation, detail, and error rendering in headless Firefox.

## Acceptance checklist

1. Start the app and sign in with the local Serene development account.
2. Open `http://localhost:5000/Research/Cpo`.
3. Hover a part and confirm its module remains active while unrelated modules dim.
4. Click a part and confirm the selection stays locked after pointer leave.
5. Close/clear the drawer and confirm dimming is removed.
6. Tab to SVG parts and select with Enter and Space; clear with Escape.
7. Expand each tree group and confirm all 21 parts are reachable without the SVG.
8. Open the switch ASIC part and confirm Broadcom is labeled `candidate` and evidence is labeled `draft`.
9. Use “打开完整部件详情” and confirm the stable part ID resolves at the detail URL.
10. Confirm empty mappings render warnings/questions instead of inferred company relationships.

## Known gaps

- Only one seed part currently has a company/evidence chain; the other parts intentionally expose missing coverage. Populating company coverage belongs to later authorized work and must follow the verification contract.
- Independent re-review recorded L-03: browser regression assertions can be hardened with exact ID-set checks, exact representation focus checks, and fault-injected async/catalog scenarios.
- Headless Firefox covers functional rendering and interaction, but no cross-browser, screen-reader, contrast, zoom/high-contrast, or pixel-diff suite is installed.
- The taxonomy still requires domain reviewer sign-off, and JPEG provenance/public reuse rights remain unresolved.
- Default Serene development authentication is not production hardening.
- The repository still has no `.git` metadata, so file review used inventory and automated verification rather than git diff.

## P3 readiness

P3 can start without changing the P2 SVG contract:

- all stable part IDs resolve through a service catalog;
- part-to-company/evidence navigation is service-based;
- candidate/draft state labels are visible and preserved;
- part detail URLs provide a stable future cross-navigation target.

Stop here. Do not implement the company universe/comparison until P3 is explicitly authorized.
