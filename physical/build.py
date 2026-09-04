"""把 data/*.json 内联进 index.html，生成 dist/ 下可直接双击打开的单文件。

用法：python physical/build.py            # 生成 dist/teardown-1.6t-dr8-siph.html
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "module-1.6t-dr8-siph.json"
SRC = HERE / "index.html"
OUT = HERE / "dist" / "teardown-1.6t-dr8-siph.html"

MARKER = "/*__INLINE_DATA__*/"


def check(data: dict) -> list[str]:
    """轻量一致性检查：信号路径引用的 part 必须存在，stage/layer 必须在字典里。"""
    m = data["module"]
    parts = {p["id"] for p in m["parts"]}
    stages = {s["id"] for s in m["stages"]}
    layers = {l["id"] for l in m["layers"]}
    errs = []
    for d in ("tx", "rx"):
        for s in m["signalPath"][d]:
            if s["partId"] not in parts:
                errs.append(f"signalPath.{d} step {s['step']} 引用了不存在的 part {s['partId']}")
    for p in m["parts"]:
        if p["layerId"] not in layers:
            errs.append(f"{p['id']} layerId {p['layerId']} 不在 layers 里")
        for c in p["companies"]:
            if c["stage"] not in stages:
                errs.append(f"{p['id']} / {c['name']} stage {c['stage']} 不在 stages 里")
            if c["evidence"] not in ("verified", "consensus", "candidate"):
                errs.append(f"{p['id']} / {c['name']} evidence 非法：{c['evidence']}")
    return errs


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    errs = check(data)
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    html = SRC.read_text(encoding="utf-8")
    if MARKER not in html:
        print("index.html 缺少内联标记", file=sys.stderr)
        return 1
    inline = "window.__TEARDOWN_DATA__ = " + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html.replace(MARKER, inline), encoding="utf-8")
    m = data["module"]
    print(f"ok → {OUT.relative_to(HERE.parent)}  ({len(m['parts'])} parts, {sum(len(p['companies']) for p in m['parts'])} company links)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
