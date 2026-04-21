from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from backend.executor import drop_context, execute_code, init_context, reset_context

HOST = os.getenv("WORKSHOP_BACKEND_HOST", "0.0.0.0")
PORT = int(os.getenv("WORKSHOP_BACKEND_PORT", "8765"))
ALLOWED_ORIGIN = os.getenv("WORKSHOP_BACKEND_ALLOW_ORIGIN", "*")


class NotebookRuntimeHandler(BaseHTTPRequestHandler):
    server_version = "WorkshopNotebookRuntime/0.1"

    def _set_headers(self, status: int = HTTPStatus.OK, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _write_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        self._set_headers(status=status)
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._set_headers(status=HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._write_json(
                {
                    "ok": True,
                    "mode": "python-backend",
                    "host": HOST,
                    "port": PORT,
                }
            )
            return
        self._write_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
        except json.JSONDecodeError as error:
            self._write_json({"ok": False, "error": f"Invalid JSON: {error}"}, status=HTTPStatus.BAD_REQUEST)
            return

        session_id = str(payload.get("session_id") or "default")
        initial_code = str(payload.get("initial_code") or "")

        if path == "/session/init":
            init_context(session_id, initial_code=initial_code)
            self._write_json({"ok": True, "session_id": session_id})
            return

        if path == "/session/reset":
            reset_context(session_id, initial_code=initial_code)
            self._write_json({"ok": True, "session_id": session_id})
            return

        if path == "/execute":
            code = str(payload.get("code") or "")
            if not code.strip():
                self._write_json(
                    {
                        "ok": True,
                        "session_id": session_id,
                        "success": True,
                        "stdout": "",
                        "stderr": "",
                        "figures": [],
                    }
                )
                return
            result = execute_code(session_id, code)
            self._write_json({"ok": True, "session_id": session_id, **result})
            return

        self._write_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/session":
            self._write_json({"ok": False, "error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return
        session_id = urlparse(self.path).query.replace("session_id=", "") or "default"
        drop_context(session_id)
        self._write_json({"ok": True, "session_id": session_id})


def run() -> None:
    server = ThreadingHTTPServer((HOST, PORT), NotebookRuntimeHandler)
    print(f"Notebook backend listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
