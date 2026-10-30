"""Process-per-session pool used by the HTTP server.

Each notebook session runs in its own worker process (``backend.worker``), which
isolates stdout/figures between participants, lets a runaway cell be interrupted,
and keeps the server's secrets out of user code.
"""

from __future__ import annotations

import multiprocessing
import os
import signal
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from multiprocessing.connection import Connection
from multiprocessing.process import BaseProcess
from typing import Any

from backend import worker

_MP = multiprocessing.get_context("spawn")
INTERRUPT_GRACE_SECONDS = 5.0
REMEMBERED_EXPIRED_SESSIONS = 1000


class BackendBusy(Exception):
    """Raised when no worker slot (or the session itself) is available."""


@dataclass
class Session:
    session_id: str
    process: BaseProcess
    conn: Connection
    initial_code: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    executions: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def busy(self) -> bool:
        return self.lock.locked()

    def signal(self, signum: int) -> None:
        """Signal the worker and anything it started (birt spawns its own processes)."""
        pid = self.process.pid
        if pid is None:
            return
        try:
            os.killpg(pid, signum)
        except (AttributeError, ProcessLookupError, PermissionError):
            try:
                os.kill(pid, signum)
            except ProcessLookupError:
                pass

    def stop(self) -> None:
        try:
            self.conn.send(("stop",))
        except Exception:
            pass
        self.process.join(timeout=1)
        if self.process.is_alive():
            self.signal(signal.SIGKILL)
            self.process.join(timeout=1)
        else:
            self.signal(signal.SIGKILL)  # reap leftover children of the worker
        self.conn.close()


def _notice(text: str) -> str:
    return f"[backend] {text}\n"


def _error_result(message: str) -> dict[str, Any]:
    return {"success": False, "stdout": "", "stderr": _notice(message), "figures": [], "html": []}


