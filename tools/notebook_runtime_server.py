"""Local execution bridge for workshop code cells.

Run with:
    poetry run python tools/notebook_runtime_server.py
"""

from __future__ import annotations

import io
import json
import os
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HOST = os.getenv("NOTEBOOK_RUNTIME_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", os.getenv("NOTEBOOK_RUNTIME_PORT", "8765")))
SESSIONS: dict[str, dict[str, Any]] = {}


def _birt_available() -> bool:
    try:
        import birt  # noqa: F401

        return True
    except Exception:
        return False


def _get_session(session_id: str) -> dict[str, Any]:
    session = SESSIONS.get(session_id)
    if session is None:
        session = {"__name__": "__main__"}
        SESSIONS[session_id] = session
    return session


def _collect_figures() -> list[str]:
    figures: list[str] = []
    for figure_id in plt.get_fignums():
        figure = plt.figure(figure_id)
        buffer = io.StringIO()
        figure.savefig(buffer, format="svg", bbox_inches="tight")
        figures.append(buffer.getvalue())
    plt.close("all")
    return figures


class NotebookRuntimeHandler(BaseHTTPRequestHandler):
    server_version = "LatentAbilityRuntime/0.1"

    def _set_headers(self, status: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _write_json(self, payload: dict[str, Any], status: int = 200) -> None:
        self._set_headers(status=status)
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._set_headers(status=204)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/health"}:
            self._write_json(
                {
                    "ok": True,
                    "mode": "poetry-runtime",
                    "python": sys.version.split()[0],
                    "birt_available": _birt_available(),
                }
            )
            return

        self._write_json({"ok": False, "error": "Not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/execute":
            self._write_json({"ok": False, "error": "Not found"}, status=404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length)

        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._write_json({"ok": False, "error": "Invalid JSON"}, status=400)
            return

        session_id = payload.get("session_id")
        prelude = payload.get("prelude", "")
        code = payload.get("code", "")

        if not session_id:
            self._write_json({"ok": False, "error": "session_id is required"}, status=400)
            return

        session = _get_session(session_id)
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        error_text = ""
        figures: list[str] = []

        try:
            plt.close("all")
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                if prelude:
                    exec(prelude, session, session)
                exec(code, session, session)
            figures = _collect_figures()
        except Exception:
            error_text = traceback.format_exc()
            stderr_buffer.write(error_text)
            plt.close("all")

        self._write_json(
            {
                "ok": error_text == "",
                "stdout": stdout_buffer.getvalue(),
                "stderr": stderr_buffer.getvalue(),
                "figures": figures,
                "birt_available": _birt_available(),
                "mode": "poetry-runtime",
            }
        )


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), NotebookRuntimeHandler)
    print(f"Notebook runtime listening on http://{HOST}:{PORT}")
    server.serve_forever()
