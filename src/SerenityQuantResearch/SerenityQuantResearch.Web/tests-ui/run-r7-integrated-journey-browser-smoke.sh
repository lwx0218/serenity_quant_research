#!/usr/bin/env bash
set -euo pipefail

command -v firefox >/dev/null || { echo "Firefox is required for the R7 integrated journey browser smoke" >&2; exit 1; }

free_port() {
    python3 - <<'PY'
import socket
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    print(sock.getsockname()[1])
PY
}
PORT=$(free_port)
BIDI=$(free_port)
while [[ "$BIDI" == "$PORT" ]]; do BIDI=$(free_port); done
ROOT=$(cd "$(dirname "$0")/../../../.." && pwd)
DB="/tmp/serenity-r7-journey-ui-$$.sqlite"
KLOG="/tmp/serenity-r7-journey-ui-$$.kestrel.log"
FLOG="/tmp/serenity-r7-journey-ui-$$.firefox.log"
PROFILE="/tmp/serenity-r7-journey-ui-profile-$$"
SCRIPT="/tmp/serenity-r7-journey-ui-$$.mjs"
SCREENSHOT_DIR="${UI_SCREENSHOT_DIR:-$ROOT/operations/reviews/research-experience-reboot-r7-screenshots}"
mkdir -p "$PROFILE" "$SCREENSHOT_DIR"

cleanup() {
    if [[ -n "${FIREFOX_PID:-}" ]]; then
        kill "$FIREFOX_PID" 2>/dev/null || true
        wait "$FIREFOX_PID" 2>/dev/null || true
    fi
    if [[ -n "${APP_PID:-}" ]]; then
        kill "$APP_PID" 2>/dev/null || true
        wait "$APP_PID" 2>/dev/null || true
    fi
    rm -rf "$PROFILE" "$SCRIPT" "$DB" "$DB-shm" "$DB-wal" "$KLOG" "$FLOG"
}
trap cleanup EXIT

cd "$ROOT"
ASPNETCORE_ENVIRONMENT=Development \
ASPNETCORE_URLS="http://127.0.0.1:$PORT" \
Data__Default__ConnectionString="Data Source=$DB" \
OpenAccess__Enabled=true BackgroundJobs__Enabled=false ClamAV__Enabled=false StartNodeScripts='' \
dotnet run --no-build --project src/SerenityQuantResearch/SerenityQuantResearch.Web/SerenityQuantResearch.Web.csproj \
    --urls "http://127.0.0.1:$PORT" >"$KLOG" 2>&1 &
APP_PID=$!
for _ in $(seq 1 120); do
    curl -fsS "http://127.0.0.1:$PORT/Account/Login" >/dev/null 2>&1 && break
    kill -0 "$APP_PID" 2>/dev/null || { tail -120 "$KLOG"; exit 1; }
    sleep .25
done
curl -fsS "http://127.0.0.1:$PORT/Account/Login" >/dev/null

firefox --headless --no-remote --profile "$PROFILE" --remote-debugging-port "$BIDI" about:blank >"$FLOG" 2>&1 &
FIREFOX_PID=$!
for _ in $(seq 1 100); do
    grep -q 'WebDriver BiDi listening' "$FLOG" && break
    kill -0 "$FIREFOX_PID" 2>/dev/null || { tail -100 "$FLOG"; exit 1; }
    sleep .25
done
grep -q 'WebDriver BiDi listening' "$FLOG"

cat >"$SCRIPT" <<'JS'
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';

