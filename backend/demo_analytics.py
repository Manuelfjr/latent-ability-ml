"""Write realistic sample events so the admin dashboard can be previewed locally.

    poetry run python -m backend.demo_analytics /tmp/demo-analytics.jsonl
"""

from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PAGES = ["/", "/section-1/", "/section-2/", "/section-2-activity/", "/section-3/", "/section-3-activity/", "/section-5-activity/", "/references/"]
NOTEBOOK_PAGES = {"/section-2-activity/": "section-2-activity", "/section-3-activity/": "section-3-activity", "/section-5-activity/": "section-5-activity"}
CLIENTS = [
    ("MacIntel", "1512x857", "Europe/London"),
    ("Win32", "1920x969", "Europe/London"),
    ("MacIntel", "1440x789", "America/Recife"),
    ("Linux x86_64", "1366x657", "Europe/Paris"),
    ("iPhone", "390x664", "Europe/London"),
]


def make_events(count: int = 160, seed: int = 3) -> list[dict]:
    rng = random.Random(seed)
    now = datetime.now(timezone.utc)
    visitors = [f"tab-{rng.randrange(10**12)}-{rng.randrange(36**6):06x}" for _ in range(14)]
    events = []
    minutes_ago = count * 0.9
    for _ in range(count):
        minutes_ago -= rng.uniform(0.1, 1.7)
        tab = rng.choice(visitors)
        platform, viewport, tz = CLIENTS[sum(map(ord, tab)) % len(CLIENTS)]
        page = rng.choice(PAGES)
        notebook = NOTEBOOK_PAGES.get(page, "")
        event_type = "page_view"
        if notebook:
            event_type = rng.choices(["page_view", "run_cell", "run_demo", "export_ipynb"], weights=[3, 8, 3, 1])[0]
        events.append(
            {
                "timestamp": (now - timedelta(minutes=max(minutes_ago, 0))).isoformat(),
                "event_type": event_type,
                "page": page,
                "title": "Latent Ability",
                "notebook_id": notebook if event_type != "page_view" else "",
                "session_id": f"{tab}:{notebook}" if notebook else tab,
                "runtime_mode": rng.choice(["cloud", "cloud", "cloud", "browser"]) if event_type in ("run_cell", "run_demo") else "",
                "platform": platform,
                "language": "en-GB",
                "timezone": tz,
                "viewport": viewport,
                "cell_label": f"Task {rng.randint(1, 4)}" if event_type == "run_cell" else "",
                "demo_id": "beta4-curve-lab" if event_type == "run_demo" else "",
                "ip_masked": f"81.2.{rng.randint(10, 250)}.*",
            }
        )
    return events


def main() -> None:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "backend/data/demo-analytics.jsonl")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(json.dumps(event) + "\n" for event in make_events()), encoding="utf-8")
    print(f"Wrote sample events to {target}")


if __name__ == "__main__":
    main()
