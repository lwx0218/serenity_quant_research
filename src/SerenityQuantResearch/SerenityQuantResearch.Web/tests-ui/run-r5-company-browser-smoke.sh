#!/usr/bin/env bash
set -euo pipefail

command -v firefox >/dev/null || { echo "Firefox is required for the R5 Company browser smoke" >&2; exit 1; }

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
DB="/tmp/serenity-r5-company-ui-$$.sqlite"
KLOG="/tmp/serenity-r5-company-ui-$$.kestrel.log"
FLOG="/tmp/serenity-r5-company-ui-$$.firefox.log"
PROFILE="/tmp/serenity-r5-company-ui-profile-$$"
SCRIPT="/tmp/serenity-r5-company-ui-$$.mjs"
SCREENSHOT_DIR="${UI_SCREENSHOT_DIR:-$ROOT/operations/reviews/research-experience-reboot-r5-screenshots}"
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
for _ in $(seq 1 100); do
    curl -fsS "http://127.0.0.1:$PORT/Account/Login" >/dev/null 2>&1 && break
    kill -0 "$APP_PID" 2>/dev/null || { tail -100 "$KLOG"; exit 1; }
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
    const diagnostic = await evaluate(`(()=>({path:location.pathname, view:document.querySelector('#company-research-app')?.dataset.view, drawer:document.querySelector('#company-quick-drawer')?.className, status:document.querySelector('#company-pool-status')?.innerText, body:document.body.innerText.slice(0, 1400)}))()`);
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
const page = '/Research/Companies?source=cpo-explorer&componentId=cpo.mod.host-asic';
const waitCompanyPool = () => waitFor(`document.querySelector('#company-research-app')?.dataset.view && !document.querySelector('#company-filters')?.hasAttribute('aria-busy') && document.querySelectorAll('[data-company-card="true"]').length >= 20`, 'R5 Company Pool loaded');
const waitFilteredPool = () => waitFor(`!document.querySelector('#company-filters')?.hasAttribute('aria-busy') && document.querySelector('select[name="CountryRegion"]')?.value === '美国' && document.querySelector('[data-company-card="true"][data-company-id="global.broadcom"]') && document.querySelectorAll('[data-company-card="true"]').length > 1`, 'R5 Company Pool region filter loaded');
const waitDrawer = () => waitFor(`document.querySelector('#company-quick-drawer.is-open') && document.querySelector('#company-research-app')?.dataset.drawerCompanyId === 'global.broadcom' && document.querySelector('#company-quick-drawer-content')?.innerText.includes('Broadcom Inc.')`, 'Broadcom Quick Drawer open');
const waitDetail = () => waitFor(`location.pathname === '/Research/Companies/global.broadcom' && !!document.querySelector('#company-detail-content')?.innerText.includes('Company Overview')`, 'Broadcom Full Company Detail');

async function assertResearchShell(expectedActive) {
    const state = await evaluate(`(()=>{const nav=document.querySelector('[data-testid="research-primary-nav"]');return{hasTopbar:!!document.querySelector('[data-testid="research-shell-topbar"]'),hasSidebar:!!document.querySelector('#s-sidebar'),labels:nav?[...nav.querySelectorAll('a')].map(x=>x.textContent.trim()):[],active:nav?.querySelector('a.is-active')?.textContent.trim()??'',navText:nav?.innerText??''}})()`);
    assert(state.hasTopbar, 'research shell topbar missing');
    assert(!state.hasSidebar, 'Serenity sidebar leaked into Company Research shell');
    assert(JSON.stringify(state.labels) === JSON.stringify(['CPO Explorer', 'Company Pool', 'Research Workspace']), 'research primary nav labels changed');
    assert(state.active === expectedActive, `expected active nav ${expectedActive}, got ${state.active}`);
    assert(!/Dashboard|Administration|Users|Roles|Permissions/.test(state.navText), 'admin nav leaked into research primary nav');
}

