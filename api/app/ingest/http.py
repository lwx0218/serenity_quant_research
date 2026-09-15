"""标准库 HTTP：统一 UA、超时、重试、JSON。所有适配器只经这里出网。"""
from __future__ import annotations

import gzip
import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 TeardownIngest/0.1")
DEFAULT_TIMEOUT = 20


class FetchError(RuntimeError):
    """一次抓取失败（网络 / 状态码 / 解析），带上可读原因给 ingest_todo。"""


def get(url: str, params: dict | None = None, *, timeout: int = DEFAULT_TIMEOUT, headers: dict | None = None,
        data: bytes | None = None, retries: int = 2, backoff: float = 1.5) -> bytes:
    if params:
        url = f"{url}{'&' if '?' in url else '?'}{urlencode(params)}"
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = Request(url, data=data, headers={"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip", **(headers or {})})
            with urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return raw
        except HTTPError as e:
            last = e
            if e.code in (400, 401, 403, 404):
                break
        except (URLError, TimeoutError, OSError) as e:
            last = e
        time.sleep(backoff * (attempt + 1))
    raise FetchError(f"{type(last).__name__}: {str(last)[:160]}  ← {url[:160]}")


def get_json(url: str, params: dict | None = None, **kw) -> Any:
    raw = get(url, params, **kw)
    text = raw.decode("utf-8", "ignore").strip()
    # 东财有的接口包 jQuery 回调：cb({...})
    if text and not text.startswith(("{", "[")):
        i, j = text.find("("), text.rfind(")")
        if 0 <= i < j:
            text = text[i + 1:j]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise FetchError(f"not JSON ({e.msg}): {text[:120]!r}  ← {url[:120]}") from e


def post_json(url: str, body: dict, **kw) -> Any:
    kw.setdefault("headers", {})["Content-Type"] = "application/json"
    return get_json(url, data=json.dumps(body).encode(), **kw)
