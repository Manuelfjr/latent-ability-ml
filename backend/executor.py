from __future__ import annotations

import ast
import base64
import io
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from threading import Lock
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

NOTEBOOK_DIR = ROOT_DIR / "notebooks"
if str(NOTEBOOK_DIR) not in sys.path:
    sys.path.insert(0, str(NOTEBOOK_DIR))

CONTEXTS: dict[str, dict[str, Any]] = {}
CONTEXTS_LOCK = Lock()


def _new_context() -> dict[str, Any]:
    return {
        "__builtins__": __builtins__,
        "__name__": "__main__",
    }


def init_context(session_id: str, initial_code: str = "") -> None:
    with CONTEXTS_LOCK:
        context = _new_context()
        CONTEXTS[session_id] = context
    if initial_code.strip():
        exec(initial_code, context, context)


def reset_context(session_id: str, initial_code: str = "") -> None:
    init_context(session_id, initial_code=initial_code)


def drop_context(session_id: str) -> None:
    with CONTEXTS_LOCK:
        CONTEXTS.pop(session_id, None)


def get_or_create_context(session_id: str) -> dict[str, Any]:
    with CONTEXTS_LOCK:
        if session_id not in CONTEXTS:
            CONTEXTS[session_id] = _new_context()
        return CONTEXTS[session_id]


def _collect_figures() -> list[str]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return []

    encoded: list[str] = []
    try:
        for figure_number in plt.get_fignums():
            figure = plt.figure(figure_number)
            buffer = io.BytesIO()
            figure.savefig(buffer, format="png", bbox_inches="tight", dpi=180)
            encoded.append(base64.b64encode(buffer.getvalue()).decode("ascii"))
    finally:
        plt.close("all")
    return encoded


def execute_code(session_id: str, code: str) -> dict[str, Any]:
    context = get_or_create_context(session_id)
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    success = True

    try:
        tree = ast.parse(code, mode="exec")
        body = list(tree.body)
        trailing_expr = body[-1] if body and isinstance(body[-1], ast.Expr) else None
        executable = ast.Module(body=body[:-1] if trailing_expr else body, type_ignores=[])
        compiled_exec = compile(executable, "<cell>", "exec")
        compiled_expr = compile(ast.Expression(trailing_expr.value), "<cell>", "eval") if trailing_expr else None

        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(compiled_exec, context, context)
            if compiled_expr is not None:
                value = eval(compiled_expr, context, context)
                if value is not None:
                    print(value)
    except Exception:
        success = False
        stderr_buffer.write(traceback.format_exc())

    figures = _collect_figures()
    return {
        "success": success,
        "stdout": stdout_buffer.getvalue(),
        "stderr": stderr_buffer.getvalue(),
        "figures": figures,
    }