async function assertCardDefault() {
    const state = await evaluate(`(()=>{const app=document.querySelector('#company-research-app');const cardIds=[...document.querySelectorAll('[data-company-card="true"]')].map(x=>x.dataset.companyId);return{path:location.pathname,view:app.dataset.view,cardHidden:document.querySelector('#company-card-panel').hidden,listHidden:document.querySelector('#company-list-panel').hidden,cardIds,context:[...document.querySelectorAll('[data-company-source-context]')].map(x=>x.textContent.trim()).join(String.fromCharCode(10)),text:document.body.innerText,hasSleekGrid:!!document.querySelector('.slickgrid-container,.slick-pane,.company-sleekgrid'),hasComparison:/Company Comparison|对比|comparison/i.test(document.body.innerText)}})()`);
    assert(state.path === '/Research/Companies', 'card click should not be needed for initial Company Pool route');
    assert(state.view === 'card' && !state.cardHidden && state.listHidden, 'Company Pool did not default to Card View');
    assert(state.cardIds.length === 20, `expected same 20-company universe in Card View, got ${state.cardIds.length}`);
    assert(state.cardIds.includes('global.broadcom'), 'Broadcom candidate card missing');
    assert(state.context.includes('CPO Explorer') && state.context.includes('Host ASIC'), 'Explorer/source context not visible in Card View');
    assert(!state.hasSleekGrid, 'SleekGrid surface leaked into R5 card-first pool');
    assert(!state.hasComparison, 'Company Comparison leaked into R5 pool');
    assert(/Candidate \/ 候选（未核验）|Research gap \/ 尚无暴露记录/.test(state.text), 'candidate/unmapped states not visibly differentiated on cards');
}

async function applyRegionFilter() {
    await act(`const select=document.querySelector('select[name="CountryRegion"]'); if (![...select.options].some(x=>x.value==='美国')) throw new Error('美国 region filter option missing'); select.value='美国'; document.querySelector('#company-filters').dispatchEvent(new Event('change',{bubbles:true,cancelable:true}));`);
    await waitFilteredPool();
    const state = await evaluate(`(()=>({region:document.querySelector('select[name="CountryRegion"]').value,count:document.querySelectorAll('[data-company-card="true"]').length,ids:[...document.querySelectorAll('[data-company-card="true"]')].map(x=>x.dataset.companyId),context:[...document.querySelectorAll('[data-company-source-context]')].map(x=>x.textContent.trim()).join(String.fromCharCode(10))}))()`);
    assert(state.region === '美国' && state.count > 1 && state.ids.includes('global.broadcom'), 'region filter did not keep Broadcom in the filtered company universe');
    assert(state.context.includes('CPO Explorer') && state.context.includes('Host ASIC'), 'source context was lost after applying lightweight filter');
}

async function assertListSharesUniverse() {
    const state = await evaluate(`(()=>{const cardIds=[...document.querySelectorAll('[data-company-card="true"]')].map(x=>x.dataset.companyId);document.querySelector('[data-company-view="list"]').click();const listIds=[...document.querySelectorAll('[data-company-row="true"]')].map(x=>x.dataset.companyId);return{view:document.querySelector('#company-research-app').dataset.view,region:document.querySelector('select[name="CountryRegion"]').value,cardIds,listIds,cardHidden:document.querySelector('#company-card-panel').hidden,listHidden:document.querySelector('#company-list-panel').hidden,context:[...document.querySelectorAll('[data-company-source-context]')].map(x=>x.textContent.trim()).join(String.fromCharCode(10)),text:document.body.innerText}})()`);
    assert(state.view === 'list' && state.cardHidden && !state.listHidden, 'List View did not activate as compact peer view');
    assert(state.region === '美国', 'List View did not preserve the active lightweight filter');
    assert(JSON.stringify(state.cardIds) === JSON.stringify(state.listIds), 'List View did not share Card View company universe/order');
    assert(state.context.includes('CPO Explorer') && state.context.includes('Host ASIC'), 'Explorer/source context not visible in List View');
    assert(/Candidate \/ 候选（未核验）/.test(state.text), 'candidate state not visible in List View');
}

async function assertDrawerState(expectedScroll) {
    const state = await evaluate(`(()=>({path:location.pathname,drawerOpen:document.querySelector('#company-quick-drawer').classList.contains('is-open'),cardPanelStillPresent:!!document.querySelector('#company-card-panel'),view:document.querySelector('#company-research-app').dataset.view,region:document.querySelector('select[name="CountryRegion"]').value,scrollY:Math.round(scrollY),context:[...document.querySelectorAll('[data-company-source-context]')].map(x=>x.textContent.trim()).join(String.fromCharCode(10)),text:document.querySelector('#company-quick-drawer-content')?.innerText??''}))()`);
    assert(state.path === '/Research/Companies', 'Quick Drawer first click navigated away from Company Pool');
    assert(state.drawerOpen && state.cardPanelStillPresent, 'Company Pool not preserved behind Quick Drawer');
    assert(state.region === '美国', 'active filter did not survive opening Quick Drawer');
    assert(Math.abs(state.scrollY - expectedScroll) <= 8, `scroll position changed after opening drawer: ${state.scrollY} vs ${expectedScroll}`);
    assert(state.context.includes('CPO Explorer') && state.context.includes('Host ASIC'), 'source context not preserved into drawer state');
    assert(state.text.includes('Candidate / 候选（未核验）'), 'candidate exposure was not visibly unverified in drawer');
    assert(state.text.includes('Draft / 草稿（未审核）'), 'draft evidence was not visibly unreviewed in drawer');
    assert(state.text.includes('Unknown / 未知（不可视为已核验）'), 'unknown state rule was not visible in drawer');
    assert(state.text.includes('Expand to Full Company Detail'), 'explicit expand action missing from Quick Drawer');
    assert(!/Company Comparison|new research entity|生产状态|market share|BOM|投资逻辑/i.test(state.text), 'out-of-scope or unsupported fact text leaked into drawer');
}

