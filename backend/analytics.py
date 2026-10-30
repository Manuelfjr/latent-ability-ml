"""Append-only JSONL store for the optional admin analytics."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

MAX_FIELD_CHARS = 300


def clip(value: Any, limit: int = MAX_FIELD_CHARS) -> str:
    return str(value or "")[:limit]


class AnalyticsStore:
    """Keeps the most recent ``max_rows`` events.

    Events are appended (cheap) and the file is compacted only once it grows to
    twice the limit, so a busy workshop never rewrites the file on every event.
    """

    def __init__(self, path: Path, max_rows: int) -> None:
        self.path = path
        self.max_rows = max(1, max_rows)
        self._lock = threading.Lock()
        self._line_count: int | None = None

    def append(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False) + "\n"
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self._line_count is None:
                self._line_count = len(self._read_lines())
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line)
            self._line_count += 1
            if self._line_count > 2 * self.max_rows:
                kept = self._read_lines()[-self.max_rows :]
                tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
                tmp_path.write_text("".join(f"{entry}\n" for entry in kept), encoding="utf-8")
                tmp_path.replace(self.path)
                self._line_count = len(kept)

    def read(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Most recent events first."""
        with self._lock:
            lines = self._read_lines()
        events: list[dict[str, Any]] = []
        for line in reversed(lines[-(limit or self.max_rows) :]):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events

    def _read_lines(self) -> list[str]:
        if not self.path.exists():
            return []
        return [line for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
