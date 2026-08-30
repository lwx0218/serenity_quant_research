#!/usr/bin/env bash
set -euo pipefail

command -v firefox >/dev/null || { echo "Firefox is required for the R6 Workspace browser smoke" >&2; exit 1; }

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
DB="/tmp/serenity-r6-workspace-ui-$$.sqlite"
KLOG="/tmp/serenity-r6-workspace-ui-$$.kestrel.log"
FLOG="/tmp/serenity-r6-workspace-ui-$$.firefox.log"
PROFILE="/tmp/serenity-r6-workspace-ui-profile-$$"
SCRIPT="/tmp/serenity-r6-workspace-ui-$$.mjs"
SCREENSHOT_DIR="${UI_SCREENSHOT_DIR:-$ROOT/operations/reviews/research-experience-reboot-r6-screenshots}"
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
        if (await evaluate(expression)) return;
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    const diagnostic = await evaluate(`(()=>({path:location.pathname, search:location.search, text:document.body.innerText.slice(0, 1600), app:document.querySelector('#research-workspace-app')?.dataset}))()`);
    throw new Error(`Timeout: ${label}: ${JSON.stringify(diagnostic)}`);
}
async function viewport(width, height = 980) {
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
    assert(!state.hasSidebar, 'Serenity sidebar leaked into Workspace shell');
    assert(JSON.stringify(state.labels) === JSON.stringify(['CPO Explorer', 'Company Pool', 'Research Workspace']), 'research primary nav labels changed');
    assert(JSON.stringify(state.hrefs) === JSON.stringify(['/Research/Cpo', '/Research/Companies', '/Research/Workspace']), 'research primary nav hrefs changed');
    assert(state.active === expectedActive, `expected active nav ${expectedActive}, got ${state.active}`);
    assert(!/Dashboard|Administration|Users|Roles|Permissions/.test(state.navText), 'admin nav leaked into research primary nav');
}

async function waitWorkspace(objectType, objectId) {
    await waitFor(`document.querySelector('#research-workspace-app')?.dataset.objectType === '${objectType}' && document.querySelector('#research-workspace-app')?.dataset.objectId === '${objectId}' && document.querySelector('#research-workspace-app')?.dataset.readOnly === 'true'`, `${objectType} workspace loaded`);
}

async function assertNoForbiddenControls() {
    const state = await evaluate(`(()=>({text:document.body.innerText, controls:[...document.querySelectorAll('button,input,textarea,[contenteditable="true"]')].map(x=>x.textContent || x.getAttribute('aria-label') || x.name || '').join(String.fromCharCode(10)), editable:!!document.querySelector('textarea,[contenteditable="true"]'), slick:!!document.querySelector('.slickgrid-container,.slick-pane,.company-sleekgrid')}))()`);
    assert(!/New Note|Graph|ResearchNote|OpenQuestion|Backlink/i.test(state.controls), 'deferred writing/graph controls leaked into Workspace controls');
    assert(!state.editable, 'editable surface leaked into read-only Workspace');
    assert(!state.slick, 'grid/admin surface leaked into Workspace');
    assert(!/Company Comparison|market share|BOM|投资逻辑/i.test(state.text), 'out-of-scope comparison or unsupported facts leaked into Workspace');
}