async function assertDrawerClosesVia(method) {
    if (method === 'esc')
        await act(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}))`);
    else if (method === 'outside')
        await act(`document.body.dispatchEvent(new Event('pointerdown',{bubbles:true,cancelable:true}))`);
    else
        await act(`document.querySelector('#company-quick-drawer-close').click()`);
    await waitFor(`!document.querySelector('#company-quick-drawer').classList.contains('is-open') && document.querySelector('#company-quick-drawer').hidden`, `drawer close via ${method}`);
    const state = await evaluate(`(()=>({path:location.pathname,view:document.querySelector('#company-research-app').dataset.view,region:document.querySelector('select[name="CountryRegion"]').value,context:[...document.querySelectorAll('[data-company-source-context]')].map(x=>x.textContent.trim()).join(String.fromCharCode(10))}))()`);
    assert(state.path === '/Research/Companies', `drawer close via ${method} navigated away`);
    assert(state.region === '美国', `active filter lost after drawer close via ${method}`);
    assert(state.context.includes('CPO Explorer') && state.context.includes('Host ASIC'), `source context lost after drawer close via ${method}`);
}

async function assertFullDetail() {
    const state = await evaluate(`(()=>{const text=document.querySelector('#company-detail-content')?.innerText??'';return{path:location.pathname,query:location.search,text,backHref:document.querySelector('.company-back-link')?.getAttribute('href')??'',tabCount:document.querySelectorAll('[role="tab"],.company-tab,.company-detail-tab').length,workspaceControls:[...document.querySelectorAll('button,input,textarea')].map(x=>x.textContent || x.getAttribute('aria-label') || x.name || '').join(String.fromCharCode(10))}})()`);
    assert(state.path === '/Research/Companies/global.broadcom', 'Expand did not navigate to Full Company Detail route');
    assert(state.query.includes('source=cpo-explorer') && state.query.includes('componentId=cpo.mod.host-asic'), 'Full Detail did not preserve source context query');
    assert(state.query.includes('CountryRegion=') && state.query.includes('view=list'), 'Full Detail did not preserve active filter/list context query');
    assert(state.backHref.includes('/Research/Companies?') && state.backHref.includes('CountryRegion=') && state.backHref.includes('view=list'), 'Full Detail Back link did not preserve source/filter context');
    for (const label of ['Current Research Context', 'Company Overview', 'Industry-chain Exposure', 'Key Evidence', 'Open Questions', 'Material Events / Financial Evidence', 'Link to Research Workspace'])
        assert(state.text.includes(label), `Full Detail missing entity-centric section: ${label}`);
    assert(state.text.includes('Candidate / 候选（未核验）'), 'candidate exposure was not visibly unverified in Full Detail');
    assert(state.text.includes('Draft / 草稿（未审核）'), 'draft evidence was not visibly unreviewed in Full Detail');
    assert(state.text.includes('Unknown / 未知（不可视为已核验）') || state.text.includes('Unknown / 未记录（不可视为已核验）'), 'unknown semantics not visible in Full Detail');
    assert(state.tabCount === 0, 'Full Detail leaked tab/seven-tab layout');
    assert(!/Company Comparison|SleekGrid|生产状态|market share|BOM|投资逻辑/i.test(state.text), 'out-of-scope comparison/grid/prototype fact text leaked into Full Detail');
    assert(!/New Note|Graph|ResearchNote/.test(state.workspaceControls), 'Workspace writing controls leaked into R5 Full Detail');
}

async function assertFullDetailPartAndChainContext() {
    await navigate(`${base}/Research/Companies/global.broadcom?source=cpo-explorer&componentId=cpo.mod.host-asic&partId=cpo.part.host-asic.switch-die&chainNodeId=cpo.chain.asic&CountryRegion=%E7%BE%8E%E5%9B%BD&view=list`);
    await waitDetail();
    const state = await evaluate(`(()=>{const text=document.querySelector('#company-detail-content')?.innerText??'';return{context:[...document.querySelectorAll('#company-detail-content .company-detail-section')].find(x=>x.innerText.includes('Current Research Context'))?.innerText??'',backHref:document.querySelector('.company-back-link')?.getAttribute('href')??'',text}})()`);
    assert(state.context.includes('Host ASIC'), 'Full Detail source path lost module context when part and chain are present');
    assert(state.context.includes('Switch Die / Host ASIC') || state.context.includes('cpo.part.host-asic.switch-die'), 'Full Detail source path lost child part context');
    assert(state.context.includes('ASIC / Switch Silicon') || state.context.includes('cpo.chain.asic'), 'Full Detail source path lost chain context');
    assert(state.backHref.includes('partId=cpo.part.host-asic.switch-die') && state.backHref.includes('chainNodeId=cpo.chain.asic') && state.backHref.includes('CountryRegion='), 'Back link lost part/chain/filter context');
    assert(!/Company Comparison|New Note|Graph|ResearchNote/i.test(state.text), 'out-of-scope Company Comparison or Workspace writing leaked into part+chain detail context');
}

async function runViewportEvidence(width, height, suffix) {
    await viewport(width, height);
    await navigate(`${base}${page}`);
    await waitCompanyPool();
    await assertResearchShell('Company Pool');
    await assertCardDefault();
    await applyRegionFilter();
    await screenshot(`r5-company-card-${suffix}.png`);

    await assertListSharesUniverse();
    await sleep(160);
    await screenshot(`r5-company-list-${suffix}.png`);

    await viewport(width, 480);
    await act(`document.querySelector('[data-company-view="card"]').click()`);
    await sleep(80);
    const scrollTarget = await evaluate(`(()=>{const card=document.querySelector('[data-company-card="true"][data-company-id="global.broadcom"]'); if (!card) throw new Error('Broadcom card missing for scroll preservation'); card.scrollIntoView({block:'center', inline:'nearest'}); const scroller=document.scrollingElement; return {max:Math.round(Math.max(0, scroller.scrollHeight - innerHeight)), cardCount:document.querySelectorAll('[data-company-card="true"]').length};})()`);
    await sleep(120);
    const scrollBefore = await evaluate(`Math.round(scrollY)`);
    assert(scrollBefore >= 40, `Company Pool did not create a stable measurable scroll position with the activation card in view: ${JSON.stringify({...scrollTarget, scrollY: scrollBefore})}`);
    await act(`const card=document.querySelector('[data-company-card="true"][data-company-id="global.broadcom"]'); card.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,pointerType:'mouse'})); card.click();`);
    await waitDrawer();
    await sleep(220);
    await assertDrawerState(scrollBefore);
    await sleep(220);
    await screenshot(`r5-company-drawer-${suffix}.png`);
    await assertDrawerClosesVia('esc');

    await act(`document.querySelector('[data-company-view="list"]').click(); document.querySelector('[data-company-row="true"][data-company-id="global.broadcom"]').click()`);
    await waitDrawer();
    await assertDrawerClosesVia('outside');
    await act(`document.querySelector('[data-company-row="true"][data-company-id="global.broadcom"]').click()`);
    await waitDrawer();
    await assertDrawerClosesVia('close');

    await act(`document.querySelector('[data-company-row="true"][data-company-id="global.broadcom"]').click()`);
    await waitDrawer();
    await act(`document.querySelector('.company-expand-link').click()`);
    await waitDetail();
    await viewport(width, height);
    await assertResearchShell('Company Pool');
    await assertFullDetail();
    await sleep(220);
    await screenshot(`r5-company-full-detail-${suffix}.png`);
}

await runViewportEvidence(1440, 980, '1440');
await runViewportEvidence(1920, 1080, '1920');
await viewport(1920, 1080);
await assertFullDetailPartAndChainContext();
await sleep(220);
await screenshot('r5-company-full-detail-part-chain-context-1920.png');
await command('session.end', {});
ws.close();
console.log(`R5 Company browser smoke passed; screenshots written to ${screenshotDir}`);
JS

node "$SCRIPT" "$PORT" "$BIDI" "$SCREENSHOT_DIR"
if grep -Eq 'Unhandled exception|System.InvalidOperationException' "$KLOG"; then
    echo "Unexpected unhandled/internal failure during R5 Company browser smoke" >&2
    grep -n -C 4 -E 'Unhandled exception|System.InvalidOperationException' "$KLOG" >&2 || true
    exit 1
fi
