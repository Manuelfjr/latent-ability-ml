"""Session worker: one Python process per notebook session.

The parent (``backend.sessions``) talks to it through a ``multiprocessing`` pipe:

- the worker sends ``("ready", init_result)`` once the initial code has run;
- the parent sends ``("execute", code)`` and receives the result payload.

A timeout is delivered as SIGINT, which only interrupts while user code runs, so
the session keeps its variables after an interrupted cell.
"""

from __future__ import annotations

import os
import signal
import sys
import warnings
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
NOTEBOOK_DIR = ROOT_DIR / "notebooks"

_executing = False


def _on_sigint(_signum: int, _frame: Any) -> None:
    if _executing:
        raise KeyboardInterrupt("Execution interrupted: the cell exceeded the backend time limit.")


def _mark_executing(value: bool) -> None:
    global _executing
    _executing = value


def _prepare_environment() -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    for path in (NOTEBOOK_DIR, ROOT_DIR):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    warnings.filterwarnings("ignore", message=".*non-interactive.*")
    warnings.filterwarnings("ignore", message=".*Matplotlib is currently using agg.*")


def _preload() -> None:
    # Warm up the libraries every notebook uses; birt/TensorFlow stays lazy
    # because it costs ~400 MB per process.
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy  # noqa: F401
        import pandas  # noqa: F401

        from backend import executor

        plt.show = executor.show
    except Exception:
        pass


def serve(conn: Connection, initial_code: str) -> None:
    # Own process group, so the server can interrupt or kill this worker together
    # with any process the user's code started.
    if hasattr(os, "setpgrp"):
        os.setpgrp()
    signal.signal(signal.SIGINT, _on_sigint)
    _prepare_environment()
    _preload()

    from backend.executor import execute_code, new_context

    def run(code: str) -> dict[str, Any]:
        return execute_code(
            context,
            code,
            on_start=lambda: _mark_executing(True),
            on_finish=lambda: _mark_executing(False),
        )

    context = new_context()
    init_result = run(initial_code) if initial_code.strip() else None
    conn.send(("ready", init_result))

    while True:
        try:
            message = conn.recv()
        except (EOFError, OSError):
            break
        except KeyboardInterrupt:
            continue
        kind = message[0] if isinstance(message, tuple) and message else None
        if kind == "execute":
            conn.send(run(str(message[1])))
        elif kind == "stop":
            break
