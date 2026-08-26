# Phase 1 P1 Work Log — Serenity Bootstrap and Core Objects

## Status

- Date: 2026-08-24
- Route: `plan`
- Result: completed
- P2 status: not started

## Implemented

### Runtime and project structure

- Installed user-local .NET SDK `10.0.400`, Node `24.19.0`, and npm `11.17.0`.
- Generated Community `Serene.Templates@10.3.7` without demo modules.
- Added `global.json`, `SerenityQuantResearch.slnx`, web project, xUnit project, root ignore rules, and platform normalization for hosts exporting `PLATFORM=linux`.
- Switched the local database from LocalDB to repository-relative SQLite runtime storage under the web application's `App_Data/`.
- Disabled nonessential local background jobs, ClamAV, and automatic Node watch startup.

### Research domain

FluentMigrator and Serenity Row models now cover:

- `Theme`
- `IndustryChain` / recursive `IndustryChainNode`
- `PhysicalModule` / recursive `PhysicalPart`
- `TechnologyLink`
- part ↔ technology and part ↔ industry-chain links
- `Company` / `CompanyExposure`
- `SourceDocument` / `Event` / versioned `Evidence`
- versioned `ResearchConclusion` / `ResearchReport`
- exposure/evidence, conclusion/evidence, report/conclusion, and report/evidence locked-version links

Primary entities use Serenity logging rows with insert/update audit fields. Minimum permissions separate general maintenance, evidence review, and publication.

### Seed and services

- Added `data/seeds/cpo/cpo-research-seed.json`.
- Added validation for duplicate/missing IDs, recursive cycles, broken references, source levels, and mandatory draft state for machine-assisted seed evidence.
- Added an idempotent startup importer.
- Seed result: 9 modules, 21 parts, 10 chain nodes, 4 technology links, and 20 companies.
- Added one deliberately limited example:
  - `cpo.part.host-asic.switch-die`
  - `global.broadcom`
  - exposure state `candidate`
  - evidence `EVD-2026-0001@v1`, state `draft`
- Added `PartResearchService` / endpoint for complete-chain queries.
- Added evidence workflow service/endpoint and conclusion publication policy baseline.

The example proves data relationships only. It does not assert a verified CPO product, supplier relationship, or investment conclusion.

## Verify

Passed:

```text
dotnet restore SerenityQuantResearch.slnx
dotnet build SerenityQuantResearch.slnx --no-restore
dotnet test SerenityQuantResearch.slnx --no-build
npm ci
npm run build
dotnet sergen doctor
```

Results:

- Build: 0 warnings, 0 errors
- Tests: 12 passed, 0 failed
- Fresh application startup: passed
- Login HTTP smoke: `200`
- Anonymous root behavior: expected `302` to login
- Fresh SQLite migration: passed
- Seed idempotency: passed in integration test
- Runtime counts: modules 9, parts 21, chain nodes 10, companies 20, example exposures 1, example evidence 1
- Complete part → company exposure → evidence query: passed
- Evidence unique version key: `(StableId, Version)` verified
- No P2 SVG, copied JPEG layer, trading module, market data, account integration, backtest, or browser runtime added

## Known gaps

- No P2 research diagram, drawer, part page, or table/tree UI yet.
- P1 exposes a complete-chain service but does not yet provide business-facing Serenity grids/forms for every research object.
- Seed company mappings remain candidate/discovery records; no exposure was promoted to `verified`.
- Seed evidence remains `draft`; no conclusion/report was published.
- JPEG provenance and public reuse rights remain unresolved.
- The default Serene authentication/bootstrap behavior still needs production hardening before deployment.
- The repository directory still has no `.git` metadata, so change review used file inventory and automated validation rather than git diff.

## P2 Readiness

P2 may start without schema redesign:

- stable `part_id` values exist;
- physical and industry-chain models are separate and queryable;
- recursive expansion is supported;
- SVG geometry can bind to domain IDs without carrying business relationships;
- company/evidence states prevent candidate seed data from appearing as reviewed fact.

Before P2, confirm the desired original SVG visual composition and accessibility acceptance criteria; do not reopen the frozen product scope.
