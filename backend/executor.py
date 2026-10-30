"""Cell execution logic.

This module runs inside a session worker process (see ``backend.worker``), so the
redirections and matplotlib state below never leak between participants.
"""

from __future__ import annotations

import ast
import base64
import io
import itertools
import linecache
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

MAX_STREAM_CHARS = 200_000
MAX_FIGURES = 20
FIGURE_DPI = 150

_cell_counter = itertools.count(1)
_active_collector: OutputCollector | None = None


class OutputCollector:
    """Rich outputs (figures and HTML) produced while a cell runs."""

    def __init__(self) -> None:
        self.figures: list[str] = []
        self.html: list[str] = []

    def add_figure(self, figure: Any) -> None:
        if len(self.figures) >= MAX_FIGURES:
            return
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png", bbox_inches="tight", dpi=FIGURE_DPI)
        self.figures.append(base64.b64encode(buffer.getvalue()).decode("ascii"))

    def flush_figures(self) -> None:
        # Only touch pyplot when the cell actually used it.
        plt = sys.modules.get("matplotlib.pyplot")
        if plt is None:
            return
        try:
            for number in plt.get_fignums():
                self.add_figure(plt.figure(number))
        finally:
            plt.close("all")

    def display(self, *values: Any) -> None:
        for value in values:
            if value is None:
                continue
            if _is_matplotlib_figure(value):
                self.add_figure(value)
                plt = sys.modules.get("matplotlib.pyplot")
                if plt is not None:
                    plt.close(value)
                continue
            html = _html_repr(value)
            if html:
                self.html.append(html)
            else:
                print(repr(value))


def _is_matplotlib_figure(value: Any) -> bool:
    figure_module = sys.modules.get("matplotlib.figure")
    return figure_module is not None and isinstance(value, figure_module.Figure)


def _html_repr(value: Any) -> str | None:
    if isinstance(value, type):
        return None
    module_name = getattr(value.__class__, "__module__", "") or ""
    if module_name.startswith("plotly") and hasattr(value, "to_html"):
        try:
            return value.to_html(include_plotlyjs="cdn", full_html=False)
        except Exception:
            return None
    repr_html = getattr(value, "_repr_html_", None)
    if callable(repr_html):
        try:
            html = repr_html()
        except Exception:
            return None
        return html if isinstance(html, str) and html else None
    return None


def show(*_args: Any, **_kwargs: Any) -> None:
    """Replacement for ``plt.show`` that renders figures into the cell output."""
    if _active_collector is not None:
        _active_collector.flush_figures()


def display(*values: Any) -> None:
    """Jupyter-like ``display`` available in every cell."""
    if _active_collector is not None:
        _active_collector.display(*values)
    else:
        for value in values:
            print(repr(value))


def new_context() -> dict[str, Any]:
    return {
        "__builtins__": __builtins__,
        "__name__": "__main__",
        "display": display,
    }


def _compile_cell(code: str, filename: str) -> tuple[Any, Any]:
    linecache.cache[filename] = (len(code), None, code.splitlines(keepends=True), filename)
    tree = ast.parse(code, filename=filename, mode="exec")
    body = list(tree.body)
    trailing_expr = body[-1] if body and isinstance(body[-1], ast.Expr) else None
    executable = ast.Module(body=body[:-1] if trailing_expr else body, type_ignores=[])
    compiled_exec = compile(executable, filename, "exec")
    compiled_expr = compile(ast.Expression(trailing_expr.value), filename, "eval") if trailing_expr else None
    return compiled_exec, compiled_expr


def _format_exception(error: BaseException) -> str:
    # Hide the executor's own frames so the traceback starts at the user's cell.
    tb = error.__traceback__
    while tb is not None and not tb.tb_frame.f_code.co_filename.startswith("<cell"):
        tb = tb.tb_next
    return "".join(traceback.format_exception(type(error), error, tb))


def _truncate(text: str) -> str:
    if len(text) <= MAX_STREAM_CHARS:
        return text
    hidden = len(text) - MAX_STREAM_CHARS
    return text[:MAX_STREAM_CHARS] + f"\n… output truncated ({hidden:,} more characters).\n"


def execute_code(context: dict[str, Any], code: str, on_start: Any = None, on_finish: Any = None) -> dict[str, Any]:
    """Run ``code`` in ``context`` and return the JSON payload the site expects.

    ``on_start``/``on_finish`` bracket the user code so the worker knows when an
    interrupt (timeout) may be raised.
    """
    global _active_collector
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    collector = OutputCollector()
    success = True
    filename = f"<cell-{next(_cell_counter)}>"
    _active_collector = collector

    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            try:
                compiled_exec, compiled_expr = _compile_cell(code, filename)
                if on_start:
                    on_start()
                try:
                    exec(compiled_exec, context, context)
                    value = eval(compiled_expr, context, context) if compiled_expr is not None else None
                finally:
                    if on_finish:
                        on_finish()
                if value is not None:
                    collector.display(value)
            except BaseException as error:  # noqa: BLE001 - SystemExit/KeyboardInterrupt must not kill the worker
                success = False
                stderr_buffer.write(_format_exception(error))
            try:
                collector.flush_figures()
            except Exception as error:
                stderr_buffer.write(f"Could not render figures: {error}\n")
    finally:
        # The linecache entry is kept so later tracebacks through functions
        # defined in this cell still show their source lines.
        _active_collector = None

    return {
        "success": success,
        "stdout": _truncate(stdout_buffer.getvalue()),
        "stderr": _truncate(stderr_buffer.getvalue()),
        "figures": collector.figures,
        "html": collector.html,
    }
