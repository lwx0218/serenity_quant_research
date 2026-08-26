#!/usr/bin/env bash
set -euo pipefail

command -v firefox >/dev/null || { echo "Firefox is required for the Phase 1 browser smoke" >&2; exit 1; }

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
DB="/tmp/serenity-phase1-ui-$$.sqlite"
KLOG="/tmp/serenity-phase1-ui-$$.kestrel.log"
FLOG="/tmp/serenity-phase1-ui-$$.firefox.log"
PROFILE="/tmp/serenity-phase1-ui-profile-$$"
SCRIPT="/tmp/serenity-phase1-ui-$$.mjs"
mkdir -p "$PROFILE"

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
BackgroundJobs__Enabled=false ClamAV__Enabled=false StartNodeScripts='' \
dotnet run --no-build --project src/SerenityQuantResearch/SerenityQuantResearch.Web/SerenityQuantResearch.Web.csproj \
    --urls "http://127.0.0.1:$PORT" >"$KLOG" 2>&1 &
APP_PID=$!
for _ in $(seq 1 80); do
    curl -fsS "http://127.0.0.1:$PORT/Account/Login" >/dev/null 2>&1 && break
    kill -0 "$APP_PID" 2>/dev/null || { tail -80 "$KLOG"; exit 1; }
    sleep .25
done
curl -fsS "http://127.0.0.1:$PORT/Account/Login" >/dev/null

firefox --headless --no-remote --profile "$PROFILE" --remote-debugging-port "$BIDI" about:blank >"$FLOG" 2>&1 &
FIREFOX_PID=$!
for _ in $(seq 1 80); do
    grep -q 'WebDriver BiDi listening' "$FLOG" && break
    kill -0 "$FIREFOX_PID" 2>/dev/null || { tail -80 "$FLOG"; exit 1; }
    sleep .25
done
grep -q 'WebDriver BiDi listening' "$FLOG"

