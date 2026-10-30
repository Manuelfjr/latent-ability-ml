"""Server-rendered admin dashboard (``GET /admin``)."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from html import escape
from typing import Any

EVENT_LABELS = {
    "page_view": "Page view",
    "run_cell": "Cell run",
    "run_demo": "Demo run",
    "export_ipynb": "Notebook export",
    "share_notebook": "Notebook share",
    "email_summary": "Email summary",
}


def _label(event_type: str) -> str:
    return EVENT_LABELS.get(event_type, event_type.replace("_", " ").capitalize() or "Unknown")


def _short_session(session_id: str) -> str:
    if not session_id:
        return "—"
    # Site tab ids look like "tab-<timestamp>-<random>"; the random part is the readable bit.
    return session_id.split(":", 1)[0].rsplit("-", 1)[-1][:12]


def _bars(counter: Counter[str], label_fn: Any = str, limit: int = 6) -> str:
    items = counter.most_common(limit)
    if not items:
        return "<p class='empty'>Nothing recorded yet.</p>"
    peak = items[0][1]
    rows = []
    for key, count in items:
        width = max(2.0, 100 * count / peak)
        label = escape(label_fn(key))
        rows.append(
            f"<li class='bar' title='{label}: {count}'>"
            f"<span class='bar__label'>{label}</span>"
            f"<span class='bar__track'><span class='bar__fill' style='width:{width:.1f}%'></span></span>"
            f"<span class='bar__value'>{count}</span></li>"
        )
    return f"<ul class='bars'>{''.join(rows)}</ul>"


def _format_duration(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    return f"{seconds // 3600}h {seconds % 3600 // 60}m"


def _sessions_panel(stats: dict[str, Any]) -> str:
    sessions = stats.get("sessions", [])
    if not sessions:
        body = "<p class='empty'>No Python sessions are running right now.</p>"
    else:
        rows = []
        for row in sessions:
            state = "<span class='pill pill--busy'>Running</span>" if row["busy"] else "<span class='pill'>Idle</span>"
            memory = f"{row['memory_mb']:.0f} MB" if row.get("memory_mb") is not None else "—"
            notebook = escape(row["session_id"].split(":", 1)[-1])
            rows.append(
                "<tr>"
                f"<td><span class='mono'>{escape(_short_session(row['session_id']))}</span></td>"
                f"<td>{notebook}</td>"
                f"<td>{state}</td>"
                f"<td class='num'>{row['executions']}</td>"
                f"<td class='num'>{_format_duration(row['idle_seconds'])}</td>"
                f"<td class='num'>{_format_duration(row['age_seconds'])}</td>"
                f"<td class='num'>{memory}</td>"
                "</tr>"
            )
        body = (
            "<div class='table-wrap'><table><thead><tr>"
            "<th>Tab</th><th>Notebook</th><th>State</th><th class='num'>Cells</th>"
            "<th class='num'>Idle</th><th class='num'>Age</th><th class='num'>Memory</th>"
            f"</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
        )
    return (
        "<section class='card'>"
        "<header class='card__head'><h2>Live Python sessions</h2>"
        f"<span class='card__meta'>Idle sessions close after {stats.get('idle_ttl_seconds', 0) / 60:.0f} min · "
        f"cells stop after {stats.get('execution_timeout_seconds', 0):.0f} s</span></header>"
        f"{body}</section>"
    )


def _event_rows(events: list[dict[str, Any]]) -> str:
    rows = []
    for event in events:
        event_type = str(event.get("event_type", ""))
        timestamp = str(event.get("timestamp", ""))
        detail = event.get("cell_label") or event.get("demo_id") or event.get("notebook_id") or ""
        runtime = str(event.get("runtime_mode", ""))
        rows.append(
            f"<tr data-type='{escape(event_type)}'>"
            f"<td><time datetime='{escape(timestamp)}' title='{escape(timestamp)}'>{escape(timestamp[:19].replace('T', ' '))}</time></td>"
            f"<td><span class='tag tag--{escape(event_type)}'>{escape(_label(event_type))}</span></td>"
            f"<td><span class='path'>{escape(str(event.get('page', '')))}</span>"
            f"{f'<span class=sub>{escape(str(detail))}</span>' if detail else ''}</td>"
            f"<td>{escape(runtime) if runtime else '—'}</td>"
            f"<td><span class='mono'>{escape(_short_session(str(event.get('session_id', ''))))}</span></td>"
            f"<td>{escape(str(event.get('ip_masked', '')))}"
            f"<span class='sub'>{escape(str(event.get('platform', '')))} · {escape(str(event.get('viewport', '')))}</span></td>"
            f"<td>{escape(str(event.get('timezone', '')) or '—')}</td>"
            "</tr>"
        )
    return "".join(rows) or "<tr><td colspan='7' class='empty'>No events recorded yet.</td></tr>"


def render_admin_html(events: list[dict[str, Any]], stats: dict[str, Any]) -> str:
    types = Counter(str(event.get("event_type") or "unknown") for event in events)
    pages = Counter(str(event.get("page") or "/") for event in events)
    tabs = {str(event.get("session_id")).split(":", 1)[0] for event in events if event.get("session_id")}
    cell_runs = types.get("run_cell", 0) + types.get("run_demo", 0)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    filter_chips = "".join(
        f"<button type='button' class='chip' data-filter='{escape(key)}'>{escape(_label(key))} <span>{count}</span></button>"
        for key, count in types.most_common()
    )
    kpis = [
        ("Events", len(events), f"last {len(events)} kept"),
        ("Visitors", len(tabs), "distinct browser tabs"),
        ("Page views", types.get("page_view", 0), "across all pages"),
        ("Cells run", cell_runs, "cells and interactive demos"),
        ("Live sessions", f"{stats.get('active', 0)}/{stats.get('max_workers', 0)}", f"{stats.get('busy', 0)} running now"),
    ]
    kpi_html = "".join(
        f"<div class='kpi'><span class='kpi__label'>{label}</span>"
        f"<span class='kpi__value'>{value}</span><span class='kpi__hint'>{hint}</span></div>"
        for label, value, hint in kpis
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Workshop Admin</title>
  <style>
    :root {{
      --bg: #f6f2ea; --surface: #ffffff; --surface-2: #fbf8f3; --line: #e8dfd1;
      --ink: #1d1b19; --ink-2: #5c554c; --ink-3: #8a8277;
      --accent: #ab2330; --accent-soft: #f6e4e2; --good: #2f7a4f; --good-soft: #e3f1e8;
      --bar: #ab2330; --shadow: 0 1px 2px rgba(60, 40, 20, .05), 0 8px 24px rgba(60, 40, 20, .06);
      color-scheme: light;
    }}
    @media (prefers-color-scheme: dark) {{
      :root:not([data-theme="light"]) {{
        --bg: #161412; --surface: #1f1c19; --surface-2: #26221e; --line: #36302a;
        --ink: #f1ebe3; --ink-2: #c2b8ab; --ink-3: #8f8679;
        --accent: #e0737a; --accent-soft: #3a2224; --good: #7cc79a; --good-soft: #1f3327;
        --bar: #d65a63; --shadow: none; color-scheme: dark;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: var(--bg); color: var(--ink);
      font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif;
      -webkit-font-smoothing: antialiased;
    }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 40px 24px 64px; }}
    .top {{ display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 16px; margin-bottom: 28px; }}
    .eyebrow {{ margin: 0 0 6px; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--accent); font-weight: 600; }}
    h1 {{ margin: 0; font: 600 30px/1.15 "Palatino Linotype", Palatino, Georgia, serif; letter-spacing: -.01em; }}
    .top p {{ margin: 6px 0 0; color: var(--ink-2); }}
    .actions {{ display: flex; align-items: center; gap: 10px; color: var(--ink-3); font-size: 13px; }}
    .status {{ display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 999px;
      background: var(--good-soft); color: var(--good); font-weight: 600; font-size: 13px; }}
    .status::before {{ content: ""; width: 8px; height: 8px; border-radius: 50%; background: currentColor; }}
    .btn {{ border: 1px solid var(--line); background: var(--surface); color: var(--ink); border-radius: 10px;
      padding: 7px 12px; font: inherit; font-size: 13px; cursor: pointer; }}
    .btn:hover {{ border-color: var(--ink-3); }}
    .btn[aria-pressed="true"] {{ background: var(--accent-soft); border-color: var(--accent); color: var(--accent); }}
    .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(160px, 100%), 1fr)); gap: 14px; margin-bottom: 18px; }}
    .kpi {{ background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px;
      display: flex; flex-direction: column; gap: 2px; box-shadow: var(--shadow); }}
    .kpi__label {{ font-size: 13px; color: var(--ink-2); }}
    .kpi__value {{ font-size: 30px; font-weight: 650; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }}
    .kpi__hint {{ font-size: 12px; color: var(--ink-3); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(340px, 100%), 1fr)); gap: 18px; margin-bottom: 18px; }}
    .card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 18px; padding: 20px 22px;
      box-shadow: var(--shadow); min-width: 0; margin-bottom: 18px; }}
    .grid .card {{ margin-bottom: 0; }}
    .card__head {{ display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px; margin-bottom: 14px; }}
    h2 {{ margin: 0; font-size: 16px; font-weight: 650; }}
    .card__meta {{ font-size: 12px; color: var(--ink-3); }}
    .bars {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }}
    .bar {{ display: grid; grid-template-columns: minmax(0, 38%) minmax(40px, 1fr) auto; align-items: center; gap: 12px; font-size: 14px; }}
    .bar__label {{ color: var(--ink-2); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .bar__track {{ height: 10px; border-radius: 4px; background: var(--surface-2); overflow: hidden; }}
    .bar__fill {{ display: block; height: 100%; background: var(--bar); border-radius: 0 4px 4px 0; }}
    .bar:hover .bar__fill {{ filter: brightness(1.12); }}
    .bar__value {{ min-width: 2.5ch; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 14px; }}
    .search {{ flex: 1 1 220px; min-width: 0; border: 1px solid var(--line); background: var(--surface-2); color: var(--ink);
      border-radius: 10px; padding: 8px 12px; font: inherit; font-size: 14px; }}
    .search:focus, .btn:focus-visible, .chip:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
    .chip {{ border: 1px solid var(--line); background: var(--surface); color: var(--ink-2); border-radius: 999px;
      padding: 5px 11px; font: inherit; font-size: 13px; cursor: pointer; }}
    .chip span {{ color: var(--ink-3); margin-left: 2px; }}
    .chip[aria-pressed="true"] {{ background: var(--ink); color: var(--surface); border-color: var(--ink); }}
    .chip[aria-pressed="true"] span {{ color: inherit; opacity: .7; }}
    .table-wrap {{ overflow-x: auto; margin: 0 -22px; padding: 0 22px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th {{ text-align: left; font-size: 12px; font-weight: 600; color: var(--ink-3); text-transform: uppercase;
      letter-spacing: .06em; padding: 0 12px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; }}
    td {{ padding: 12px; border-bottom: 1px solid var(--line); vertical-align: top; }}
    tbody tr:last-child td {{ border-bottom: 0; }}
    tbody tr:hover td {{ background: var(--surface-2); }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; color: var(--ink-2); }}
    .path {{ font-weight: 500; }}
    .sub {{ display: block; font-size: 12px; color: var(--ink-3); margin-top: 2px; }}
    time {{ white-space: nowrap; color: var(--ink-2); }}
    .tag {{ display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 12px; font-weight: 600;
      background: var(--surface-2); color: var(--ink-2); border: 1px solid var(--line); white-space: nowrap; }}
    .tag--run_cell, .tag--run_demo {{ background: var(--accent-soft); color: var(--accent); border-color: transparent; }}
    .pill {{ font-size: 12px; font-weight: 600; color: var(--ink-3); }}
    .pill--busy {{ color: var(--good); }}
    .empty {{ color: var(--ink-3); text-align: center; padding: 18px 0; margin: 0; }}
    footer {{ color: var(--ink-3); font-size: 12px; text-align: center; margin-top: 28px; }}
    footer code {{ background: var(--surface-2); padding: 1px 6px; border-radius: 6px; }}
    @media (max-width: 640px) {{
      .wrap {{ padding: 24px 16px 48px; }} h1 {{ font-size: 24px; }}
      .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
      .kpi {{ padding: 12px 14px; }} .kpi__value {{ font-size: 24px; }}
      .card {{ padding: 16px; }} .table-wrap {{ margin: 0 -16px; padding: 0 16px; }}
    }}
  </style>
</head>
<body>
  <main class="wrap">
    <header class="top">
      <div>
        <p class="eyebrow">Latent Ability · Workshop backend</p>
        <h1>Admin overview</h1>
        <p>What participants are doing in the workshop site, and which Python sessions are live.</p>
      </div>
      <div class="actions">
        <span class="status">Backend online</span>
        <button type="button" class="btn" id="auto-refresh" aria-pressed="false">Auto-refresh</button>
        <button type="button" class="btn" onclick="location.reload()">Refresh</button>
      </div>
    </header>

    <section class="kpis" aria-label="Summary">{kpi_html}</section>

    <div class="grid">
      <section class="card">
        <header class="card__head"><h2>Activity by type</h2><span class="card__meta">recent events</span></header>
        {_bars(types, _label)}
      </section>
      <section class="card">
        <header class="card__head"><h2>Most visited pages</h2><span class="card__meta">all event types</span></header>
        {_bars(pages)}
      </section>
    </div>

    {_sessions_panel(stats)}

    <section class="card">
      <header class="card__head"><h2>Recent events</h2><span class="card__meta" id="event-count">{len(events)} events</span></header>
      <div class="toolbar">
        <input class="search" id="event-search" type="search" placeholder="Search page, notebook, session, timezone…" aria-label="Search events" />
        <button type="button" class="chip" data-filter="" aria-pressed="true">All <span>{len(events)}</span></button>
        {filter_chips}
      </div>
      <div class="table-wrap">
        <table id="events">
          <thead><tr><th>When</th><th>Event</th><th>Page</th><th>Runtime</th><th>Tab</th><th>Client</th><th>Timezone</th></tr></thead>
          <tbody>{_event_rows(events)}</tbody>
        </table>
      </div>
    </section>

    <footer>Generated {generated} · JSON at <code>/admin/api/events</code> and <code>/admin/api/sessions</code> · enabled by <code>WORKSHOP_ENABLE_ADMIN_ANALYTICS</code></footer>
  </main>
  <script>
    (() => {{
      const rows = Array.from(document.querySelectorAll('#events tbody tr[data-type]'));
      const search = document.getElementById('event-search');
      const chips = Array.from(document.querySelectorAll('.chip'));
      const count = document.getElementById('event-count');
      let activeType = '';
      const apply = () => {{
        const term = search.value.trim().toLowerCase();
        let shown = 0;
        rows.forEach((row) => {{
          const visible = (!activeType || row.dataset.type === activeType) && (!term || row.textContent.toLowerCase().includes(term));
          row.hidden = !visible;
          if (visible) shown += 1;
        }});
        count.textContent = shown === rows.length ? `${{rows.length}} events` : `${{shown}} of ${{rows.length}} events`;
      }};
      search.addEventListener('input', apply);
      chips.forEach((chip) => chip.addEventListener('click', () => {{
        activeType = chip.dataset.filter;
        chips.forEach((other) => other.setAttribute('aria-pressed', String(other === chip)));
        apply();
      }}));

      const relative = new Intl.RelativeTimeFormat(undefined, {{ numeric: 'auto' }});
      const steps = [[60, 'second'], [3600, 'minute'], [86400, 'hour'], [Infinity, 'day']];
      document.querySelectorAll('time[datetime]').forEach((node) => {{
        const date = new Date(node.getAttribute('datetime'));
        if (Number.isNaN(date.getTime())) return;
        const seconds = (date.getTime() - Date.now()) / 1000;
        const [limit, unit] = steps.find(([max]) => Math.abs(seconds) < max);
        const divisor = {{ second: 1, minute: 60, hour: 3600, day: 86400 }}[unit];
        node.textContent = relative.format(Math.round(seconds / divisor), unit);
        node.title = date.toLocaleString();
      }});

      const toggle = document.getElementById('auto-refresh');
      let timer = null;
      const setAuto = (on) => {{
        toggle.setAttribute('aria-pressed', String(on));
        clearInterval(timer);
        timer = on ? setInterval(() => location.reload(), 15000) : null;
        try {{ on ? sessionStorage.setItem('admin-auto', '1') : sessionStorage.removeItem('admin-auto'); }} catch (_) {{}}
      }};
      toggle.addEventListener('click', () => setAuto(toggle.getAttribute('aria-pressed') !== 'true'));
      try {{ if (sessionStorage.getItem('admin-auto')) setAuto(true); }} catch (_) {{}}
    }})();
  </script>
</body>
</html>"""
