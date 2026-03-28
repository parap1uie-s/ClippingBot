from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field

import lark_oapi as lark
from lark_oapi.api.im.v1.model.p2_im_message_receive_v1 import P2ImMessageReceiveV1
from lark_oapi.ws import Client as WSClient

from .config import Settings, load_settings
from .feishu_client import FeishuMessageClient
from .models import ClipRequest
from .processor import ClipProcessor


@dataclass
class LongConnRuntime:
    settings: Settings
    processor: ClipProcessor
    message_client: FeishuMessageClient | None
    seen_message_ids: set[str] = field(default_factory=set)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def handle_message(self, data: P2ImMessageReceiveV1) -> None:
        event = data.event
        if event is None or event.message is None:
            return

        message = event.message
        if message.message_type != "text" or not message.content:
            return

        message_id = message.message_id or ""
        with self.lock:
            if message_id and message_id in self.seen_message_ids:
                return
            if message_id:
                self.seen_message_ids.add(message_id)

        try:
            content = json.loads(message.content)
            text = str(content.get("text", "")).strip()
        except json.JSONDecodeError as exc:
            self._safe_reply(message.chat_id, f"剪藏失败：无法解析飞书消息内容。{exc}")
            return

        if not text:
            return

        try:
            saved = self.processor.process(
                ClipRequest(
                    raw_text=text,
                    source="feishu",
                    external_id=message.message_id,
                    reply_target=message.chat_id,
                )
            )
        except Exception as exc:
            self._safe_reply(message.chat_id, f"剪藏失败：{exc}")
            return

        self._safe_reply(message.chat_id, f"已保存到 Obsidian：{saved.title}")

    def _safe_reply(self, receive_id: str | None, text: str) -> None:
        if not self.settings.feishu_reply_enabled or not self.message_client or not receive_id:
            return
        try:
            self.message_client.send_text(receive_id, text)
        except Exception as exc:
            print(f"Failed to send Feishu reply: {exc}")


def run_long_connection() -> None:
    settings = load_settings()
    if not settings.feishu_app_id or not settings.feishu_app_secret:
        raise RuntimeError("CLIPPINGBOT_FEISHU_APP_ID and CLIPPINGBOT_FEISHU_APP_SECRET are required")

    runtime = LongConnRuntime(
        settings=settings,
        processor=ClipProcessor(settings),
        message_client=FeishuMessageClient(settings) if settings.feishu_reply_enabled else None,
    )

    handler = (
        lark.EventDispatcherHandler.builder(
            settings.feishu_encrypt_key or "",
            settings.feishu_verify_token or "",
            lark.LogLevel.INFO,
        )
        .register_p2_im_message_receive_v1(runtime.handle_message)
        .build()
    )

    client = WSClient(
        settings.feishu_app_id,
        settings.feishu_app_secret,
        log_level=lark.LogLevel.INFO,
        event_handler=handler,
    )

    print("ClippingBot Feishu long connection started")
    client.start()


if __name__ == "__main__":
    run_long_connection()

