from __future__ import annotations

import base64
import hmac
import json
import os
import re
import signal
import sys
import threading
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from backend.admin import render_admin_html
from backend.analytics import AnalyticsStore, clip
from backend.sessions import BackendBusy, SessionManager


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


HOST = os.getenv("WORKSHOP_BACKEND_HOST", "0.0.0.0")
PORT = int(os.getenv("WORKSHOP_BACKEND_PORT", "8765"))
ALLOWED_ORIGINS = [origin.strip().rstrip("/") for origin in os.getenv("WORKSHOP_BACKEND_ALLOW_ORIGIN", "*").split(",") if origin.strip()]
ENABLE_ADMIN_ANALYTICS = os.getenv("WORKSHOP_ENABLE_ADMIN_ANALYTICS", "false").lower() == "true"
ADMIN_USERNAME = os.getenv("WORKSHOP_ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("WORKSHOP_ADMIN_PASSWORD", "")
ANALYTICS_FILE = Path(os.getenv("WORKSHOP_ANALYTICS_FILE", str(Path(__file__).resolve().parent / "data" / "analytics.jsonl")))
ANALYTICS_MAX_ROWS = int(os.getenv("WORKSHOP_ANALYTICS_MAX_ROWS", "500"))
MAX_WORKERS = int(os.getenv("WORKSHOP_MAX_WORKERS", "20"))
SESSION_IDLE_MINUTES = _env_float("WORKSHOP_SESSION_IDLE_MINUTES", 20)
EXECUTION_TIMEOUT = _env_float("WORKSHOP_EXECUTION_TIMEOUT", 180)
WORKER_START_TIMEOUT = _env_float("WORKSHOP_WORKER_START_TIMEOUT", 120)
MAX_REQUEST_BYTES = int(os.getenv("WORKSHOP_MAX_REQUEST_BYTES", str(1_000_000)))

# Anything that looks like a credential is removed from the environment once it
# has been read, so session workers (which run participants' code) never see it.
_SECRET_NAME = re.compile(r"PASSWORD|SECRET|TOKEN|API_KEY|PRIVATE_KEY|^WORKSHOP_ADMIN_", re.IGNORECASE)
for _name in [name for name in os.environ if _SECRET_NAME.search(name)]:
    os.environ.pop(_name, None)

ANALYTICS = AnalyticsStore(ANALYTICS_FILE, ANALYTICS_MAX_ROWS)
SESSIONS: SessionManager | None = None


def _harden_process() -> None:
    """Make /proc/<pid>/environ of the server unreadable to session workers (Linux)."""
    if not sys.platform.startswith("linux"):
        return
    try:
        import ctypes

        pr_set_dumpable = 4
        ctypes.CDLL(None).prctl(pr_set_dumpable, 0, 0, 0, 0)
    except Exception:
        pass


def _sessions() -> SessionManager:
    if SESSIONS is None:
        raise RuntimeError("The session manager is not running.")
    return SESSIONS


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
        "user_agent": clip(handler.headers.get("User-Agent", "")),
        "accept_language": clip(handler.headers.get("Accept-Language", ""), 100),
        "referer": clip(handler.headers.get("Referer", "")),
        "query": {clip(key, 50): [clip(value, 100) for value in values[:5]] for key, values in list(parsed_query.items())[:10]},
    }


def _analytics_record(payload: dict[str, Any], handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": clip(payload.get("event_type") or "unknown", 60),
        "page": clip(payload.get("page")),
        "title": clip(payload.get("title")),
        "section": clip(payload.get("section")),
        "notebook_id": clip(payload.get("notebook_id"), 120),
        "session_id": clip(payload.get("session_id"), 120),
        "runtime_mode": clip(payload.get("runtime_mode"), 40),
        "platform": clip(payload.get("platform"), 60),
        "language": clip(payload.get("language"), 40),
        "timezone": clip(payload.get("timezone"), 60),
        "viewport": f"{clip(payload.get('viewport_width'), 6)}x{clip(payload.get('viewport_height'), 6)}",
        "screen": f"{clip(payload.get('screen_width'), 6)}x{clip(payload.get('screen_height'), 6)}",
        "cell_label": clip(payload.get("cell_label"), 120),
        "demo_id": clip(payload.get("demo_id"), 120),
        "shared": bool(payload.get("shared") or False),
        **_collect_request_metadata(handler),
    }


class RequestError(Exception):
    def __init__(self, status: HTTPStatus, message: str) -> None:
        super().__init__(message)
        self.status = status


