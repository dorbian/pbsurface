"""Small authenticated prototype API for endpoint state and actions."""

from __future__ import annotations

import hmac
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import unquote, urlparse

from .actions import ActionExecutor, UnknownAction
from .model import HostConfig


MAX_BODY = 16 * 1024


class EndpointServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], config: HostConfig) -> None:
        super().__init__(address, EndpointHandler)
        self.config = config
        self.executor = ActionExecutor(config.actions)


class EndpointHandler(BaseHTTPRequestHandler):
    server: EndpointServer
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        # Keep the standard address/status log while never logging auth headers.
        super().log_message(format, *args)

    def _authorized(self) -> bool:
        supplied = self.headers.get("X-PlayBook-Token", "")
        return hmac.compare_digest(supplied.encode("utf-8"), self.server.config.auth_token.encode("utf-8"))

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, {"ok": True, "service": "playbook-surface-host", "protocol": 1})
            return
        if not self._authorized():
            self._json(401, {"error": "authentication required"})
            return
        if path == "/v1/endpoint":
            self._json(200, self.server.config.endpoint.discovery_payload())
            return
        if path == "/v1/deck":
            self._json(200, self.server.config.deck)
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if not self._authorized():
            self._json(401, {"error": "authentication required"})
            return
        prefix = "/v1/actions/"
        if not path.startswith(prefix):
            self._json(404, {"error": "not found"})
            return
        length_text = self.headers.get("Content-Length", "0")
        try:
            length = int(length_text)
        except ValueError:
            self._json(400, {"error": "invalid content length"})
            return
        if length < 0 or length > MAX_BODY:
            self._json(413, {"error": "request body too large"})
            return
        if length:
            self.rfile.read(length)
        action_id = unquote(path[len(prefix) :])
        try:
            result = self.server.executor.run(action_id)
        except UnknownAction:
            self._json(404, {"error": "unknown action"})
            return
        except OSError as exc:
            self._json(500, {"error": "action launch failed", "detail": str(exc)})
            return
        self._json(202, {"accepted": True, "action_id": result.action_id, "pid": result.pid})