async function assertComponentWorkspace() {
    const state = await evaluate(`(()=>{const text=document.body.innerText;return{path:location.pathname,search:location.search,app:document.querySelector('#research-workspace-app')?.dataset,text,sections:[...document.querySelectorAll('.workspace-section h3')].map(x=>x.textContent.trim()),tree:[...document.querySelectorAll('.workspace-tree-item')].map(x=>x.textContent.trim()).join(String.fromCharCode(10)),linked:[...document.querySelectorAll('[data-workspace-linked-object]')].map(x=>({type:x.dataset.workspaceLinkedObject,id:x.dataset.workspaceLinkedObjectId,text:x.textContent})),evidenceBacklinks:[...document.querySelectorAll('[data-workspace-backlink="evidence"]')].map(x=>({tag:x.tagName,href:x.getAttribute('href'),id:x.dataset.workspaceBacklinkId})),relationship:document.querySelector('.workspace-context')?.innerText??''}})()`);
    assert(state.path === '/Research/Workspace', 'component Workspace route changed');
    assert(state.app.readOnly === 'true', 'Workspace is not marked read-only');
    assert(state.text.includes('Host ASIC'), 'current component missing');
    assert(state.text.includes('cpo.part.host-asic.switch-die') || state.text.includes('交换 ASIC 裸片/封装'), 'linked child part missing');
    assert(state.text.includes('Broadcom Inc.'), 'linked company missing');
    assert(state.text.includes('EVD-2026-0001@v1') && /draft \/ Not reviewed|Draft/.test(state.text), 'draft evidence is not visible as not reviewed');
    assert(state.sections.includes('Existing conclusions') && state.sections.includes('Read-only gaps / unresolved questions'), 'conclusions are not separated from gaps');
    assert(state.sections.includes('Read-only gaps / unresolved questions'), 'read-only gap section missing');
    assert(state.relationship.includes('CPO Explorer') && state.relationship.includes('CompanyExposure'), 'source path or derived relationship context missing');
    assert(state.linked.some(x => x.type === 'company' && x.id === 'global.broadcom'), 'company linked-object navigation missing');
    assert(state.evidenceBacklinks.some(x => x.id === 'EVD-2026-0001' && x.tag !== 'A' && !x.href), 'evidence backlink must be read-only context, not a dead href');
}

async function assertCompanyWorkspace() {
    const state = await evaluate(`(()=>{const text=document.body.innerText;return{path:location.pathname,search:location.search,app:document.querySelector('#research-workspace-app')?.dataset,text,relationship:document.querySelector('.workspace-context')?.innerText??'',linked:[...document.querySelectorAll('[data-workspace-linked-object]')].map(x=>({type:x.dataset.workspaceLinkedObject,id:x.dataset.workspaceLinkedObjectId,text:x.textContent})),evidenceBacklinks:[...document.querySelectorAll('[data-workspace-backlink="evidence"]')].map(x=>({tag:x.tagName,href:x.getAttribute('href'),id:x.dataset.workspaceBacklinkId}))}})()`);
    assert(state.path === '/Research/Workspace', 'company Workspace route changed');
    assert(state.app.objectType === 'company' && state.app.objectId === 'global.broadcom', 'company object identity missing');
    assert(state.search.includes('source=') && state.search.includes('companyId=global.broadcom'), 'company/source query not preserved');
    assert(state.text.includes('Broadcom Inc.'), 'company current object missing');
    assert(state.text.includes('Candidate / 候选（未核验）'), 'candidate state not visible');
    assert((state.text.includes('cpo.part.host-asic.switch-die') || state.text.includes('交换 ASIC 裸片/封装')) && (state.text.includes('cpo.chain.asic') || state.text.includes('交换 ASIC')), 'linked part/chain context missing');
    assert(state.text.includes('EVD-2026-0001@v1') && /draft \/ Not reviewed|Draft/.test(state.text), 'draft evidence not kept unreviewed');
    assert(state.text.includes('separate from verified conclusions'), 'gaps are not separated from conclusions');
    assert(state.relationship.includes('Company Detail') || state.relationship.includes('Company Pool') || state.relationship.includes('CPO Explorer'), 'source path missing in right context');
    assert(state.linked.some(x => x.type === 'part' && x.id === 'cpo.part.host-asic.switch-die'), 'part linked-object navigation missing');
    assert(state.evidenceBacklinks.some(x => x.id === 'EVD-2026-0001' && x.tag !== 'A' && !x.href), 'company evidence backlink must be read-only context, not a dead href');
}