cat >"$SCRIPT" <<'JS'
const [port, bidi] = process.argv.slice(2);
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
    for (let attempt = 0; attempt < 120; attempt++) {
        if (await evaluate(expression)) return;
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error(`Timeout: ${label}`);
}
async function center(selector) {
    return evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});if(!e)return null;const r=e.getBoundingClientRect();return{x:Math.round(r.left+r.width/2),y:Math.round(r.top+r.height/2)}})()`);
}
async function pointer(selector, click = false) {
    const point = await center(selector);
    if (!point) throw new Error(`Missing element: ${selector}`);
    const actions = [{ type: 'pointerMove', x: point.x, y: point.y, origin: 'viewport', duration: 0 }];
    if (click) actions.push({ type: 'pointerDown', button: 0 }, { type: 'pointerUp', button: 0 });
    await command('input.performActions', { context, actions: [{ type: 'pointer', id: `mouse-${Date.now()}`, parameters: { pointerType: 'mouse' }, actions }] });
}
async function key(value) {
    await command('input.performActions', { context, actions: [{ type: 'key', id: `key-${Date.now()}`, actions: [{ type: 'keyDown', value }, { type: 'keyUp', value }] }] });
}
function assert(condition, message) { if (!condition) throw new Error(message); }

await command('browsingContext.setViewport', { context, viewport: { width: 1280, height: 900 }, devicePixelRatio: 1 });
await navigate(`${base}/Research/Companies`);
let state = await evaluate(`({path:location.pathname,open:!!document.querySelector('[aria-label="免登录开放模式"]')})`);
assert(state.path==='/Research/Companies' && state.open, 'Open-access company universe failed');
state = await evaluate(`(async()=>{const token=()=>decodeURIComponent(document.cookie.match(/(?:^|; )CSRF-TOKEN=([^;]+)/)[1]);const response=await fetch('/Services/Administration/User/List',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-TOKEN':token()},body:'{}'});return{status:response.status,count:(await response.json()).Entities?.length??0}})()`, true);
assert(state.status===200 && state.count>=1, 'Open-access administration service failed');
await navigate(`${base}/Research/Cpo`);
await waitFor(`document.querySelectorAll('#cpo-diagram [data-part-id]').length===21`, 'catalog render');
state = await evaluate(`({svg:document.querySelectorAll('#cpo-diagram [data-part-id]').length,table:document.querySelectorAll('#cpo-part-tree [data-part-id]').length,modules:document.querySelectorAll('.cpo-module-layer').length})`);
assert(state.svg === 21 && state.table === 21 && state.modules === 9, '9 module / 21 part wiring failed');

const pic = '[data-part-id="cpo.part.pic.modulator"]';
const asic = '[data-part-id="cpo.part.host-asic.switch-die"]';
await pointer(`#cpo-diagram ${pic}`);
await waitFor(`document.querySelectorAll('.cpo-module-layer.is-dimmed').length===8`, 'hover dimming');
state = await evaluate(`({active:document.querySelectorAll('.cpo-module-layer.is-active').length,dim:document.querySelectorAll('.cpo-module-layer.is-dimmed').length})`);
assert(state.active === 1 && state.dim === 8, 'hover/dimming failed');
await pointer(`#cpo-diagram ${pic}`, true);
await waitFor(`document.querySelector('#cpo-drawer-content h2')?.textContent==='光调制器'`, 'drawer render');
state = await evaluate(`({locked:document.querySelector('#cpo-diagram ${pic}').classList.contains('is-locked'),text:document.querySelector('#cpo-drawer-content').innerText})`);
for (const section of ['边界','上游 / 下游','关键规格','产业链节点','技术链接','候选公司','证据','研究结论','风险','状态警告','未决问题'])
    assert(state.text.includes(section), `Missing drawer section: ${section}`);
assert(state.locked, 'click lock failed');

await evaluate(`(()=>{document.querySelector('#cpo-clear-selection').click();return true})()`);
await waitFor(`document.querySelector('#cpo-research-drawer').hidden`, 'clear selection');
state = await evaluate(`({dim:document.querySelectorAll('.cpo-module-layer.is-dimmed').length,locked:document.querySelectorAll('.is-locked').length,expanded:document.querySelector('#cpo-diagram ${pic}').getAttribute('aria-expanded'),focus:document.activeElement?.dataset?.partId})`);
assert(state.dim === 0 && state.locked === 0 && state.expanded === 'false' && state.focus === 'cpo.part.pic.modulator', 'clear ARIA/focus state failed');

await evaluate(`(()=>{document.querySelector('#cpo-diagram ${asic}').focus();return true})()`);
await key('\uE007');
await waitFor(`document.querySelector('#cpo-drawer-content h2')?.textContent==='交换 ASIC 裸片/封装'`, 'Enter selection');
state = await evaluate(`({text:document.querySelector('#cpo-drawer-content').innerText,pressed:document.querySelector('#cpo-diagram ${asic}').getAttribute('aria-pressed')})`);
assert(state.pressed === 'true' && state.text.includes('Broadcom Inc.') && state.text.includes('candidate') && state.text.includes('draft'), 'Enter/company/evidence states failed');
await key('\uE00C');
await waitFor(`document.querySelector('#cpo-research-drawer').hidden`, 'Escape clear');
await evaluate(`(()=>{document.querySelector('#cpo-diagram ${asic}').focus();return true})()`);
await key(' ');
await waitFor(`!document.querySelector('#cpo-research-drawer').hidden`, 'Space selection');
await key('\uE00C');
await waitFor(`document.querySelector('#cpo-research-drawer').hidden`, 'second Escape');

await evaluate(`(()=>{const e=document.querySelector('#cpo-part-tree ${pic}');e.closest('details').open=true;e.focus();return true})()`);
await key('\uE007');
await waitFor(`document.querySelector('#cpo-drawer-content h2')?.textContent==='光调制器'`, 'fallback selection');
await pointer('#cpo-close-drawer', true);
await waitFor(`document.querySelector('#cpo-research-drawer').hidden`, 'close button');
state = await evaluate(`({focus:document.activeElement?.dataset?.partId,expanded:document.querySelector('#cpo-part-tree ${pic}').getAttribute('aria-expanded'),dim:document.querySelectorAll('.cpo-module-layer.is-dimmed').length})`);
assert(state.focus === 'cpo.part.pic.modulator' && state.expanded === 'false' && state.dim === 0, 'fallback focus restoration failed');

await navigate(`${base}/Research/Parts/cpo.part.host-asic.switch-die`);
await waitFor(`document.querySelector('#cpo-detail-content h2')?.textContent==='交换 ASIC 裸片/封装'`, 'detail render');
state = await evaluate(`({text:document.querySelector('#cpo-detail-content').innerText})`);
for (const section of ['边界','上游 / 下游','关键规格','研究结论','风险']) assert(state.text.includes(section), `Missing detail section: ${section}`);
assert(state.text.includes('candidate') && state.text.includes('draft'), 'detail states failed');

await navigate(`${base}/Research/Parts/cpo.part.does-not-exist`);
await waitFor(`document.querySelector('#cpo-detail-content .alert-danger')`, 'detail error state');

// P3 company universe: real SleekGrid, native fallback, all 20 stable IDs, server filters and comparison.
const companyIds = ['global.nvidia','global.broadcom','global.cisco','global.intel','global.marvell','global.coherent','global.lumentum','global.arista','cn.300308','cn.300502','cn.002281','cn.300394','cn.000988','cn.603083','cn.688498','cn.688048','cn.002916','cn.002463','cn.300602','cn.688200'];
await navigate(`${base}/Research/Companies`);
await waitFor(`document.querySelectorAll('#company-table-body tr[data-company-id]').length===20`, '20 company universe render');
state = await evaluate(`(()=>{const ids=[...document.querySelectorAll('#company-table-body tr[data-company-id]')].map(x=>x.dataset.companyId);const start=document.querySelector('.sg-start.slick-header-columns');return{ids,unique:new Set(ids).size,gridCells:document.querySelectorAll('#company-grid .slick-cell').length,headers:document.querySelectorAll('#company-grid .slick-header-column').length,startHeaders:start?.querySelectorAll('.slick-header-column').length??0,startX:start?.getBoundingClientRect().x??-1}})()`);
assert(JSON.stringify([...state.ids].sort())===JSON.stringify([...companyIds].sort()) && state.unique===20, 'exact 20 stable company IDs failed');
assert(state.gridCells>0 && state.headers>=12 && state.startHeaders===3, 'SleekGrid FrozenLayout did not pin exactly three identity columns');
const frozenStartX = state.startX;
state = await evaluate(`(async()=>{const viewport=document.querySelector('#company-grid .sg-body.sg-main.slick-viewport');viewport.scrollLeft=500;viewport.dispatchEvent(new Event('scroll'));await new Promise(requestAnimationFrame);return{scrollLeft:viewport.scrollLeft,startX:document.querySelector('.sg-start.slick-header-columns').getBoundingClientRect().x}})()`, true);
assert(state.scrollLeft>0 && Math.abs(state.startX-frozenStartX)<1, 'frozen identity columns moved during horizontal scroll');

await evaluate(`(()=>{const s=document.querySelector('#company-filters select[name="Exchange"]');s.value='NASDAQ';s.dispatchEvent(new Event('change',{bubbles:true}));return true})()`);
await waitFor(`document.querySelectorAll('#company-table-body tr[data-company-id]').length===6`, 'server exchange filter');
state = await evaluate(`([...document.querySelectorAll('#company-table-body tr[data-company-id]')].every(x=>x.children[3].textContent==='NASDAQ'))`);
assert(state, 'exchange filter returned non-NASDAQ company');
await evaluate(`(()=>{document.querySelector('#company-clear-filters').click();return true})()`);
await waitFor(`document.querySelectorAll('#company-table-body tr[data-company-id]').length===20`, 'clear company filters');

const compareSelector = '#company-table-body tr[data-company-id="global.nvidia"] .company-compare-check';
await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(compareSelector)});e.focus();return true})()`);
await key(' ');
await waitFor(`document.querySelector('#company-comparison-content')?.innerText.includes('NVIDIA Corporation')`, 'keyboard company comparison');
state = await evaluate(`({checked:document.querySelector(${JSON.stringify(compareSelector)}).checked,focus:document.activeElement===document.querySelector(${JSON.stringify(compareSelector)}),detail:document.querySelector('#company-comparison-content a')?.getAttribute('href')})`);
assert(state.checked && state.focus && state.detail.includes('/Research/Companies/global.nvidia'), 'comparison keyboard/detail navigation failed');

state = await evaluate(`(async()=>{const links=[...document.querySelectorAll('#company-table-body tr[data-company-id] td:nth-child(2) a')].map(x=>x.href);return await Promise.all(links.map(async href=>({href,status:(await fetch(href)).status})))})()`, true);
assert(state.length===20 && state.every(x=>x.status===200), 'not all 20 company detail page targets resolve');

// Broadcom detail: seven accessible tabs, candidate/draft visibility, cross navigation and policy rejection.
await navigate(`${base}/Research/Companies/global.broadcom`);
await waitFor(`document.querySelectorAll('[role="tab"]').length===7`, 'company detail tabs');
state = await evaluate(`({labels:[...document.querySelectorAll('[role="tab"]')].map(x=>x.textContent),candidate:document.querySelector('#company-detail-content').innerText.includes('Candidate / 候选（未核验）')})`);
assert(JSON.stringify(state.labels)===JSON.stringify(['Overview','Industry-chain Exposure','Earnings & Financial Evidence','Capex & Investment','Events','Research Conclusions','Sources & Audit']), 'frozen seven tabs failed');
assert(state.candidate, 'candidate state label not visible');
await evaluate(`(()=>{document.querySelector('[role="tab"][data-tab="overview"]').focus();return true})()`);
await key('\uE014');
await waitFor(`document.querySelector('[role="tab"][data-tab="exposure"]').getAttribute('aria-selected')==='true'`, 'ArrowRight accessible tab');
state = await evaluate(`({text:document.querySelector('#company-panel-exposure').innerText,part:document.querySelector('#company-panel-exposure a[href*="/Research/Parts/"]')?.href,node:document.querySelector('#company-panel-exposure a[href*="/Research/ChainNodes/"]')?.href})`);
assert(state.text.includes('Candidate / 候选（未核验）') && state.text.includes('Draft / 草稿（未审核）'), 'candidate/draft state labels failed');
assert(state.part && state.node, 'company part/chain cross-navigation links missing');
// Resolve current cross-navigation URLs without interpolating page content into script source.
state = await evaluate(`(async()=>{const p=document.querySelector('#company-panel-exposure a[href*="/Research/Parts/"]').href;const n=document.querySelector('#company-panel-exposure a[href*="/Research/ChainNodes/"]').href;return{part:(await fetch(p)).status,node:(await fetch(n)).status}})()`, true);
assert(state.part===200 && state.node===200, 'company part/chain targets do not resolve');

await evaluate(`(()=>{const d=document.querySelector('.company-exposure-editor');d.open=true;const s=d.querySelector('select[name="VerificationState"]');s.value='verified';d.querySelector('form').requestSubmit();return true})()`);
await waitFor(`document.querySelector('.company-editor-policy.is-error')`, 'candidate to verified policy rejection');
state = await evaluate(`({error:document.querySelector('.company-editor-policy.is-error').textContent,candidate:document.querySelector('#company-panel-exposure').innerText.includes('Candidate / 候选（未核验）')})`);
assert(state.candidate && state.error.length>0, 'UI did not surface verified-evidence policy rejection');
state = await evaluate(`(async()=>{const token=()=>decodeURIComponent(document.cookie.match(/(?:^|; )CSRF-TOKEN=([^;]+)/)[1]);const post=async(path,body)=>fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-TOKEN':token()},body:JSON.stringify(body)});const before=await (await post('/Services/Research/CompanyUniverse/Retrieve',{CompanyId:'global.broadcom'})).json();const e=before.Company.Exposures[0];const denied=await post('/Services/Research/CompanyExposure/Update',{ExposureId:e.ExposureId,CompanyId:'global.broadcom',PartId:e.Part.Id,ChainNodeId:e.ChainNode.Id,Role:e.Role,Relevance:e.Relevance,Confidence:e.Confidence,VerificationState:'verified',ScopeNote:e.ScopeNote});const error=await denied.json();const after=await (await post('/Services/Research/CompanyUniverse/Retrieve',{CompanyId:'global.broadcom'})).json();return{status:denied.status,code:error.Error?.Code??error.error?.code,state:after.Company.Exposures[0].VerificationState,draft:after.Company.Exposures[0].ContextEvidence.some(x=>x.EvidenceId==='EVD-2026-0001'&&x.ReviewState==='draft')}})()`, true);
assert(state.status===400 && state.code==='VerifiedExposureEvidenceRequired' && state.state==='candidate' && state.draft, 'structured 4xx policy rejection contract failed');
await navigate(`${base}/Research/Companies/global.broadcom`);
await waitFor(`document.querySelectorAll('[role="tab"]').length===7`, 'Broadcom reload after rejected promotion');
await evaluate(`(()=>{document.querySelector('[role="tab"][data-tab="exposure"]').click();return true})()`);
state = await evaluate(`({text:document.querySelector('#company-panel-exposure').innerText})`);
assert(state.text.includes('Candidate / 候选（未核验）') && state.text.includes('Draft / 草稿（未审核）'), 'rejected promotion mutated candidate/draft state');

await navigate(`${base}/Research/ChainNodes/cpo.chain.asic`);
await waitFor(`document.querySelector('#company-detail-content h2')?.textContent==='交换 ASIC'`, 'chain node detail');
state = await evaluate(`({text:document.querySelector('#company-detail-content').innerText,company:document.querySelector('a[href*="/Research/Companies/global.broadcom"]')?.href,part:document.querySelector('a[href*="/Research/Parts/cpo.part.host-asic.switch-die"]')?.href})`);
assert(state.text.includes('Candidate / 候选（未核验）') && state.company && state.part, 'chain node cross-navigation/state failed');

await navigate(`${base}/Research/Companies?view=table`);
await waitFor(`document.querySelectorAll('#company-table-body tr[data-company-id]').length===20`, 'explicit table fallback');
state = await evaluate(`({gridHidden:document.querySelector('#company-grid').hidden,message:document.querySelector('#company-grid-error').textContent,keyboard:document.querySelectorAll('#company-table-body .company-compare-check').length})`);
assert(state.gridHidden && state.keyboard===20 && state.message.includes('fallback'), 'table fallback mode failed');

await command('session.end', {});
ws.close();
console.log('Browser UI smoke passed: P2 9/21 flow plus P3 SleekGrid, 20 companies, filters, keyboard comparison/tabs, fallback, policy and cross-navigation.');
JS

node "$SCRIPT" "$PORT" "$BIDI"
if grep -Eq 'Unhandled exception|System.InvalidOperationException' "$KLOG"; then
    echo "Unexpected unhandled/internal failure during browser smoke" >&2
    grep -n -C 4 -E 'Unhandled exception|System.InvalidOperationException' "$KLOG" >&2 || true
    exit 1
fi