const [port, bidi, screenshotDir] = process.argv.slice(2);
const base = `http://127.0.0.1:${port}`;
const ws = new WebSocket(`ws://127.0.0.1:${bidi}/session`);
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
let sequence = 0;
const pending = new Map();
ws.onmessage = event => {
    const message = JSON.parse(event.data);
    if (!message.id || !pending.has(message.id)) return;
    const [resolve, reject] = pending.get(message.id);
    pending.delete(message.id);
    message.type === 'error' ? reject(new Error(JSON.stringify(message))) : resolve(message);
};
const command = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++sequence;
    pending.set(id, [resolve, reject]);
    ws.send(JSON.stringify({ id, method, params }));
});
await command('session.new', { capabilities: { alwaysMatch: {} } });
const context = (await command('browsingContext.create', { type: 'tab' })).result.context;
const navigate = url => command('browsingContext.navigate', { context, url, wait: 'complete' });
async function evaluate(expression, awaitPromise = false) {
    const wrapped = awaitPromise ? `(async()=>JSON.stringify(await (${expression})))()` : `JSON.stringify(${expression})`;
    const response = await command('script.evaluate', { expression: wrapped, target: { context }, awaitPromise, resultOwnership: 'none' });
    const result = response.result?.result;
    if (result?.type !== 'string') throw new Error(JSON.stringify(response));
    return JSON.parse(result.value);
}
async function waitFor(expression, label) {
    for (let attempt = 0; attempt < 180; attempt++) {
        if (await evaluate(`Boolean(${expression})`)) return;
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    const diagnostic = await evaluate(`(()=>({path:location.pathname, search:location.search, text:document.body.innerText.slice(0, 1800), app:document.querySelector('#research-workspace-app')?.dataset}))()`);
    throw new Error(`Timeout: ${label}: ${JSON.stringify(diagnostic)}`);
}
async function viewport(width, height) {
    await command('browsingContext.setViewport', { context, viewport: { width, height }, devicePixelRatio: 1 });
}
async function screenshot(name) {
    const response = await command('browsingContext.captureScreenshot', { context, origin: 'viewport' });
    writeFileSync(join(screenshotDir, name), Buffer.from(response.result.data, 'base64'));
}
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
function assert(condition, message) { if (!condition) throw new Error(message); }
const act = async expression => evaluate(`(()=>{${expression};return true})()`);

async function assertResearchShell(expectedActive) {
    const state = await evaluate(`(()=>{const nav=document.querySelector('[data-testid="research-primary-nav"]');return{hasTopbar:!!document.querySelector('[data-testid="research-shell-topbar"]'),hasSidebar:!!document.querySelector('#s-sidebar'),labels:nav?[...nav.querySelectorAll('a')].map(x=>x.textContent.trim()):[],hrefs:nav?[...nav.querySelectorAll('a')].map(x=>new URL(x.href).pathname):[],active:nav?.querySelector('a.is-active')?.textContent.trim()??'',navText:nav?.innerText??''}})()`);
    assert(state.hasTopbar, 'research shell topbar missing');
    assert(!state.hasSidebar, 'Serenity sidebar leaked into research shell');
    assert(JSON.stringify(state.labels) === JSON.stringify(['CPO Explorer', 'Company Pool', 'Research Workspace']), 'research primary nav labels changed');
    assert(JSON.stringify(state.hrefs) === JSON.stringify(['/Research/Cpo', '/Research/Companies', '/Research/Workspace']), 'research primary nav hrefs changed');
    assert(state.active === expectedActive, `expected active nav ${expectedActive}, got ${state.active}`);
    assert(!/Dashboard|Administration|Users|Roles|Permissions/.test(state.navText), 'admin nav leaked into research primary nav');
}

async function assertNoForbiddenControls() {
    const state = await evaluate(`(()=>({text:document.body.innerText, controls:[...document.querySelectorAll('a,button,input,textarea,[contenteditable="true"]')].map(x=>x.textContent || x.getAttribute('aria-label') || x.name || '').join(String.fromCharCode(10)), editable:!!document.querySelector('textarea,[contenteditable="true"]'), slick:!!document.querySelector('.slickgrid-container,.slick-pane,.company-sleekgrid')}))()`);
    assert(!/New Note|Graph|ResearchNote|OpenQuestion|Backlink/i.test(state.controls), 'deferred writing/graph controls leaked into Workspace controls');
    assert(!state.editable, 'editable surface leaked into read-only Workspace');
    assert(!state.slick, 'grid/admin surface leaked into Workspace');
    assert(!/Company Comparison|market share|BOM|投资逻辑/i.test(state.text), 'out-of-scope comparison or unsupported facts leaked into Workspace');
}

async function waitWorkspace(objectType, objectId) {
    await waitFor(`document.querySelector('#research-workspace-app')?.dataset.objectType === '${objectType}' && document.querySelector('#research-workspace-app')?.dataset.objectId === '${objectId}' && document.querySelector('#research-workspace-app')?.dataset.readOnly === 'true'`, `${objectType} workspace loaded`);
}

async function assertCompanyWorkspaceIntegrated() {
    const state = await evaluate(`(()=>{const text=document.body.innerText;return{path:location.pathname,search:location.search,app:document.querySelector('#research-workspace-app')?.dataset,text,relationship:document.querySelector('.workspace-context')?.innerText??'',linked:[...document.querySelectorAll('[data-workspace-linked-object]')].map(x=>({type:x.dataset.workspaceLinkedObject,id:x.dataset.workspaceLinkedObjectId,text:x.textContent})),evidenceBacklinks:[...document.querySelectorAll('[data-workspace-backlink="evidence"]')].map(x=>({tag:x.tagName,href:x.getAttribute('href'),id:x.dataset.workspaceBacklinkId}))}})()`);
    assert(state.path === '/Research/Workspace', 'company Workspace route changed');
    assert(state.app.objectType === 'company' && state.app.objectId === 'global.broadcom' && state.app.readOnly === 'true', 'company workspace identity/read-only state missing');
    assert(state.search.includes('source=cpo-explorer') && state.search.includes('companyId=global.broadcom') && state.search.includes('componentId=cpo.mod.host-asic'), 'Explorer/company context query not preserved');
    assert(state.text.includes('Broadcom Inc.'), 'company current object missing');
    assert(state.text.includes('Candidate / 候选（未核验）'), 'candidate state not visible');
    assert(state.text.includes('EVD-2026-0001@v1') && /draft \/ Not reviewed|Draft/.test(state.text), 'draft evidence not kept unreviewed');
    assert(state.text.includes('separate from verified conclusions'), 'gaps are not separated from conclusions');
    assert(state.relationship.includes('CPO Explorer') && state.search.includes('componentId=cpo.mod.host-asic'), `CPO Explorer source path missing in Workspace context: ${state.relationship}`);
    assert(state.relationship.includes('CompanyExposure'), 'derived CompanyExposure relationship context missing');
    assert(state.linked.some(x => x.type === 'part' && x.id === 'cpo.part.host-asic.switch-die'), 'part linked-object navigation missing');
    assert(state.evidenceBacklinks.some(x => x.id === 'EVD-2026-0001' && x.tag !== 'A' && !x.href), 'evidence backlink must be read-only context, not a dead href');
}

async function runIntegratedJourney(width, height, suffix) {
    await viewport(width, height);
    await navigate(`${base}/Research/Cpo`);
    await waitFor(`document.querySelector('#cpo-explorer-app')?.dataset.ready === 'true' && document.querySelector('.cpo-component-three[data-component-id="cpo.mod.host-asic"]')`, 'Explorer loaded');
    await assertResearchShell('CPO Explorer');
    await act(`const target=document.querySelector('.cpo-component-three[data-component-id="cpo.mod.host-asic"]'); target.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,pointerType:'mouse'})); target.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));`);
    await waitFor(`document.querySelector('#cpo-research-drawer:not([hidden])') && document.querySelector('.cpo-company-pool-link') && document.querySelector('.cpo-workspace-link')`, 'Explorer drawer seam links visible');
    await act(`document.querySelector('[data-child-part-id="cpo.part.host-asic.switch-die"]').click()`);
    await waitFor(`document.querySelector('[data-child-part-id="cpo.part.host-asic.switch-die"]')?.classList.contains('is-active') && document.querySelector('.cpo-company-pool-link')?.href.includes('partId=cpo.part.host-asic.switch-die')`, 'Explorer child part context selected');
    const explorerLinks = await evaluate(`(()=>{const pool=new URL(document.querySelector('.cpo-company-pool-link').href); const workspace=new URL(document.querySelector('.cpo-workspace-link').href); return {pool:{pathname:pool.pathname,search:pool.search,href:pool.href}, workspace:{pathname:workspace.pathname,search:workspace.search,href:workspace.href}}})()`);
    assert(explorerLinks.pool.pathname === '/Research/Companies' && explorerLinks.pool.search.includes('source=cpo-explorer') && explorerLinks.pool.search.includes('componentId=cpo.mod.host-asic') && explorerLinks.pool.search.includes('partId=cpo.part.host-asic.switch-die'), 'Explorer Company Pool link lost source context');
    assert(explorerLinks.workspace.pathname === '/Research/Workspace' && explorerLinks.workspace.search.includes('objectId=cpo.part.host-asic.switch-die') && explorerLinks.workspace.search.includes('source=cpo-explorer'), 'Explorer Workspace link lost object/source context');
    await sleep(180);
    await screenshot(`r7-journey-explorer-selected-${suffix}.png`);

    await act(`document.querySelector('.cpo-company-pool-link').click()`);
    await waitFor(`location.pathname === '/Research/Companies' && location.search.includes('source=cpo-explorer') && location.search.includes('componentId=cpo.mod.host-asic') && location.search.includes('partId=cpo.part.host-asic.switch-die') && document.querySelector('[data-company-card="true"][data-company-id="global.broadcom"]')`, 'Company Pool reached from Explorer');
    await assertResearchShell('Company Pool');
    await sleep(180);
    await screenshot(`r7-journey-company-pool-${suffix}.png`);

    await act(`const card=document.querySelector('[data-company-card="true"][data-company-id="global.broadcom"]'); card.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,pointerType:'mouse'})); card.click();`);
    await waitFor(`document.querySelector('#company-quick-drawer.is-open') && document.querySelector('.company-expand-link') && document.querySelector('.company-workspace-link')`, 'Company quick drawer seam links visible');
    const drawer = await evaluate(`(()=>{const text=document.querySelector('#company-quick-drawer')?.innerText??''; const expand=new URL(document.querySelector('.company-expand-link').href); const workspace=new URL(document.querySelector('.company-workspace-link').href); return {text, expand:{pathname:expand.pathname,search:expand.search,href:expand.href}, workspace:{pathname:workspace.pathname,search:workspace.search,href:workspace.href}}})()`);
    assert(drawer.text.includes('CPO Explorer') && drawer.text.includes('CompanyExposure'), 'Company drawer lost Explorer/CompanyExposure context');
    assert(drawer.expand.pathname === '/Research/Companies/global.broadcom' && drawer.expand.search.includes('source=cpo-explorer') && drawer.expand.search.includes('componentId=cpo.mod.host-asic'), 'Company drawer expand link lost source context');
    assert(drawer.workspace.pathname === '/Research/Workspace' && drawer.workspace.search.includes('companyId=global.broadcom') && drawer.workspace.search.includes('source=cpo-explorer'), 'Company drawer workspace link lost source context');
    await sleep(180);
    await screenshot(`r7-journey-company-drawer-${suffix}.png`);

    await act(`document.querySelector('.company-expand-link').click()`);
    await waitFor(`location.pathname === '/Research/Companies/global.broadcom' && location.search.includes('source=cpo-explorer') && document.querySelector('#company-detail-content')?.innerText.includes('Open in Research Workspace')`, 'Company Detail reached from drawer');
    await assertResearchShell('Company Pool');
    const detail = await evaluate(`(()=>{const text=document.querySelector('#company-detail-content')?.innerText??''; const workspace=new URL(document.querySelector('.company-detail-section a[href*="/Research/Workspace"]').href); return {text, workspace:{pathname:workspace.pathname,search:workspace.search,href:workspace.href}}})()`);
    assert(detail.text.includes('CPO Explorer') && detail.text.includes('Industry-chain Exposure'), 'Company Detail lost Explorer/exposure context');
    assert(detail.workspace.pathname === '/Research/Workspace' && detail.workspace.search.includes('companyId=global.broadcom') && detail.workspace.search.includes('source=cpo-explorer'), 'Company Detail workspace link lost source context');
    await sleep(180);
    await screenshot(`r7-journey-company-detail-${suffix}.png`);

    await act(`document.querySelector('.company-detail-section a[href*="/Research/Workspace"]').click()`);
    await waitWorkspace('company', 'global.broadcom');
    await assertResearchShell('Research Workspace');
    await assertCompanyWorkspaceIntegrated();
    await assertNoForbiddenControls();
    await sleep(180);
    await screenshot(`r7-journey-workspace-company-${suffix}.png`);
}

await runIntegratedJourney(1440, 980, '1440');
await runIntegratedJourney(1920, 1080, '1920');

await command('session.end');
JS

node "$SCRIPT" "$PORT" "$BIDI" "$SCREENSHOT_DIR"
echo "R7 integrated journey browser smoke passed; screenshots saved to $SCREENSHOT_DIR"