class SessionManager:
    def __init__(self, max_workers: int, idle_ttl: float, execution_timeout: float, start_timeout: float) -> None:
        self.max_workers = max_workers
        self.idle_ttl = idle_ttl
        self.execution_timeout = execution_timeout
        self.start_timeout = start_timeout
        self._sessions: dict[str, Session] = {}
        self._expired: OrderedDict[str, tuple[str, str]] = OrderedDict()
        self._pending = 0
        self._lock = threading.Lock()
        self._stopping = threading.Event()
        self._reaper = threading.Thread(target=self._reap_forever, name="session-reaper", daemon=True)
        self._reaper.start()

    # -- lifecycle -----------------------------------------------------------------

    def start(self, session_id: str, initial_code: str = "") -> dict[str, Any] | None:
        """Start (or restart) a session with a fresh namespace."""
        self.drop(session_id, reason=None)
        session, init_result = self._spawn(session_id, initial_code)
        with self._lock:
            previous = self._sessions.pop(session_id, None)
            self._sessions[session_id] = session
        if previous is not None:
            previous.stop()
        return init_result

    def drop(self, session_id: str, reason: str | None = None) -> bool:
        with self._lock:
            session = self._sessions.pop(session_id, None)
            if session is not None and reason:
                self._remember_expired(session, reason)
        if session is None:
            return False
        session.stop()
        return True

    def shutdown(self) -> None:
        self._stopping.set()
        with self._lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()
        for session in sessions:
            session.stop()

    # -- execution -----------------------------------------------------------------

    def execute(self, session_id: str, code: str) -> dict[str, Any]:
        notices: list[str] = []
        with self._lock:
            session = self._sessions.get(session_id)
            expired = self._expired.pop(session_id, None)
        if session is None:
            initial_code, reason = expired or ("", "")
            if expired:
                notices.append(f"Your previous Python session was closed ({reason}). Variables from earlier cells are gone: re-run them first.")
            self.start(session_id, initial_code)
            with self._lock:
                session = self._sessions.get(session_id)
            if session is None:
                return _error_result("The Python session could not be started. Please try again.")

        if not session.lock.acquire(timeout=self.execution_timeout + INTERRUPT_GRACE_SECONDS + 5):
            raise BackendBusy("A previous cell in this session is still running.")
        try:
            result = self._run_locked(session, code)
        finally:
            session.last_used = time.time()
            session.lock.release()

        if notices:
            result["stdout"] = "".join(_notice(text) for text in notices) + result.get("stdout", "")
        return result

    def _run_locked(self, session: Session, code: str) -> dict[str, Any]:
        session.executions += 1
        try:
            session.conn.send(("execute", code))
            if session.conn.poll(self.execution_timeout):
                return session.conn.recv()
            # Soft interrupt first: the worker raises KeyboardInterrupt and keeps its state.
            session.signal(signal.SIGINT)
            if session.conn.poll(INTERRUPT_GRACE_SECONDS):
                result = session.conn.recv()
                result["stderr"] = result.get("stderr", "") + _notice(
                    f"The cell was stopped after {self.execution_timeout:.0f} s. Your variables were kept."
                )
                return result
        except (EOFError, OSError, BrokenPipeError):
            self.drop(session.session_id, reason="the worker stopped unexpectedly, probably out of memory")
            return _error_result(
                "The Python worker stopped unexpectedly (often because it ran out of memory). "
                "The session was reset: re-run the earlier cells."
            )
        self.drop(session.session_id, reason=f"a cell did not stop after {self.execution_timeout:.0f} s")
        return _error_result(
            f"The cell did not finish within {self.execution_timeout:.0f} s and could not be interrupted, "
            "so the session was reset. Re-run the earlier cells."
        )

    # -- internals -----------------------------------------------------------------

    def _spawn(self, session_id: str, initial_code: str) -> tuple[Session, dict[str, Any] | None]:
        self._reserve_slot()
        try:
            parent_conn, child_conn = _MP.Pipe()
            process = _MP.Process(
                target=worker.serve,
                args=(child_conn, initial_code),
                name=f"session-worker:{session_id[:40]}",
                # Not a daemon: birt's Beta4 starts its own processes during fit().
                daemon=False,
            )
            process.start()
            child_conn.close()
            if not parent_conn.poll(self.start_timeout):
                Session(session_id, process, parent_conn, initial_code).stop()
                raise RuntimeError("The Python worker took too long to start.")
            try:
                _, init_result = parent_conn.recv()
            except EOFError as error:
                raise RuntimeError("The Python worker exited during start-up.") from error
            return Session(session_id, process, parent_conn, initial_code), init_result
        finally:
            with self._lock:
                self._pending -= 1

    def _reserve_slot(self) -> None:
        while True:
            with self._lock:
                if len(self._sessions) + self._pending < self.max_workers:
                    self._pending += 1
                    return
                idle = [s for s in self._sessions.values() if not s.busy]
                victim = min(idle, key=lambda s: s.last_used) if idle else None
                if victim is None:
                    raise BackendBusy("All Python workers are busy. Please try again in a moment.")
                self._sessions.pop(victim.session_id, None)
                self._remember_expired(victim, "the server needed room for another participant")
            victim.stop()

    def _remember_expired(self, session: Session, reason: str) -> None:
        self._expired[session.session_id] = (session.initial_code, reason)
        while len(self._expired) > REMEMBERED_EXPIRED_SESSIONS:
            self._expired.popitem(last=False)

    def _reap_forever(self) -> None:
        while not self._stopping.wait(30):
            cutoff = time.time() - self.idle_ttl
            with self._lock:
                stale = [s for s in self._sessions.values() if not s.busy and s.last_used < cutoff]
            for session in stale:
                minutes = self.idle_ttl / 60
                self.drop(session.session_id, reason=f"it was idle for more than {minutes:.0f} min")

    # -- introspection -------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        now = time.time()
        with self._lock:
            sessions = list(self._sessions.values())
        rows = []
        for session in sorted(sessions, key=lambda s: s.last_used, reverse=True):
            rows.append(
                {
                    "session_id": session.session_id,
                    "pid": session.process.pid,
                    "busy": session.busy,
                    "executions": session.executions,
                    "age_seconds": round(now - session.created_at),
                    "idle_seconds": round(now - session.last_used),
                    "memory_mb": _memory_mb(session.process.pid),
                }
            )
        return {
            "active": len(rows),
            "busy": sum(1 for row in rows if row["busy"]),
            "max_workers": self.max_workers,
            "idle_ttl_seconds": self.idle_ttl,
            "execution_timeout_seconds": self.execution_timeout,
            "sessions": rows,
        }


def _memory_mb(pid: int | None) -> float | None:
    if pid is None:
        return None
    try:
        import psutil

        return round(psutil.Process(pid).memory_info().rss / 1_048_576, 1)
    except Exception:
        return None
