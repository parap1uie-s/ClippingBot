from __future__ import annotations

import json
from typing import Any

from .models import ClipRequest


def parse_feishu_event(payload: dict[str, Any], verify_token: str | None) -> tuple[str, ClipRequest | None]:
    event_type = payload.get("type")
    if event_type == "url_verification":
        token = payload.get("token")
        if verify_token and token != verify_token:
            raise ValueError("Invalid Feishu verification token")
        return "url_verification", None

    header = payload.get("header") or {}
    if header.get("event_type") != "im.message.receive_v1":
        return "ignored", None

    event = payload.get("event") or {}
    message = event.get("message") or {}
    if message.get("message_type") != "text":
        return "ignored", None

    content = message.get("content") or "{}"
    try:
        content_json = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid Feishu message content JSON") from exc

    text = (content_json.get("text") or "").strip()
    if not text:
        return "ignored", None

    request = ClipRequest(
        raw_text=text,
        source="feishu",
        external_id=message.get("message_id"),
        reply_target=message.get("chat_id"),
    )
    return "clip", request
