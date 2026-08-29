#!/usr/bin/env bash
set -euo pipefail

command -v firefox >/dev/null || { echo "Firefox is required for the R3 browser smoke" >&2; exit 1; }

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
DB="/tmp/serenity-r3-explorer-ui-$$.sqlite"
KLOG="/tmp/serenity-r3-explorer-ui-$$.kestrel.log"
FLOG="/tmp/serenity-r3-explorer-ui-$$.firefox.log"
PROFILE="/tmp/serenity-r3-explorer-ui-profile-$$"
SCRIPT="/tmp/serenity-r3-explorer-ui-$$.mjs"
SCREENSHOT_DIR="${UI_SCREENSHOT_DIR:-$ROOT/operations/reviews/research-experience-reboot-r3-screenshots}"
mkdir -p "$PROFILE" "$SCREENSHOT_DIR"

cleanup() {
    kill "${FIREFOX_PID:-0}" "${APP_PID:-0}" 2>/dev/null || true
    wait "${FIREFOX_PID:-0}" 2>/dev/null || true
    wait "${APP_PID:-0}" 2>/dev/null || true
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
    const response = await command('script.evaluate', {
        expression: wrapped, target: { context }, awaitPromise, resultOwnership: 'none'
    });
    const result = response.result?.result;
    if (result?.type !== 'string') throw new Error(JSON.stringify(response));
    return JSON.parse(result.value);
}
async function waitFor(expression, label) {
    for (let attempt = 0; attempt < 160; attempt++) {
        if (await evaluate(expression)) return;
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error(`Timeout: ${label}`);
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
    let state = await evaluate(`({text:document.querySelector('.research-placeholder')?.innerText??'',writeControls:[...document.querySelectorAll('button,a,input,textarea')].map(x=>x.textContent || x.getAttribute('aria-label') || x.name || '').join('\\\\n')})`);
    assert(state.text.includes('does not provide writing') || state.text.includes('不提供写入'), 'workspace placeholder must state no writing');
    assert(!/New Note|Graph|ResearchNote/.test(state.writeControls), 'deferred workspace controls leaked into placeholder');

    await navigate(`${base}/Administration/User`);
    await waitFor(`document.querySelector('#s-sidebar') && !document.querySelector('[data-testid="research-primary-nav"]')`, 'secondary admin route shell separation');
    state = await evaluate(`({path:location.pathname,sidebar:!!document.querySelector('#s-sidebar'),researchNav:!!document.querySelector('[data-testid="research-primary-nav"]'),body:document.body.innerText})`);
    assert(state.path === '/Administration/User' && state.sidebar && !state.researchNav, 'secondary admin route did not remain available outside research primary nav');

    await navigate(`${base}/Research/Companies`);
    state = await evaluate(`(async()=>{const token=()=>decodeURIComponent(document.cookie.match(/(?:^|; )CSRF-TOKEN=([^;]+)/)[1]);const response=await fetch('/Services/Administration/User/List',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-TOKEN':token()},body:'{}'});return{status:response.status,count:(await response.json()).Entities?.length??0}})()`, true);
    assert(state.status === 200 && state.count >= 1, 'secondary admin service route not reachable in Open Access maintenance mode');
}
const act = async expression => evaluate(`(()=>{${expression};return true})()`);
const waitReady = () => waitFor(`document.querySelector('#cpo-explorer-app')?.dataset.ready === 'true'`, 'R3 explorer ready');
const waitDrawer = () => waitFor(`document.querySelector('#cpo-research-drawer.is-open') && document.body.innerText.includes('光调制器') && document.body.innerText.includes('暂无已核验材料数据')`, 'SiPh drawer content');
const selectComponent = async scene => {
    await act(`document.querySelector('#cpo-scene-${scene} .cpo-component').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))`);
    await waitDrawer();
};
const hoverComponent = async scene => act(`document.querySelector('#cpo-scene-${scene} .cpo-component').dispatchEvent(new MouseEvent('mouseenter',{bubbles:false,cancelable:true}))`);
const hoverCallout = async scene => act(`document.querySelector('#cpo-scene-${scene} .cpo-callout').dispatchEvent(new MouseEvent('mouseenter',{bubbles:false,cancelable:true}))`);
const clearComponentHover = async scene => act(`document.querySelector('#cpo-scene-${scene} .cpo-component').dispatchEvent(new MouseEvent('mouseleave',{bubbles:false,cancelable:true}))`);
const clearCalloutHover = async scene => act(`document.querySelector('#cpo-scene-${scene} .cpo-callout').dispatchEvent(new MouseEvent('mouseleave',{bubbles:false,cancelable:true}))`);
const clickCallout = async scene => act(`document.querySelector('#cpo-scene-${scene} .cpo-callout').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))`);
const clickBlank = async () => act(`document.querySelector('#cpo-canvas-frame').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))`);
const esc = async () => act(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}))`);
const keySelect = async (scene, key = 'Enter') => act(`const el=document.querySelector('#cpo-scene-${scene} .cpo-component');el.focus();if(document.activeElement!==el)throw new Error('component did not receive keyboard focus');document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'${key}',bubbles:true,cancelable:true}))`);
const setView = async view => act(`document.querySelector('#cpo-view-${view}').click()`);
async function assertIdle() {
    const state = await evaluate(`(()=>({selected:document.querySelector('#cpo-explorer-app').dataset.selected, drawer:document.querySelector('#cpo-research-drawer').classList.contains('is-open')}))()`);
    assert(state.selected === '' && !state.drawer, 'Explorer did not reset to overview');
}
async function assertSelected(expectedView) {
    const state = await evaluate(`(()=>({selected:document.querySelector('#cpo-explorer-app').dataset.selected, view:document.querySelector('#cpo-explorer-app').dataset.view, drawer:document.querySelector('#cpo-research-drawer').classList.contains('is-open'), activeComponent:document.querySelector('#cpo-scene-' + document.querySelector('#cpo-explorer-app').dataset.view + ' .cpo-component')?.classList.contains('is-active'), activeCallout:document.querySelector('#cpo-scene-' + document.querySelector('#cpo-explorer-app').dataset.view + ' .cpo-callout')?.classList.contains('is-active')}))()`);
    assert(state.selected === 'cpo.mod.pic', `expected cpo.mod.pic selected, got ${state.selected}`);
    assert(state.view === expectedView, `expected view ${expectedView}, got ${state.view}`);
    assert(state.drawer && state.activeComponent && state.activeCallout, 'selected state did not synchronize component/callout/drawer');
}
async function assertMaterialAndCompanySafety() {
    const state = await evaluate(`(()=>{const drawer=document.querySelector('#cpo-drawer-content');return{text:drawer.innerText,techBadges:[...drawer.querySelectorAll('.cpo-badge.is-link')].map(x=>x.textContent.trim())}})()`);
    assert(state.text.includes('暂无已核验材料数据'), 'material reviewed-gap text missing');
    assert(state.text.includes('尚无 SiPh PIC 或其子部件的显式公司暴露映射'), 'safe company empty state missing');
    assert(state.text.includes('光调制器') && state.text.includes('WDM 复用/解复用') && state.text.includes('波导与片上耦合结构'), 'real SiPh child parts missing');
    assert(state.techBadges.includes('硅光集成'), 'authoritative part→technology context missing');
    assert(!state.techBadges.some(x => /SiN|LNOI|Silicon\b/.test(x)), 'prototype material chip leaked into technology badges');
}
async function assertHitOwnershipAndNoBlueComponentOutline() {
    const state = await evaluate(`(()=>{const flat=document.querySelector('#cpo-scene-flat .cpo-component');const box=flat.getBBox();const three=document.querySelector('#cpo-scene-three .cpo-component');const threeStroke=getComputedStyle(three.querySelector('polygon')).stroke;const outline=getComputedStyle(three).outlineColor;return{hitOwner:flat.dataset.hitOwner,width:box.width,height:box.height,stroke:threeStroke,outline}})()`);
    assert(state.hitOwner === 'real-geometry', 'flat SiPh hit owner is not real geometry');
    assert(state.width < 220 && state.height < 110, `flat SiPh hit box too broad: ${state.width}x${state.height}`);
    assert(!/49, 85, 207/.test(`${state.stroke} ${state.outline}`), `component uses strong blue outline: ${state.stroke} / ${state.outline}`);
}
async function assertVisibleCalloutHit(scene) {
    const state = await evaluate(`(()=>{const callout=document.querySelector('#cpo-scene-${scene} .cpo-callout');const card=callout.querySelector('.cpo-callout-card');const drawer=document.querySelector('#cpo-research-drawer');const rect=card.getBoundingClientRect();const drawerRect=drawer.getBoundingClientRect();const x=rect.left + rect.width / 2;const y=rect.top + rect.height / 2;const top=document.elementFromPoint(x,y);return{right:rect.right,drawerLeft:drawerRect.left,hit:!!top?.closest('#cpo-scene-${scene} .cpo-callout'),visible:rect.width>20 && rect.height>20 && rect.left>=0 && rect.top>=0}})()`);
    assert(state.visible, `${scene} callout card is not visible in selected state`);
    assert(state.right <= state.drawerLeft, `${scene} callout card is covered by drawer: right ${state.right}, drawerLeft ${state.drawerLeft}`);
    assert(state.hit, `${scene} callout is not top-most pointer target`);
}
async function assertHoverPair(scene) {
    const hover = await evaluate(`(()=>({component:document.querySelector('#cpo-scene-${scene} .cpo-component').classList.contains('is-hovered'),callout:document.querySelector('#cpo-scene-${scene} .cpo-callout').classList.contains('is-hovered'),line:document.querySelector('#cpo-state-line').innerText}))()`);
    assert(hover.component && hover.callout, `${scene} hover did not focus paired component/callout`);
    assert(hover.line.includes('hover preview') && !hover.line.includes('selected'), `${scene} hover was announced as selected`);
}
async function runViewportEvidence(width, height, suffix) {
    await viewport(width, height);
    await navigate(`${base}/`);
    await waitReady();
    await assertResearchShell('CPO Explorer');
    await assertHitOwnershipAndNoBlueComponentOutline();

    await setView('flat');
    await assertIdle();
    await screenshot(`idle-flat-${suffix}.png`);
    await hoverComponent('flat');
    await assertHoverPair('flat');
    await screenshot(`hover-flat-${suffix}.png`);
    await clearComponentHover('flat');
    await hoverCallout('flat');
    await assertHoverPair('flat');
    await clearCalloutHover('flat');
    await selectComponent('flat');
    await assertSelected('flat');
    await assertMaterialAndCompanySafety();
    await sleep(360);
    await screenshot(`selected-flat-${suffix}.png`);
    await clickBlank();
    await assertIdle();
    await sleep(360);
    await screenshot(`reset-blank-flat-${suffix}.png`);

    await setView('three');
    await screenshot(`idle-3d-${suffix}.png`);
    await hoverComponent('three');
    await assertHoverPair('three');
    await screenshot(`hover-3d-${suffix}.png`);
    await clearComponentHover('three');
    await hoverCallout('three');
    await assertHoverPair('three');
    await clearCalloutHover('three');
    await selectComponent('three');
    await assertSelected('three');
    await sleep(360);
    await assertVisibleCalloutHit('three');
    await screenshot(`selected-3d-${suffix}.png`);

    await setView('flat');
    await assertSelected('flat');
    await sleep(360);
    await screenshot(`view-switch-preserved-${suffix}.png`);
    await esc();
    await assertIdle();
    await sleep(360);
    await screenshot(`reset-esc-${suffix}.png`);
}

await runViewportEvidence(1440, 980, '1440');
await runViewportEvidence(1920, 1080, '1920');

await viewport(1440, 980);
await navigate(`${base}/`);
await waitReady();
await setView('three');
await selectComponent('three');
await sleep(360);
await screenshot('sequence-component-selected-1440.png');
await clickCallout('three');
await assertIdle();
await sleep(360);
await screenshot('sequence-same-callout-reset-1440.png');
await clickCallout('three');
await waitDrawer();
await assertSelected('three');
await sleep(360);
await screenshot('sequence-callout-selected-1440.png');
await act(`document.querySelector('#cpo-close-drawer').click()`);
await assertIdle();
await sleep(360);
await screenshot('sequence-close-reset-1440.png');
await keySelect('three', 'Enter');
await waitDrawer();
await assertSelected('three');
await sleep(360);
await screenshot('sequence-keyboard-enter-selected-1440.png');
await esc();
await assertIdle();
await sleep(360);
await screenshot('sequence-keyboard-esc-reset-1440.png');
await keySelect('three', ' ');
await waitDrawer();
await assertSelected('three');
await sleep(360);
await screenshot('sequence-keyboard-space-selected-1440.png');
await esc();
await assertIdle();

await assertR2RegressionSurface();

await command('session.end', {});
ws.close();
console.log(`R3 Explorer browser smoke passed; screenshots written to ${screenshotDir}`);
JS

node "$SCRIPT" "$PORT" "$BIDI" "$SCREENSHOT_DIR"
if grep -Eq 'Unhandled exception|System.InvalidOperationException' "$KLOG"; then
    echo "Unexpected unhandled/internal failure during R3 browser smoke" >&2
    grep -n -C 4 -E 'Unhandled exception|System.InvalidOperationException' "$KLOG" >&2 || true
    exit 1
fi
