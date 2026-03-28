from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .config import Settings, load_settings
from .feishu import parse_feishu_event
from .models import ClipRequest
from .processor import ClipProcessor


class ClippingBotHandler(BaseHTTPRequestHandler):
    processor: ClipProcessor
    settings: Settings

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json_response(HTTPStatus.OK, {"status": "ok"})
            return
        self._json_response(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:
        try:
            payload = self._read_json()
        except ValueError as exc:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        try:
            if self.path == "/ingest":
                self._handle_ingest(payload)
                return
            if self.path == "/feishu/events":
                self._handle_feishu(payload)
                return
        except Exception as exc:
            self._json_response(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
            return

        self._json_response(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def _handle_ingest(self, payload: dict[str, Any]) -> None:
        text = str(payload.get("text", "")).strip()
        if not text:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": "text is required"})
            return
        source = str(payload.get("source", "manual")).strip() or "manual"
        saved = self.processor.process(ClipRequest(raw_text=text, source=source))
        self._json_response(
            HTTPStatus.OK,
            {"status": "saved", "title": saved.title, "path": str(saved.path), "created": saved.created},
        )

    def _handle_feishu(self, payload: dict[str, Any]) -> None:
        action, request = parse_feishu_event(payload, self.settings.feishu_verify_token)
        if action == "url_verification":
            self._json_response(HTTPStatus.OK, {"challenge": payload.get("challenge", "")})
            return
        if action == "ignored" or request is None:
            self._json_response(HTTPStatus.OK, {"status": "ignored"})
            return

        saved = self.processor.process(request)
        self._json_response(
            HTTPStatus.OK,
            {"status": "saved", "title": saved.title, "path": str(saved.path), "created": saved.created},
        )

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(raw or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Request body must be valid JSON") from exc
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def _json_response(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_server() -> None:
    settings = load_settings()
    handler_cls = type(
        "ConfiguredClippingBotHandler",
        (ClippingBotHandler,),
        {"processor": ClipProcessor(settings), "settings": settings},
    )
    server = ThreadingHTTPServer((settings.server_host, settings.server_port), handler_cls)
    print(f"ClippingBot listening on http://{settings.server_host}:{settings.server_port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()

