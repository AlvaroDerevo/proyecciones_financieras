#!/usr/bin/env python3
"""Stop + PreCompact hook — append conversation turns to pod/journal/chat.jsonl (append-only).

Sources the turns from the Claude Code session transcript (the hook receives its path as
`transcript_path` on stdin) and reconciles against a watermark, so each run appends only the
turns added since last time. This is the chat-journal sibling of log-event.py: same
reconcile-from-watermark discipline, different source (the transcript, not the state files).

Wire it on two events:
  - Stop       -> fires once per assistant turn; captures the turn just completed.
  - PreCompact -> fires before the transcript is compacted; flushes any unwritten turns so
                  compaction never eats history.

Scope note: Claude Code has no concept of a focused *section*, so each turn is scoped to the
current phase (pod/state/current-phase), not to a section. Section-scoped journaling is only
available with a custom kernel. Recorded turns carry `scope` = the phase at write time.

First run (no watermark): captures every conversational turn currently in the transcript and
sets the watermark. Unlike log-event.py this DOES capture history on first run — chat turns
carry their own real timestamps from the transcript, so writing them is faithful, not
fabricated. For a Pod that ships with this hook from creation, the first turn is captured.

Best-effort: never blocks the agent (always exits 0). A journal failure must never halt work.
"""
import sys, os, json, pathlib, hashlib
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


def _entry_ts(e):
    return e.get("created_at") or e.get("timestamp") or (e.get("message") or {}).get("created_at") or ""


def _entry_uuid(e):
    u = e.get("uuid")
    if u:
        return u
    # stable fallback id when an entry has no uuid
    basis = (_entry_ts(e) + json.dumps(e.get("message", ""), sort_keys=True)).encode("utf-8")
    return "sha:" + hashlib.sha1(basis).hexdigest()[:16]


def _extract_turn(e):
    """Return (role, text, tools) for a conversational entry, or None to skip it."""
    typ = e.get("type")
    if typ not in ("user", "assistant") and not isinstance(e.get("message"), dict):
        return None
    msg = e.get("message")
    if not isinstance(msg, dict):
        return None
    role = msg.get("role") or typ
    if role not in ("user", "assistant"):
        return None

    content = msg.get("content")
    text_parts, tools = [], []
    if isinstance(content, str):
        text_parts.append(content)
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            bt = block.get("type")
            if bt == "text" and block.get("text"):
                text_parts.append(block["text"])
            elif bt == "tool_use" and block.get("name"):
                tools.append(block["name"])
            # thinking / tool_result are intentionally excluded from the chat journal
    text = "\n".join(p.strip() for p in text_parts if p and p.strip()).strip()

    if not text and not tools:
        return None  # pure thinking / tool_result / empty — not a conversation turn
    return role, text, tools


def main():
    # Hook input arrives as JSON on stdin.
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    tpath = payload.get("transcript_path")
    if not tpath:
        return
    tpath = pathlib.Path(os.path.expanduser(tpath))
    if not tpath.exists():
        return

    root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    journal = root / "pod" / "journal" / "chat.jsonl"
    phase_file = root / "pod" / "state" / "current-phase"
    wm_file = root / "pod" / ".agent" / ".chat-watermark.json"
    pod_yml = root / "pod" / "pod.yml"

    # Only act inside a Pod repo.
    if not journal.parent.exists() and not phase_file.exists():
        return

    pod_id = "unknown"
    if pod_yml.exists():
        for line in pod_yml.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("id:"):
                pod_id = line.split(":", 1)[1].strip()
                break

    phase = phase_file.read_text(encoding="utf-8").strip() if phase_file.exists() else ""

    # Read transcript (JSONL; tolerate blank/garbage lines).
    entries = []
    for line in tpath.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    if not entries:
        return

    # Locate the cutoff from the watermark.
    start = 0
    wm = None
    if wm_file.exists():
        try:
            wm = json.loads(wm_file.read_text(encoding="utf-8"))
        except Exception:
            wm = None
    if wm:
        last_uuid, last_ts = wm.get("last_uuid"), wm.get("last_ts")
        uuids = [_entry_uuid(e) for e in entries]
        if last_uuid in uuids:
            start = uuids.index(last_uuid) + 1
        elif last_ts:
            start = next((i for i, e in enumerate(entries) if _entry_ts(e) > last_ts), len(entries))
        else:
            return  # watermark exists but can't be located — bail rather than risk duplicates

    new = entries[start:]
    if not new:
        return

    journal.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with journal.open("a", encoding="utf-8") as fh:
        for e in new:
            turn = _extract_turn(e)
            if turn is None:
                continue
            role, text, tools = turn
            rec = {
                "ts": _entry_ts(e) or _now(),
                "role": role,
                "scope": phase,            # phase-scoped (see module docstring)
                "text": text,
                "tools": tools,
                "uuid": _entry_uuid(e),
                "pod": pod_id,
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1

    # Advance the watermark past everything scanned this run (incl. non-conversational tail).
    last = new[-1]
    wm_file.parent.mkdir(parents=True, exist_ok=True)
    wm_file.write_text(json.dumps({"last_uuid": _entry_uuid(last), "last_ts": _entry_ts(last)}))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never block the agent
        sys.stderr.write(f"log-chat: non-fatal: {exc}\n")
    sys.exit(0)