class NotebookRuntimeHandler(BaseHTTPRequestHandler):
    server_version = "WorkshopNotebookRuntime/0.2"

    # -- responses -----------------------------------------------------------------

    def _cors_origin(self) -> str:
        if "*" in ALLOWED_ORIGINS:
            return "*"
        origin = (self.headers.get("Origin") or "").rstrip("/")
        return origin if origin in ALLOWED_ORIGINS else (ALLOWED_ORIGINS[0] if ALLOWED_ORIGINS else "")

    def _set_headers(self, status: int = HTTPStatus.OK, content_type: str = "application/json", extra: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()

    def _write_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK, extra: dict[str, str] | None = None) -> None:
        body = json.dumps(payload).encode("utf-8")
        self._set_headers(status=status, extra={"Content-Length": str(len(body)), **(extra or {})})
        self.wfile.write(body)

    def _write_html(self, html: str, status: int = HTTPStatus.OK) -> None:
        body = html.encode("utf-8")
        self._set_headers(status=status, content_type="text/html; charset=utf-8", extra={"Content-Length": str(len(body))})
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError as error:
            raise RequestError(HTTPStatus.BAD_REQUEST, "Invalid Content-Length header.") from error
        if length > MAX_REQUEST_BYTES:
            raise RequestError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, f"Request body is larger than {MAX_REQUEST_BYTES} bytes.")
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RequestError(HTTPStatus.BAD_REQUEST, f"Invalid JSON: {error}") from error
        if not isinstance(payload, dict):
            raise RequestError(HTTPStatus.BAD_REQUEST, "The JSON body must be an object.")
        return payload

    def _dispatch(self, handler: Any) -> None:
        try:
            handler()
        except RequestError as error:
            self._write_json({"ok": False, "error": str(error)}, status=error.status)
        except BackendBusy as error:
            self._write_json({"ok": False, "error": str(error)}, status=HTTPStatus.SERVICE_UNAVAILABLE, extra={"Retry-After": "5"})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as error:  # noqa: BLE001 - always answer with JSON so the site can show the message
            self.log_error("Unhandled error on %s %s: %r", self.command, self.path, error)
            try:
                self._write_json({"ok": False, "error": f"Internal backend error: {error}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            except Exception:
                pass

    # -- admin ---------------------------------------------------------------------

    def _check_admin_auth(self) -> bool:
        if not ENABLE_ADMIN_ANALYTICS or not ADMIN_USERNAME or not ADMIN_PASSWORD:
            return False
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(auth_header.split(" ", 1)[1]).decode("utf-8")
        except Exception:
            return False
        username, _, password = decoded.partition(":")
        user_ok = hmac.compare_digest(username.encode(), ADMIN_USERNAME.encode())
        password_ok = hmac.compare_digest(password.encode(), ADMIN_PASSWORD.encode())
        return user_ok and password_ok

    def _require_admin_auth(self) -> bool:
        if not ENABLE_ADMIN_ANALYTICS:
            self._write_json({"ok": False, "error": "Admin analytics are disabled."}, status=HTTPStatus.NOT_FOUND)
            return False
        if self._check_admin_auth():
            return True
        self._write_json(
            {"ok": False, "error": "Authentication required."},
            status=HTTPStatus.UNAUTHORIZED,
            extra={"WWW-Authenticate": 'Basic realm="Workshop admin"'},
        )
        return False

    # -- routes --------------------------------------------------------------------

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._set_headers(status=HTTPStatus.NO_CONTENT, extra={"Access-Control-Max-Age": "86400"})

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch(self._handle_get)

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch(self._handle_post)

    def do_DELETE(self) -> None:  # noqa: N802
        self._dispatch(self._handle_delete)

    def _handle_get(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            stats = _sessions().stats()
            self._write_json(
                {
                    "ok": True,
                    "mode": "python-backend",
                    "host": HOST,
                    "port": PORT,
                    "admin_analytics_enabled": ENABLE_ADMIN_ANALYTICS,
                    "execution_timeout_seconds": EXECUTION_TIMEOUT,
                    "sessions": {"active": stats["active"], "busy": stats["busy"], "max_workers": stats["max_workers"]},
                }
            )
        elif path == "/admin":
            if self._require_admin_auth():
                self._write_html(render_admin_html(ANALYTICS.read(), _sessions().stats()))
        elif path == "/admin/api/events":
            if self._require_admin_auth():
                self._write_json({"ok": True, "events": ANALYTICS.read()})
        elif path == "/admin/api/sessions":
            if self._require_admin_auth():
                self._write_json({"ok": True, **_sessions().stats()})
        else:
            raise RequestError(HTTPStatus.NOT_FOUND, "Not found")

    def _handle_post(self) -> None:
        path = urlparse(self.path).path
        payload = self._read_json()
        session_id = clip(payload.get("session_id") or "default", 200)

        if path in ("/session/init", "/session/reset"):
            init_result = _sessions().start(session_id, initial_code=str(payload.get("initial_code") or ""))
            response: dict[str, Any] = {"ok": True, "session_id": session_id}
            if init_result is not None:
                response["init"] = init_result
            self._write_json(response)
        elif path == "/execute":
            code = str(payload.get("code") or "")
            if not code.strip():
                result: dict[str, Any] = {"success": True, "stdout": "", "stderr": "", "figures": [], "html": []}
            else:
                result = _sessions().execute(session_id, code)
            self._write_json({"ok": True, "session_id": session_id, **result})
        elif path == "/analytics/event":
            if not ENABLE_ADMIN_ANALYTICS:
                raise RequestError(HTTPStatus.NOT_FOUND, "Analytics disabled.")
            ANALYTICS.append(_analytics_record(payload, self))
            self._write_json({"ok": True})
        else:
            raise RequestError(HTTPStatus.NOT_FOUND, "Not found")

    def _handle_delete(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/session":
            raise RequestError(HTTPStatus.NOT_FOUND, "Not found")
        session_id = parse_qs(parsed.query).get("session_id", ["default"])[0] or "default"
        _sessions().drop(session_id)
        self._write_json({"ok": True, "session_id": session_id})


def run() -> None:
    global SESSIONS
    _harden_process()
    SESSIONS = SessionManager(
        max_workers=MAX_WORKERS,
        idle_ttl=SESSION_IDLE_MINUTES * 60,
        execution_timeout=EXECUTION_TIMEOUT,
        start_timeout=WORKER_START_TIMEOUT,
    )
    server = ThreadingHTTPServer((HOST, PORT), NotebookRuntimeHandler)
    server.daemon_threads = True

    def _stop(_signum: int, _frame: Any) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, _stop)
    print(
        f"Notebook backend listening on http://{HOST}:{PORT} "
        f"(max {MAX_WORKERS} workers, {SESSION_IDLE_MINUTES:g} min idle, {EXECUTION_TIMEOUT:g} s per cell)",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        SESSIONS.shutdown()


if __name__ == "__main__":
    run()
