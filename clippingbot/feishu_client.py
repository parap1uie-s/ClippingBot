from __future__ import annotations

import json
import uuid

import lark_oapi as lark
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody

from .config import Settings


class FeishuMessageClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.feishu_app_id or not settings.feishu_app_secret:
            raise RuntimeError("Feishu app credentials are required for reply support")
        self._settings = settings
        self._client = lark.Client.builder().app_id(settings.feishu_app_id).app_secret(
            settings.feishu_app_secret
        ).build()

    def send_text(self, receive_id: str, text: str) -> None:
        request = (
            CreateMessageRequest.builder()
            .receive_id_type(self._settings.feishu_reply_receive_id_type)
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(receive_id)
                .msg_type("text")
                .content(json.dumps({"text": text}, ensure_ascii=False))
                .uuid(str(uuid.uuid4()))
                .build()
            )
            .build()
        )
        response = self._client.im.v1.message.create(request)
        if not response.success():
            raise RuntimeError(
                f"Feishu reply failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}"
            )

