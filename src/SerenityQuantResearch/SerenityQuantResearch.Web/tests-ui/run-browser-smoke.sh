#!/usr/bin/env bash
set -euo pipefail

command -v firefox >/dev/null || { echo "Firefox is required for the R2 browser smoke" >&2; exit 1; }

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
DB="/tmp/serenity-r2-shell-ui-$$.sqlite"
KLOG="/tmp/serenity-r2-shell-ui-$$.kestrel.log"
FLOG="/tmp/serenity-r2-shell-ui-$$.firefox.log"
PROFILE="/tmp/serenity-r2-shell-ui-profile-$$"
SCRIPT="/tmp/serenity-r2-shell-ui-$$.mjs"
SCREENSHOT_DIR="${UI_SCREENSHOT_DIR:-$ROOT/operations/reviews/research-experience-reboot-r2-screenshots}"
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
    for (let attempt = 0; attempt < 120; attempt++) {
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

await viewport(1440);
await navigate(`${base}/`);
await waitFor(`document.querySelector('[data-testid="research-primary-nav"]') && document.querySelector('#cpo-research-app')`, 'root research shell');
await assertResearchShell('CPO Explorer');
await screenshot('root-cpo-shell-1440.png');

await viewport(1920, 1080);
await navigate(`${base}/`);
await waitFor(`document.querySelector('[data-testid="research-primary-nav"]') && document.querySelector('#cpo-research-app')`, 'root research shell 1920');
await assertResearchShell('CPO Explorer');
await screenshot('root-cpo-shell-1920.png');

await viewport(1440);
await navigate(`${base}/Research/Companies`);
await waitFor(`document.querySelector('[data-testid="research-primary-nav"]') && document.querySelector('#company-research-app')`, 'company research shell');
await assertResearchShell('Company Pool');
await screenshot('company-pool-shell-1440.png');

await viewport(1920, 1080);
await navigate(`${base}/Research/Companies`);
await waitFor(`document.querySelector('[data-testid="research-primary-nav"]') && document.querySelector('#company-research-app')`, 'company research shell 1920');
await assertResearchShell('Company Pool');
await screenshot('company-pool-shell-1920.png');

await navigate(`${base}/Research/Workspace`);
await waitFor(`document.querySelector('[data-testid="research-primary-nav"]') && document.querySelector('.research-placeholder')`, 'workspace placeholder route');
await assertResearchShell('Research Workspace');
let state = await evaluate(`({text:document.querySelector('.research-placeholder')?.innerText??'',writeControls:[...document.querySelectorAll('button,a,input,textarea')].map(x=>x.textContent || x.getAttribute('aria-label') || x.name || '').join('\\n')})`);
assert(state.text.includes('does not provide writing') || state.text.includes('不提供写入'), 'workspace placeholder must state no writing');
assert(!/New Note|Graph|ResearchNote/.test(state.writeControls), 'deferred workspace controls leaked into R2 placeholder');

await navigate(`${base}/Administration/User`);
await waitFor(`document.querySelector('#s-sidebar') && !document.querySelector('[data-testid="research-primary-nav"]')`, 'secondary admin route shell separation');
state = await evaluate(`({path:location.pathname,sidebar:!!document.querySelector('#s-sidebar'),researchNav:!!document.querySelector('[data-testid="research-primary-nav"]'),body:document.body.innerText})`);
assert(state.path === '/Administration/User' && state.sidebar && !state.researchNav, 'secondary admin route did not remain available outside research primary nav');
await screenshot('secondary-admin-route-1440.png');

await navigate(`${base}/Research/Companies`);
state = await evaluate(`(async()=>{const token=()=>decodeURIComponent(document.cookie.match(/(?:^|; )CSRF-TOKEN=([^;]+)/)[1]);const response=await fetch('/Services/Administration/User/List',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-TOKEN':token()},body:'{}'});return{status:response.status,count:(await response.json()).Entities?.length??0}})()`, true);
assert(state.status === 200 && state.count >= 1, 'secondary admin service route not reachable in Open Access maintenance mode');

await command('session.end', {});
ws.close();
console.log(`R2 browser shell smoke passed; screenshots written to ${screenshotDir}`);
JS

node "$SCRIPT" "$PORT" "$BIDI" "$SCREENSHOT_DIR"
if grep -Eq 'Unhandled exception|System.InvalidOperationException' "$KLOG"; then
    echo "Unexpected unhandled/internal failure during R2 browser smoke" >&2
    grep -n -C 4 -E 'Unhandled exception|System.InvalidOperationException' "$KLOG" >&2 || true
    exit 1
fi
