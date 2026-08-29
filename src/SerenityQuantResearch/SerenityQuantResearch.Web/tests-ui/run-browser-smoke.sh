#!/usr/bin/env bash
set -euo pipefail

command -v firefox >/dev/null || { echo "Firefox is required for the R4 browser smoke" >&2; exit 1; }

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
DB="/tmp/serenity-r4-explorer-ui-$$.sqlite"
KLOG="/tmp/serenity-r4-explorer-ui-$$.kestrel.log"
FLOG="/tmp/serenity-r4-explorer-ui-$$.firefox.log"
PROFILE="/tmp/serenity-r4-explorer-ui-profile-$$"
SCRIPT="/tmp/serenity-r4-explorer-ui-$$.mjs"
SCREENSHOT_DIR="${UI_SCREENSHOT_DIR:-$ROOT/operations/reviews/research-experience-reboot-r4-screenshots}"
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
const expectedModules = [
  'cpo.mod.thermal', 'cpo.mod.host-asic', 'cpo.mod.eic', 'cpo.mod.pic', 'cpo.mod.laser',
  'cpo.mod.receiver', 'cpo.mod.fiber-interface', 'cpo.mod.cpa-substrate', 'cpo.mod.host-board'
];
const childCounts = new Map([
  ['cpo.mod.thermal', 3], ['cpo.mod.host-asic', 2], ['cpo.mod.eic', 3], ['cpo.mod.pic', 3], ['cpo.mod.laser', 2],
  ['cpo.mod.receiver', 1], ['cpo.mod.fiber-interface', 2], ['cpo.mod.cpa-substrate', 2], ['cpo.mod.host-board', 3]
]);
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
    const diagnostic = await evaluate(`(()=>({path:location.pathname, app:document.querySelector('#cpo-explorer-app')?.dataset ? {...document.querySelector('#cpo-explorer-app').dataset} : null, stateLine:document.querySelector('#cpo-state-line')?.innerText ?? '', body:document.body.innerText.slice(0, 1200)}))()`);
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
const waitReady = () => waitFor(`document.querySelector('#cpo-explorer-app')?.dataset.ready === 'true'`, 'R4 explorer ready');
const waitDrawer = id => waitFor(`document.querySelector('#cpo-research-drawer.is-open') && document.querySelector('#cpo-explorer-app')?.dataset.selected === '${id}' && document.querySelector('#cpo-drawer-content')?.innerText.includes('stable: ${id}')`, `drawer for ${id}`);
const setView = async view => act(`document.querySelector('#cpo-view-${view}').click()`);
const hoverComponent = async (scene, id) => act(`document.querySelector('#cpo-scene-${scene} .cpo-component[data-component-id="${id}"]').dispatchEvent(new MouseEvent('mouseenter',{bubbles:false,cancelable:true}))`);
const hoverCallout = async (scene, id) => act(`document.querySelector('#cpo-scene-${scene} .cpo-callout[data-component-id="${id}"]').dispatchEvent(new MouseEvent('mouseenter',{bubbles:false,cancelable:true}))`);
const clearHover = async (scene, selector, id) => act(`document.querySelector('#cpo-scene-${scene} ${selector}[data-component-id="${id}"]').dispatchEvent(new MouseEvent('mouseleave',{bubbles:false,cancelable:true}))`);
const clickComponent = async (scene, id) => act(`document.querySelector('#cpo-scene-${scene} .cpo-component[data-component-id="${id}"]').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))`);
const clickCallout = async (scene, id) => act(`document.querySelector('#cpo-scene-${scene} .cpo-callout[data-component-id="${id}"]').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))`);
const clickBlank = async () => act(`document.querySelector('#cpo-canvas-frame').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))`);
const esc = async () => act(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}))`);
const keySelect = async (scene, id, key = 'Enter') => act(`const el=document.querySelector('#cpo-scene-${scene} .cpo-component[data-component-id="${id}"]');el.focus();if(document.activeElement!==el)throw new Error('component did not receive keyboard focus');document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'${key}',bubbles:true,cancelable:true}))`);
async function assertResearchShell(expectedActive) {
    const state = await evaluate(`(()=>{const nav=document.querySelector('[data-testid="research-primary-nav"]');return{hasTopbar:!!document.querySelector('[data-testid="research-shell-topbar"]'),hasSidebar:!!document.querySelector('#s-sidebar'),labels:nav?[...nav.querySelectorAll('a')].map(x=>x.textContent.trim()):[],hrefs:nav?[...nav.querySelectorAll('a')].map(x=>new URL(x.href).pathname):[],active:nav?.querySelector('a.is-active')?.textContent.trim()??'',navText:nav?.innerText??''}})()`);
    assert(state.hasTopbar, 'research shell topbar missing');
    assert(!state.hasSidebar, 'Serenity sidebar leaked into research shell');
    assert(JSON.stringify(state.labels) === JSON.stringify(['CPO Explorer', 'Company Pool', 'Research Workspace']), 'primary research nav labels changed');
    assert(JSON.stringify(state.hrefs) === JSON.stringify(['/Research/Cpo', '/Research/Companies', '/Research/Workspace']), 'primary research nav hrefs changed');
    assert(state.active === expectedActive, `expected active nav ${expectedActive}, got ${state.active}`);
    for (const banned of ['Dashboard', 'Administration', 'Language', 'Users', 'Roles', 'Permissions'])
        assert(!state.navText.includes(banned), `banned primary-nav label visible: ${banned}`);
}
async function assertR2RegressionSurface() {
    for (const [width, height] of [[1440, 980], [1920, 1080]]) {
        await viewport(width, height);
        await navigate(`${base}/Research/Companies`);
        await waitFor(`document.querySelector('[data-testid="research-primary-nav"]') && document.querySelector('#company-research-app')`, `company research shell ${width}`);
        await assertResearchShell('Company Pool');
    }
    await navigate(`${base}/Research/Workspace`);
    await waitFor(`document.querySelector('[data-testid="research-primary-nav"]') && document.querySelector('.research-placeholder')`, 'workspace placeholder route');
    await assertResearchShell('Research Workspace');
    let state = await evaluate(`({text:document.querySelector('.research-placeholder')?.innerText??'',writeControls:[...document.querySelectorAll('button,a,input,textarea')].map(x=>x.textContent || x.getAttribute('aria-label') || x.name || '').join('\\n')})`);
    assert(state.text.includes('does not provide writing') || state.text.includes('不提供写入'), 'workspace placeholder must state no writing');
    assert(!/New Note|Graph|ResearchNote/.test(state.writeControls), 'deferred workspace controls leaked into placeholder');
    await navigate(`${base}/Administration/User`);
    await waitFor(`document.querySelector('#s-sidebar') && !document.querySelector('[data-testid="research-primary-nav"]')`, 'secondary admin route shell separation');
    state = await evaluate(`({path:location.pathname,sidebar:!!document.querySelector('#s-sidebar'),researchNav:!!document.querySelector('[data-testid="research-primary-nav"]')})`);
    assert(state.path === '/Administration/User' && state.sidebar && !state.researchNav, 'secondary admin route did not remain available outside research primary nav');
}
async function assertCoverage() {
    const state = await evaluate(`(()=>{const scenes=['flat','three'];const perScene=Object.fromEntries(scenes.map(scene=>[scene,{components:[...document.querySelectorAll('#cpo-scene-'+scene+' .cpo-component[data-component-id]')].map(x=>x.dataset.componentId),callouts:[...document.querySelectorAll('#cpo-scene-'+scene+' .cpo-callout[data-component-id]')].map(x=>x.dataset.componentId)}]));const app=document.querySelector('#cpo-explorer-app');return{ready:app.dataset.ready,moduleCount:app.dataset.catalogModuleCount,partCount:app.dataset.catalogPartCount,coverage:app.dataset.coverageComplete,perScene}})()`);
    assert(state.ready === 'true' && state.moduleCount === '9' && state.partCount === '21' && state.coverage === 'true', 'catalog coverage dataset mismatch');
    const expectedSorted = [...expectedModules].sort();
    for (const scene of ['flat', 'three']) {
        assert(JSON.stringify([...state.perScene[scene].components].sort()) === JSON.stringify(expectedSorted), `${scene} component stable-ID coverage mismatch`);
        assert(JSON.stringify([...state.perScene[scene].callouts].sort()) === JSON.stringify(expectedSorted), `${scene} callout stable-ID coverage mismatch`);
    }
}
async function assertGeometryOwnership(scene) {
    const geometry = await evaluate(`(()=>[...document.querySelectorAll('#cpo-scene-${scene} .cpo-component[data-component-id]')].map(el=>{const b=el.getBBox();return{scene:'${scene}',id:el.dataset.componentId,owner:el.dataset.hitOwner,width:b.width,height:b.height,area:b.width*b.height,stroke:[...el.querySelectorAll('*')].map(x=>getComputedStyle(x).stroke).join('|')}}))()`);
    assert(geometry.length === 9, `expected 9 component renderings in ${scene}`);
    for (const item of geometry) {
        assert(item.owner === 'real-geometry', `${item.scene}/${item.id} is not marked real-geometry`);
        assert(item.width > 20 && item.height > 20, `${item.scene}/${item.id} has usable visible geometry`);
        assert(item.area < 240000, `${item.scene}/${item.id} hit geometry is too broad`);
        assert(!/49, 85, 207/.test(item.stroke), `${item.scene}/${item.id} uses strong blue component stroke`);
    }
}
async function assertHoverPair(scene, id) {
    const state = await evaluate(`(()=>({component:document.querySelector('#cpo-scene-${scene} .cpo-component[data-component-id="${id}"]').classList.contains('is-hovered'),callout:document.querySelector('#cpo-scene-${scene} .cpo-callout[data-component-id="${id}"]').classList.contains('is-hovered'),dimmed:[...document.querySelectorAll('#cpo-scene-${scene} .cpo-component[data-component-id]')].filter(x=>x.dataset.componentId!=='${id}').every(x=>x.classList.contains('is-dimmed')),line:document.querySelector('#cpo-state-line').innerText}))()`);
    assert(state.component && state.callout, `${scene}/${id} hover did not focus paired component/callout`);
    assert(state.dimmed, `${scene}/${id} hover did not de-emphasize unrelated components`);
    assert(state.line.includes('hover preview') && !state.line.includes('selected'), `${scene}/${id} hover announced as selected`);
}
async function assertSelected(scene, id) {
    const state = await evaluate(`(()=>({selected:document.querySelector('#cpo-explorer-app').dataset.selected,view:document.querySelector('#cpo-explorer-app').dataset.view,drawer:document.querySelector('#cpo-research-drawer').classList.contains('is-open'),activeComponent:document.querySelector('#cpo-scene-${scene} .cpo-component[data-component-id="${id}"]')?.classList.contains('is-active'),activeCallout:document.querySelector('#cpo-scene-${scene} .cpo-callout[data-component-id="${id}"]')?.classList.contains('is-active'),childCards:document.querySelectorAll('#cpo-drawer-content .cpo-child-card').length,text:document.querySelector('#cpo-drawer-content')?.innerText??''}))()`);
    assert(state.selected === id && state.view === scene && state.drawer && state.activeComponent && state.activeCallout, `${scene}/${id} selected state did not synchronize`);
    assert(state.childCards === childCounts.get(id), `${scene}/${id} child part count mismatch: ${state.childCards}`);
    assert(state.text.includes('暂无已核验材料数据'), `${scene}/${id} material gap text missing`);
    assert(!/SiN|LNOI|国产化率|BOM|market share|投资逻辑/.test(state.text), `${scene}/${id} leaked unsupported factual/prototype text`);
}
async function assertIdle() {
    const state = await evaluate(`(()=>({selected:document.querySelector('#cpo-explorer-app').dataset.selected, drawer:document.querySelector('#cpo-research-drawer').classList.contains('is-open')}))()`);
    assert(state.selected === '' && !state.drawer, 'Explorer did not reset to overview');
}
async function assertVisibleCallout(scene, id) {
    const state = await evaluate(`(()=>{const callout=document.querySelector('#cpo-scene-${scene} .cpo-callout[data-component-id="${id}"]');const card=callout.querySelector('.cpo-callout-card');const drawer=document.querySelector('#cpo-research-drawer');const rect=card.getBoundingClientRect();const drawerRect=drawer.getBoundingClientRect();const x=rect.left+rect.width/2;const y=rect.top+rect.height/2;const top=document.elementFromPoint(x,y);return{right:rect.right,left:rect.left,top:rect.top,width:rect.width,height:rect.height,drawerLeft:drawerRect.left,hit:!!top?.closest('#cpo-scene-${scene} .cpo-callout[data-component-id="${id}"]')}})()`);
    assert(state.width > 20 && state.height > 20 && state.left >= 0 && state.top >= 0, `${scene}/${id} callout card is not visible`);
    assert(state.right <= state.drawerLeft, `${scene}/${id} callout card is covered by drawer: right ${state.right}, drawerLeft ${state.drawerLeft}`);
    assert(state.hit, `${scene}/${id} callout is not top-most pointer target`);
}
async function exerciseFullCoverage() {
    for (const id of expectedModules) {
        await setView('flat');
        await hoverComponent('flat', id); await assertHoverPair('flat', id); await clearHover('flat', '.cpo-component', id);
        await hoverCallout('flat', id); await assertHoverPair('flat', id); await clearHover('flat', '.cpo-callout', id);
        await clickComponent('flat', id); await waitDrawer(id); await assertSelected('flat', id); await assertVisibleCallout('flat', id);
        await clickComponent('flat', id); await assertIdle();

        await setView('three');
        await clickCallout('three', id); await waitDrawer(id); await assertSelected('three', id); await assertVisibleCallout('three', id);
        await setView('flat'); await assertSelected('flat', id);
        await esc(); await assertIdle();
    }
}
async function assertKeyboardAndBlankReset() {
    await setView('three');
    await keySelect('three', 'cpo.mod.pic', 'Enter'); await waitDrawer('cpo.mod.pic'); await assertSelected('three', 'cpo.mod.pic');
    await clickBlank(); await assertIdle();
    await keySelect('three', 'cpo.mod.pic', ' '); await waitDrawer('cpo.mod.pic'); await assertSelected('three', 'cpo.mod.pic');
    await esc(); await assertIdle();
}
async function runViewportEvidence(width, height, suffix) {
    await viewport(width, height);
    await navigate(`${base}/`);
    await waitReady();
    await assertResearchShell('CPO Explorer');
    await assertCoverage();

    await setView('flat'); await assertGeometryOwnership('flat'); await screenshot(`idle-flat-${suffix}.png`);
    await hoverComponent('flat', 'cpo.mod.pic'); await assertHoverPair('flat', 'cpo.mod.pic'); await screenshot(`hover-flat-pic-${suffix}.png`); await clearHover('flat', '.cpo-component', 'cpo.mod.pic');
    await clickComponent('flat', 'cpo.mod.host-asic'); await waitDrawer('cpo.mod.host-asic'); await assertSelected('flat', 'cpo.mod.host-asic'); await sleep(360); await screenshot(`selected-flat-host-asic-${suffix}.png`);
    await setView('three'); await assertSelected('three', 'cpo.mod.host-asic'); await sleep(360); await screenshot(`view-switch-host-asic-${suffix}.png`);
    await esc(); await assertIdle();

    await setView('three'); await assertGeometryOwnership('three'); await screenshot(`idle-3d-${suffix}.png`);
    await hoverCallout('three', 'cpo.mod.laser'); await assertHoverPair('three', 'cpo.mod.laser'); await screenshot(`hover-3d-laser-${suffix}.png`); await clearHover('three', '.cpo-callout', 'cpo.mod.laser');
    await clickCallout('three', 'cpo.mod.fiber-interface'); await waitDrawer('cpo.mod.fiber-interface'); await assertSelected('three', 'cpo.mod.fiber-interface'); await sleep(360); await screenshot(`selected-3d-fiber-interface-${suffix}.png`);
    await clickBlank(); await assertIdle(); await sleep(360); await screenshot(`reset-blank-${suffix}.png`);
}

await runViewportEvidence(1440, 980, '1440');
await exerciseFullCoverage();
await assertKeyboardAndBlankReset();
await runViewportEvidence(1920, 1080, '1920');
await assertR2RegressionSurface();

await command('session.end', {});
ws.close();
console.log(`R4 Explorer browser smoke passed; screenshots written to ${screenshotDir}`);
JS

node "$SCRIPT" "$PORT" "$BIDI" "$SCREENSHOT_DIR"
if grep -Eq 'Unhandled exception|System.InvalidOperationException' "$KLOG"; then
    echo "Unexpected unhandled/internal failure during R4 browser smoke" >&2
    grep -n -C 4 -E 'Unhandled exception|System.InvalidOperationException' "$KLOG" >&2 || true
    exit 1
fi
