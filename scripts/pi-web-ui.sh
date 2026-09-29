#!/usr/bin/env bash
# 使用 npm 全局安装，不在项目中安装 pi-web-ui；保留原有会话数据目录。
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
GLOBAL_ROOT="$(npm root -g)"
ENTRY="$GLOBAL_ROOT/pi-web-ui/bin/pi-web-ui.mjs"
if [[ ! -f "$ENTRY" ]]; then
  printf '未找到全局 pi-web-ui，请先运行 npm install -g pi-web-ui\n' >&2
  exit 1
fi
cd "$ROOT"
exec node "$ENTRY" --no-browser --host 127.0.0.1 --port 8787 \
  --cwd "$ROOT" --data-dir "$ROOT/.pi/npm/pi-web-ui-runtime/data" "$@"
