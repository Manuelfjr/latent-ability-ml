from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from backend.executor import drop_context, execute_code, init_context, reset_context

HOST = os.getenv("WORKSHOP_BACKEND_HOST", "0.0.0.0")
PORT = int(os.getenv("WORKSHOP_BACKEND_PORT", "8765"))
ALLOWED_ORIGIN = os.getenv("WORKSHOP_BACKEND_ALLOW_ORIGIN", "*")
ENABLE_ADMIN_ANALYTICS = os.getenv("WORKSHOP_ENABLE_ADMIN_ANALYTICS", "false").lower() == "true"
ADMIN_USERNAME = os.getenv("WORKSHOP_ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("WORKSHOP_ADMIN_PASSWORD", "")
ANALYTICS_FILE = Path(os.getenv("WORKSHOP_ANALYTICS_FILE", str(Path(__file__).resolve().parent / "data" / "analytics.jsonl")))
ANALYTICS_MAX_ROWS = int(os.getenv("WORKSHOP_ANALYTICS_MAX_ROWS", "500"))


def _mask_client_ip(ip_address: str) -> str:
    raw = str(ip_address or "").strip()
    if not raw:
        return "unknown"
    if ":" in raw and "." not in raw:
        segments = raw.split(":")
        return ":".join(segments[:4]) + ":*"
    parts = raw.split(".")
    if len(parts) == 4:
        return ".".join(parts[:3] + ["*"])
    return raw


def _collect_request_metadata(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    parsed_query = parse_qs(urlparse(handler.path).query)
    forwarded_for = handler.headers.get("X-Forwarded-For", "")
    forwarded_ip = forwarded_for.split(",")[0].strip() if forwarded_for else ""
    client_ip = forwarded_ip or (handler.client_address[0] if handler.client_address else "")
    return {
        "ip_masked": _mask_client_ip(client_ip),
        "user_agent": handler.headers.get("User-Agent", ""),
        "accept_language": handler.headers.get("Accept-Language", ""),
        "referer": handler.headers.get("Referer", ""),
        "query": {key: values for key, values in parsed_query.items()},
    }


def _write_event(record: dict[str, Any]) -> None:
    ANALYTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with ANALYTICS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_events(limit: int = ANALYTICS_MAX_ROWS) -> list[dict[str, Any]]:
    if not ANALYTICS_FILE.exists():
        return []
    lines = ANALYTICS_FILE.read_text(encoding="utf-8").splitlines()
    events: list[dict[str, Any]] = []
    for line in reversed(lines[-limit:]):
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _render_admin_html(events: list[dict[str, Any]]) -> str:
    rows = []
    for event in events:
        rows.append(
            "<tr>"
            f"<td>{escape(str(event.get('timestamp', '')))}</td>"
            f"<td>{escape(str(event.get('event_type', '')))}</td>"
            f"<td>{escape(str(event.get('page', '')))}</td>"
            f"<td>{escape(str(event.get('runtime_mode', '')))}</td>"
            f"<td>{escape(str(event.get('notebook_id', '')))}</td>"
            f"<td>{escape(str(event.get('session_id', '')))}</td>"
            f"<td>{escape(str(event.get('ip_masked', '')))}</td>"
            f"<td>{escape(str(event.get('platform', '')))}</td>"
            f"<td>{escape(str(event.get('viewport', '')))}</td>"
            f"<td>{escape(str(event.get('timezone', '')))}</td>"
            "</tr>"
        )
    body_rows = "".join(rows) or "<tr><td colspan='10'>No events recorded yet.</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Workshop Admin Analytics</title>
    <style>
      body {{
        margin: 0;
        padding: 32px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f7f3eb;
        color: #231f20;
      }}
      h1 {{
        margin: 0 0 8px;
      }}
      p {{
        margin: 0 0 20px;
        color: #5f5245;
      }}
      .table-wrap {{
        overflow: auto;
        background: white;
        border: 1px solid #e7d7c4;
        border-radius: 18px;
        box-shadow: 0 14px 40px rgba(74, 52, 24, 0.08);
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        min-width: 980px;
      }}
      th, td {{
        padding: 12px 14px;
        text-align: left;
        border-bottom: 1px solid #efe4d6;
        font-size: 14px;
        vertical-align: top;
      }}
      th {{
        position: sticky;
        top: 0;
        background: #fdf8f1;
        color: #8f1f2d;
      }}
      code {{
        background: #f3ece2;
        padding: 2px 6px;
        border-radius: 8px;
      }}
    </style>
  </head>
  <body>
    <h1>Workshop admin analytics</h1>
    <p>Recent usage events recorded for the workshop environment. This view is controlled by <code>WORKSHOP_ENABLE_ADMIN_ANALYTICS</code>.</p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Event</th>
            <th>Page</th>
            <th>Runtime</th>
            <th>Notebook</th>
            <th>Session</th>
            <th>Client</th>
            <th>Platform</th>
            <th>Viewport</th>
            <th>Timezone</th>
          </tr>
        </thead>
        <tbody>{body_rows}</tbody>
      </table>
    </div>
  </body>
</html>"""


class NotebookRuntimeHandler(BaseHTTPRequestHandler):
    server_version = "WorkshopNotebookRuntime/0.1"

    def _set_headers(self, status: int = HTTPStatus.OK, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _write_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        self._set_headers(status=status)
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _write_html(self, html: str, status: int = HTTPStatus.OK) -> None:
        self._set_headers(status=status, content_type="text/html; charset=utf-8")
        self.wfile.write(html.encode("utf-8"))

    def _admin_enabled(self) -> bool:
        return ENABLE_ADMIN_ANALYTICS

    def _check_admin_auth(self) -> bool:
        if not self._admin_enabled():
            return False
        if not ADMIN_USERNAME or not ADMIN_PASSWORD:
            return False
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(auth_header.split(" ", 1)[1]).decode("utf-8")
        except Exception:
            return False
        username, _, password = decoded.partition(":")
        return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

    def _require_admin_auth(self) -> bool:
        if not self._admin_enabled():
            self._write_json(
                {"ok": False, "error": "Admin analytics are disabled."},
                status=HTTPStatus.NOT_FOUND,
            )
            return False
        if self._check_admin_auth():
            return True
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header("WWW-Authenticate", 'Basic realm="Workshop admin"')
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": False, "error": "Authentication required."}).encode("utf-8"))
        return False

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
                    "admin_analytics_enabled": ENABLE_ADMIN_ANALYTICS,
                }
            )
            return
        if path == "/admin":
            if not self._require_admin_auth():
                return
            self._write_html(_render_admin_html(_read_events()))
            return
        if path == "/admin/api/events":
            if not self._require_admin_auth():
                return
            self._write_json({"ok": True, "events": _read_events()})
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

        if path == "/analytics/event":
            if not self._admin_enabled():
                self._write_json({"ok": False, "error": "Analytics disabled."}, status=HTTPStatus.NOT_FOUND)
                return
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": str(payload.get("event_type") or "unknown"),
                "page": str(payload.get("page") or ""),
                "title": str(payload.get("title") or ""),
                "section": str(payload.get("section") or ""),
                "notebook_id": str(payload.get("notebook_id") or ""),
                "session_id": str(payload.get("session_id") or ""),
                "runtime_mode": str(payload.get("runtime_mode") or ""),
                "platform": str(payload.get("platform") or ""),
                "language": str(payload.get("language") or ""),
                "timezone": str(payload.get("timezone") or ""),
                "viewport": f"{payload.get('viewport_width', '')}x{payload.get('viewport_height', '')}",
                "screen": f"{payload.get('screen_width', '')}x{payload.get('screen_height', '')}",
                "cell_label": str(payload.get("cell_label") or ""),
                "demo_id": str(payload.get("demo_id") or ""),
                "shared": bool(payload.get("shared") or False),
                **_collect_request_metadata(self),
            }
            _write_event(record)
            self._write_json({"ok": True})
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
