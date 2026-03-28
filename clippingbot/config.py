from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    crawl4ai_base_url: str
    crawl4ai_email: str | None
    crawl4ai_bearer_token: str | None
    crawl4ai_filter: str
    crawl4ai_timeout_seconds: int
    crawl4ai_mode: str
    crawl4ai_crawl_fallback_domains: tuple[str, ...]
    obsidian_vault_path: Path
    obsidian_inbox_dir: str
    note_tags: tuple[str, ...]
    note_overwrite_existing: bool
    filename_max_length: int
    feishu_verify_token: str | None
    feishu_app_id: str | None
    feishu_app_secret: str | None
    feishu_delivery_mode: str
    feishu_encrypt_key: str | None
    feishu_reply_enabled: bool
    feishu_reply_receive_id_type: str
    server_host: str
    server_port: int

    @property
    def obsidian_output_dir(self) -> Path:
        return self.obsidian_vault_path / self.obsidian_inbox_dir


def load_settings() -> Settings:
    _load_dotenv(Path.cwd() / ".env")

    vault = os.environ.get("CLIPPINGBOT_OBSIDIAN_VAULT", "").strip()
    if not vault:
        raise RuntimeError("CLIPPINGBOT_OBSIDIAN_VAULT is required")

    base_url = os.environ.get("CLIPPINGBOT_CRAWL4AI_BASE_URL", "http://127.0.0.1:11235").rstrip("/")
    email = os.environ.get("CLIPPINGBOT_CRAWL4AI_EMAIL", "").strip() or None
    bearer = os.environ.get("CLIPPINGBOT_CRAWL4AI_BEARER_TOKEN", "").strip() or None

    if not email and not bearer:
        raise RuntimeError(
            "Either CLIPPINGBOT_CRAWL4AI_EMAIL or CLIPPINGBOT_CRAWL4AI_BEARER_TOKEN is required"
        )

    return Settings(
        crawl4ai_base_url=base_url,
        crawl4ai_email=email,
        crawl4ai_bearer_token=bearer,
        crawl4ai_filter=os.environ.get("CLIPPINGBOT_CRAWL4AI_FILTER", "fit").strip() or "fit",
        crawl4ai_timeout_seconds=int(os.environ.get("CLIPPINGBOT_CRAWL4AI_TIMEOUT_SECONDS", "60")),
        crawl4ai_mode=os.environ.get("CLIPPINGBOT_CRAWL4AI_MODE", "auto").strip().lower() or "auto",
        crawl4ai_crawl_fallback_domains=_parse_csv(
            os.environ.get("CLIPPINGBOT_CRAWL4AI_CRAWL_FALLBACK_DOMAINS", "mp.weixin.qq.com")
        ),
        obsidian_vault_path=Path(vault).expanduser().resolve(),
        obsidian_inbox_dir=os.environ.get("CLIPPINGBOT_OBSIDIAN_INBOX", "Clippings").strip() or "Clippings",
        note_tags=_parse_csv(os.environ.get("CLIPPINGBOT_NOTE_TAGS", "clippings")),
        note_overwrite_existing=_parse_bool(os.environ.get("CLIPPINGBOT_NOTE_OVERWRITE_EXISTING"), True),
        filename_max_length=int(os.environ.get("CLIPPINGBOT_FILENAME_MAX_LENGTH", "72")),
        feishu_verify_token=os.environ.get("CLIPPINGBOT_FEISHU_VERIFY_TOKEN", "").strip() or None,
        feishu_app_id=os.environ.get("CLIPPINGBOT_FEISHU_APP_ID", "").strip() or None,
        feishu_app_secret=os.environ.get("CLIPPINGBOT_FEISHU_APP_SECRET", "").strip() or None,
        feishu_delivery_mode=os.environ.get("CLIPPINGBOT_FEISHU_DELIVERY_MODE", "longconn").strip() or "longconn",
        feishu_encrypt_key=os.environ.get("CLIPPINGBOT_FEISHU_ENCRYPT_KEY", "").strip() or None,
        feishu_reply_enabled=_parse_bool(os.environ.get("CLIPPINGBOT_FEISHU_REPLY_ENABLED"), True),
        feishu_reply_receive_id_type=os.environ.get("CLIPPINGBOT_FEISHU_REPLY_RECEIVE_ID_TYPE", "chat_id").strip()
        or "chat_id",
        server_host=os.environ.get("CLIPPINGBOT_HOST", "0.0.0.0"),
        server_port=int(os.environ.get("CLIPPINGBOT_PORT", "8787")),
    )


def _parse_csv(raw: str) -> tuple[str, ...]:
    items = [item.strip() for item in raw.split(",")]
    return tuple(item for item in items if item)


def _parse_bool(raw: str | None, default: bool) -> bool:
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)
