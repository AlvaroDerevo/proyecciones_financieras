#!/usr/bin/env python3
"""PostToolUse hook — append Pod-level events to pod/journal/events.jsonl (append-only).

Reconciles live state against a watermark and logs only genuine *forward* changes:
  - pod/state/current-phase changes        -> {"event":"phase-changed",...}
  - new lines in pod/journal/decisions.log -> {"event":"decision-recorded",...}

Catches changes regardless of which tool made them (Write/Edit/Bash append), because it
compares state rather than parsing the tool call. Best-effort: never blocks the agent
(always exits 0). On first run it records a silent watermark and emits nothing, so existing
history is never backfilled.
"""
import sys, os, json, pathlib
from datetime import datetime, timezone


def main():
    root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    journal = root / "pod" / "journal" / "events.jsonl"
    phase_file = root / "pod" / "state" / "current-phase"
    decisions = root / "pod" / "journal" / "decisions.log"
    wm_file = root / "pod" / ".agent" / ".events-watermark.json"
    pod_yml = root / "pod" / "pod.yml"

    # Only act inside a Pod repo.
    if not phase_file.exists() or not journal.parent.exists():
        return

    pod_id = "unknown"
    if pod_yml.exists():
        for line in pod_yml.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("id:"):
                pod_id = line.split(":", 1)[1].strip()
                break

    cur_phase = phase_file.read_text(encoding="utf-8").strip()
    dec_lines = []
    if decisions.exists():
        dec_lines = [l for l in decisions.read_text(encoding="utf-8").splitlines()
                     if l.strip() and not l.strip().startswith("#")]
    dec_count = len(dec_lines)

    # First run: capture baseline, emit nothing (no backfill of existing history).
    if not wm_file.exists():
        wm_file.parent.mkdir(parents=True, exist_ok=True)
        wm_file.write_text(json.dumps({"phase": cur_phase, "decisions": dec_count}))
        return

    try:
        wm = json.loads(wm_file.read_text(encoding="utf-8"))
    except Exception:
        wm = {"phase": cur_phase, "decisions": dec_count}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    events = []

    if cur_phase and cur_phase != str(wm.get("phase", "")):
        events.append({"event": "phase-changed", "at": now, "pod": pod_id,
                       "from": wm.get("phase"), "phase": cur_phase})

    prev = int(wm.get("decisions", dec_count))
    if dec_count > prev:
        for line in dec_lines[prev:]:
            parts = [p.strip() for p in line.split("|")]
            events.append({"event": "decision-recorded", "at": now, "pod": pod_id,
                           "action": parts[1] if len(parts) > 1 else "",
                           "ref": parts[2] if len(parts) > 2 else ""})

    if events:
        with journal.open("a", encoding="utf-8") as fh:
            for e in events:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")

    wm["phase"] = cur_phase
    wm["decisions"] = dec_count
    wm_file.write_text(json.dumps(wm))


if __name__ == "__main__":
    try:
        sys.stdin.read()  # drain the hook payload; reconciliation doesn't need it
    except Exception:
        pass
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