async function runWorkspaceViewport(width, height, suffix) {
    await viewport(width, height);
    await navigate(`${base}/Research/Workspace?objectType=component&objectId=cpo.mod.host-asic&source=cpo-explorer&componentId=cpo.mod.host-asic&partId=cpo.part.host-asic.switch-die`);
    await waitWorkspace('component', 'cpo.mod.host-asic');
    await assertResearchShell('Research Workspace');
    await assertComponentWorkspace();
    await assertNoForbiddenControls();
    await sleep(180);
    await screenshot(`r6-workspace-component-host-asic-${suffix}.png`);

    await navigate(`${base}/Research/Workspace?objectType=company&companyId=global.broadcom&source=company-detail&componentId=cpo.mod.host-asic&partId=cpo.part.host-asic.switch-die&chainNodeId=cpo.chain.asic&CountryRegion=%E7%BE%8E%E5%9B%BD&view=list`);
    await waitWorkspace('company', 'global.broadcom');
    await assertResearchShell('Research Workspace');
    await assertCompanyWorkspace();
    await assertNoForbiddenControls();
    await sleep(180);
    await screenshot(`r6-workspace-company-broadcom-${suffix}.png`);
}

await runWorkspaceViewport(1440, 980, '1440');
await runWorkspaceViewport(1920, 1080, '1920');

await viewport(1440, 980);
await navigate(`${base}/Research/Cpo`);
await waitFor(`document.querySelector('#cpo-explorer-app')?.dataset.ready === 'true' && document.querySelector('.cpo-component-three[data-component-id="cpo.mod.host-asic"]')`, 'Explorer loaded');
await act(`const target=document.querySelector('.cpo-component-three[data-component-id="cpo.mod.host-asic"]'); target.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,pointerType:'mouse'})); target.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));`);
await waitFor(`document.querySelector('#cpo-research-drawer:not([hidden])') && document.querySelector('#cpo-drawer-content')?.innerText.includes('Open Research Workspace')`, 'Explorer Workspace link visible');
await screenshot('r6-nav-explorer-selected-component-1440.png');
await act(`document.querySelector('.cpo-workspace-link').click()`);
await waitWorkspace('component', 'cpo.mod.host-asic');
await assertComponentWorkspace();
await screenshot('r6-nav-explorer-to-workspace-1440.png');

await navigate(`${base}/Research/Companies/global.broadcom?source=cpo-explorer&componentId=cpo.mod.host-asic&partId=cpo.part.host-asic.switch-die&chainNodeId=cpo.chain.asic&CountryRegion=%E7%BE%8E%E5%9B%BD&view=list`);
await waitFor(`location.pathname === '/Research/Companies/global.broadcom' && document.querySelector('#company-detail-content')?.innerText.includes('Open in Research Workspace')`, 'Company Detail Workspace link visible');
await screenshot('r6-nav-company-detail-source-1440.png');
await act(`document.querySelector('.company-detail-section a[href*="/Research/Workspace"]').click()`);
await waitWorkspace('company', 'global.broadcom');
await assertCompanyWorkspace();
await screenshot('r6-nav-company-detail-to-workspace-1440.png');

await navigate(`${base}/Research/Companies?source=cpo-explorer&componentId=cpo.mod.host-asic&partId=cpo.part.host-asic.switch-die`);
await waitFor(`document.querySelector('[data-company-card="true"][data-company-id="global.broadcom"]')`, 'Company Pool loaded');
await act(`const card=document.querySelector('[data-company-card="true"][data-company-id="global.broadcom"]'); card.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,pointerType:'mouse'})); card.click();`);
await waitFor(`document.querySelector('#company-quick-drawer.is-open') && document.querySelector('.company-workspace-link')`, 'Company Pool drawer Workspace link visible');
await act(`document.querySelector('.company-workspace-link').click()`);
await waitWorkspace('company', 'global.broadcom');
await assertCompanyWorkspace();

await command('session.end');
JS

node "$SCRIPT" "$PORT" "$BIDI" "$SCREENSHOT_DIR"
echo "R6 Workspace browser smoke passed; screenshots saved to $SCREENSHOT_DIR"
