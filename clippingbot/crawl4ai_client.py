from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import Settings
from .models import CrawlMarkdownResult


@dataclass
class _TokenCache:
    token: str | None = None
    expires_at: float = 0.0


class Crawl4AIClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._token_cache = _TokenCache()

    def fetch_markdown(self, url: str, filter_name: str = "fit") -> CrawlMarkdownResult:
        mode = self._settings.crawl4ai_mode
        if mode == "crawl":
            return self._fetch_via_crawl(url, filter_name)
        if mode == "md":
            return self._fetch_via_md(url, filter_name)

        if self._should_prefer_crawl(url):
            result = self._fetch_via_crawl(url, filter_name)
            if result.success and result.markdown.strip():
                return result

        result = self._fetch_via_md(url, filter_name)
        if self._looks_blocked(result.markdown):
            crawl_result = self._fetch_via_crawl(url, filter_name)
            if crawl_result.success and crawl_result.markdown.strip():
                return crawl_result
        return result

    def _fetch_via_md(self, url: str, filter_name: str) -> CrawlMarkdownResult:
        payload = {"url": url, "f": filter_name}
        response = self._request_json(
            "POST",
            "/md",
            payload,
            headers={"Authorization": f"Bearer {self._get_bearer_token()}"},
        )
        markdown = str(response.get("markdown", ""))
        success = bool(response.get("success", True))
        return CrawlMarkdownResult(url=url, markdown=markdown, success=success, filter_name=filter_name)

    def _fetch_via_crawl(self, url: str, filter_name: str) -> CrawlMarkdownResult:
        payload = {"urls": [url]}
        response = self._request_json(
            "POST",
            "/crawl",
            payload,
            headers={"Authorization": f"Bearer {self._get_bearer_token()}"},
        )
        results = response.get("results") or []
        if not results:
            return CrawlMarkdownResult(url=url, markdown="", success=False, filter_name=filter_name)
        first = results[0] or {}
        markdown_obj = first.get("markdown") or {}
        markdown = (
            str(markdown_obj.get("raw_markdown", ""))
            or str(markdown_obj.get("markdown_with_citations", ""))
            or str(first.get("fit_markdown", ""))
        )
        success = bool(first.get("success", response.get("success", True)))
        return CrawlMarkdownResult(url=url, markdown=markdown, success=success, filter_name=filter_name)

    def _should_prefer_crawl(self, url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return host in {domain.lower() for domain in self._settings.crawl4ai_crawl_fallback_domains}

    def _looks_blocked(self, markdown: str) -> bool:
        lowered = markdown.strip().lower()
        return "当前环境异常" in markdown or "完成验证后即可继续访问" in markdown or "environment exception" in lowered

    def _get_bearer_token(self) -> str:
        if self._settings.crawl4ai_bearer_token:
            return self._settings.crawl4ai_bearer_token

        now = time.time()
        if self._token_cache.token and self._token_cache.expires_at - now > 30:
            return self._token_cache.token

        response = self._request_json("POST", "/token", {"email": self._settings.crawl4ai_email})
        token = str(response["access_token"])
        expires_at = _decode_jwt_exp(token) or (now + 3600)
        self._token_cache = _TokenCache(token=token, expires_at=expires_at)
        return token

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._settings.crawl4ai_base_url}{path}"
        body = json.dumps(payload).encode("utf-8")
        request = Request(url, data=body, method=method)
        request.add_header("Content-Type", "application/json")
        if headers:
            for key, value in headers.items():
                request.add_header(key, value)
        try:
            with urlopen(request, timeout=self._settings.crawl4ai_timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Crawl4AI HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Cannot reach Crawl4AI: {exc}") from exc

        data = json.loads(raw)
        if not isinstance(data, dict):
            raise RuntimeError("Unexpected Crawl4AI response")
        return data


def _decode_jwt_exp(token: str) -> float | None:
    parts = token.split(".")
    if len(parts) != 3:
        return None

    import base64

    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload + padding).decode("utf-8")
        data = json.loads(decoded)
    except Exception:
        return None

    exp = data.get("exp")
    if isinstance(exp, (int, float)):
        return float(exp)
    return None
