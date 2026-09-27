#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把整个 web 应用打成一个离线单文件：physical/dist/teardown-web-snapshot.html。
双击即开，hash 路由，API 数据内嵌（从一台正在跑的 API 抓下来），用来验 UX。

    cd api && uvicorn app.main:app --port 8000 &          # 先有一台 API（库里是什么数据，快照里就是什么）
    python3 tools/snapshot/build.py --api http://127.0.0.1:8000

做的事：
1. `VITE_HASH_ROUTER=1 vite build --base ./ --outDir dist-snapshot`（web/）
2. 按库里的 id 列表抓 /api/* 与 /physical/*.svg，存成一个 dict
3. 把 dist-snapshot/index.html 的 JS / CSS / 字体全部内联，前面插一段 fetch 桩：GET 查 dict；候选的确认 / 驳回在内存里挪一下；其他写操作返回 {}
需要 node / npm（web/ 已 npm install）和 Python 3.10+；不需要别的包。"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WEB = REPO / "web"
OUT = REPO / "physical" / "dist" / "teardown-web-snapshot.html"
sys.path.insert(0, str(REPO / "api"))

STUB = r"""
(function(){
  var SNAP=window.__SNAP__;
  function norm(u){ u=String(u); return u.replace(/^https?:\/\/[^/]+/,''); }
  function find(u){
    if(SNAP[u]!==undefined) return SNAP[u];
    var path=u.split('?')[0], qs=new URLSearchParams(u.split('?')[1]||'');
    if(path==='/api/companies'){ var q=(qs.get('q')||'').toLowerCase(); var all=JSON.parse(SNAP['/api/companies']); return JSON.stringify(q? all.filter(function(c){return [c.name,c.short_name,c.ticker,c.id].some(function(x){return x&&String(x).toLowerCase().indexOf(q)>=0;});}) : all); }
    if(path==='/api/links/suggest'){ var q2=(qs.get('q')||'').toLowerCase(); var all2=JSON.parse(SNAP['/api/links/suggest?q=']); return JSON.stringify(all2.filter(function(x){return !q2 || String(x.label).toLowerCase().indexOf(q2)>=0 || String(x.meta||'').toLowerCase().indexOf(q2)>=0;})); }
    for(var k in SNAP){ if(k.split('?')[0]===path) return SNAP[k]; }
    return null;
  }
  window.fetch=function(url, opts){
    var u=norm(url), method=(opts&&opts.method)||'GET';
    var body=find(u);
    if(method!=='GET'){
      var cm=u.match(/^\/api\/candidates\/([^/]+)\/(confirm|reject|reopen)$/);
      if(cm){
        for(var key in SNAP){ if(key.indexOf('/api/candidates?')===0){ var cur=JSON.parse(SNAP[key]);
          cur.items=cur.items.filter(function(c){return c.id!==decodeURIComponent(cm[1]);});
          cur.counts[cm[2]==='confirm'?'confirmed':'rejected']=(cur.counts[cm[2]==='confirm'?'confirmed':'rejected']||0)+1;
          if(cur.counts.pending_relevant) cur.counts.pending_relevant--; SNAP[key]=JSON.stringify(cur); } }
        return Promise.resolve(new Response(JSON.stringify({ok:true,event_id:'evt.snapshot'}),{status:200,statusText:'OK',headers:{'Content-Type':'application/json'}}));
      }
      var subj=u.replace(/^\/api\/(notes|verifications|events)\/?/,'').split('/')[0].split('?')[0];
      body = (u.indexOf('/api/notes/')===0 && SNAP['/api/notes/'+subj]) ? SNAP['/api/notes/'+subj] : '{}';
    }
    var ok=body!==null, text=ok?body:JSON.stringify({error:'not in snapshot',path:u});
    return Promise.resolve(new Response(text,{status: ok?200:404, statusText: ok?'OK':'Not Found', headers:{'Content-Type': /\.svg$/.test(u)?'image/svg+xml':'application/json'}}));
  };
})();
"""


def crawl(api: str) -> dict[str, str]:
    from app import config, db
    snap: dict[str, str] = {}

    def add(path: str) -> None:
        try:
            with urllib.request.urlopen(api + path, timeout=90) as r:
                if r.status == 200:
                    snap[path] = r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            print("  skip", path, e)

    with db.connect(config.DB_PATH) as conn:
        nodes = [r[0] for r in conn.execute("SELECT id FROM nodes")]
        modules = [r[0] for r in conn.execute("SELECT id FROM nodes WHERE kind='module'")]
        companies = [r[0] for r in conn.execute("SELECT id FROM companies")]
        chains = [r[0] for r in conn.execute("SELECT id FROM chain_nodes")]
        events = [r[0] for r in conn.execute("SELECT id FROM events WHERE status!='ignored'")]
        objects = [r[0] for r in conn.execute("SELECT id FROM physical_objects")]
    notes = [p.stem for p in (REPO / "data" / "notes").glob("*.md")]
    urls = ["/api/overview/cpo?days=7", "/api/products/cpo", "/api/chain", "/api/companies", "/api/baskets", "/api/notes",
            "/api/research/inbox?days=7", "/api/physical", "/api/links/suggest?q=", "/api/ingest/status",
            "/api/candidates?status=pending&limit=200&relevant=1", "/api/candidates?status=pending&limit=200&relevant=all"]
    urls += [f"/api/physical/{o}" for o in objects]
    urls += [f"/api/nodes/{n}" for n in nodes] + [f"/api/nodes/{n}/market?days=7" for n in nodes]
    urls += [f"/api/chain/{c}" for c in chains] + [f"/api/companies?chain={c}" for c in chains] + [f"/api/companies?node={n}" for n in nodes]
    urls += [f"/api/companies/{c}" for c in companies] + [f"/api/companies/{c}/market?months=6" for c in companies] + [f"/api/companies/{c}/physical" for c in companies]
    urls += [f"/api/events?company={c}&days=365&limit=200" for c in companies] + [f"/api/events/{e}/resonance" for e in events] + [f"/api/events/{e}" for e in events]
    urls += [f"/api/baskets/{m}?months=6" for m in modules] + [f"/api/notes/{s}" for s in notes]
    for u in urls:
        add(u)
    pub = WEB / "public" / "physical"
    for f in pub.iterdir():
        snap["/physical/" + f.name] = f.read_text(encoding="utf-8")
    print(f"snapshot: {len(snap)} entries, {sum(len(v) for v in snap.values()) / 1e6:.1f} MB")
    return snap


def build_web(dist: Path) -> None:
    env = {**os.environ, "VITE_HASH_ROUTER": "1"}
    subprocess.run(["npx", "vite", "build", "--base", "./", "--outDir", str(dist), "--emptyOutDir"], cwd=WEB, env=env, check=True)


def inline(dist: Path, snap: dict[str, str]) -> str:
    html = (dist / "index.html").read_text(encoding="utf-8")
    # 字体 → data URI
    def font_css(css: str) -> str:
        for fn in ("Geist-Variable.woff2", "GeistMono-Variable.woff2"):
            b = base64.b64encode((WEB / "public" / "fonts" / fn).read_bytes()).decode()
            css = re.sub(r'url\(["\']?[^)"\']*' + re.escape(fn) + r'["\']?\)', f'url("data:font/woff2;base64,{b}")', css)
        return css
    # CSS
    def css_repl(m):
        css = (dist / m.group(1).lstrip("./")).read_text(encoding="utf-8")
        return "<style>" + font_css(css) + "</style>"
    html = re.sub(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*>', css_repl, html)
    html = re.sub(r'<link[^>]+rel="preload"[^>]*>\s*', "", html)
    # JS（模块脚本内联；前面插数据与 fetch 桩）
    def js_repl(m):
        js = (dist / m.group(1).lstrip("./")).read_text(encoding="utf-8").replace("</script", "<\\/script")
        data = json.dumps(snap, ensure_ascii=False).replace("</", "<\\/")
        return f"<script>window.__SNAP__={data};</script>\n<script>{STUB}</script>\n<script type=\"module\">{js}</script>"
    html, n = re.subn(r'<script[^>]+type="module"[^>]+src="([^"]+)"[^>]*></script>', js_repl, html)
    if n != 1:
        raise SystemExit(f"expected one module script in index.html, found {n}")
    html = html.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0" />', '<meta name="viewport" content="width=1440" />')
    return html


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://127.0.0.1:8000", help="正在跑的 API")
    ap.add_argument("--skip-build", action="store_true", help="dist-snapshot 已经有了就不重新 vite build")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    dist = WEB / "dist-snapshot"
    if not a.skip_build:
        build_web(dist)
    snap = crawl(a.api.rstrip("/"))
    html = inline(dist, snap)
    Path(a.out).write_text(html, encoding="utf-8")
    print(f"ok {a.out} {len(html.encode()) / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
