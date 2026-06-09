#!/usr/bin/env python3
"""SessionStart + UserPromptSubmit hook — re-anchor + keep the kernel-operations catalog in front
of Claude, so the field expert converses and Claude invokes the Pod operations itself.

Why: the Pod is meant to run as a conversation. The expert should never have to know or type a
skill/command. Claude recognises when an operation applies (orient, goal, flowcheck, propose/
ratify, promote, distill, record-outcome) and invokes it, then says so in its reply. For that to
hold across a long session, Claude's awareness of its own operations must be refreshed — context
decays, and after compaction it is gone. This hook re-injects it.

Behaviour (stdout from these two events is added to Claude's context):
  - SessionStart (startup / resume / clear / compact): inject the full re-anchor (goal, phase) +
    the conversational rule + the operations catalog. This is the boot re-anchor (the anatomy
    boot sequence) and the drift counter (term.drift: re-anchor each session), and it re-arms
    after compaction.
  - UserPromptSubmit: every REFRESH_EVERY turns, inject a compact one-line reminder so awareness
    does not decay mid-session ("from time to time"). Throttled via a counter; silent otherwise.

Best-effort: never blocks; on any error prints nothing and exits 0.
"""
import sys, os, json, pathlib

REFRESH_EVERY = 8  # UserPromptSubmit: re-inject the compact reminder every N turns


def _read(p):
    try:
        return pathlib.Path(p).read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _goal(root):
    for line in _read(root / "pod" / "pod.yml").splitlines():
        s = line.strip()
        if s.startswith("output:"):
            return s.split(":", 1)[1].strip()
    return ""


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    event = payload.get("hook_event_name") or payload.get("hookEventName") or ""
    root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())

    # only act inside a Pod
    if not (root / "pod" / "state").exists() and not (root / "pod" / "pod.yml").exists():
        return

    phase = _read(root / "pod" / "state" / "current-phase")

    # --- UserPromptSubmit: throttled compact reminder ---
    if event == "UserPromptSubmit":
        counter = root / "pod" / ".agent" / ".kernel-refresh-counter"
        try:
            n = int(_read(counter) or "0")
        except Exception:
            n = 0
        n += 1
        try:
            counter.parent.mkdir(parents=True, exist_ok=True)
            counter.write_text(str(n))
        except Exception:
            pass
        if n % REFRESH_EVERY != 0:
            return
        print(
            f"[kernel reminder] Pod phase: {phase or '?'}. You invoke kernel operations yourself "
            f"when the conversation warrants (orient / goal / flowcheck / propose / ratify / "
            f"promote / distill / record-outcome) and say so in your reply. The field expert only "
            f"converses — never ask them to run a command."
        )
        return

    # --- SessionStart (and any other event treated as a full inject) ---
    catalog = _read(root / ".claude" / "governance" / "operations-catalog.md")
    goal = _goal(root)
    out = ["[kernel re-anchor]"]
    if goal:
        out.append(f"Goal (confirm with the expert before Understand work): {goal}")
    out.append(f"Current phase: {phase or '1 (Understand)'}")
    out.append("Anchor to this record, not to conversational momentum (counters drift).")
    out += [
        "",
        "[how this Pod runs]",
        "The field expert converses in plain language and never invokes skills or commands. You "
        "recognise when a kernel operation applies and invoke it yourself, then state in your "
        "reply which one you ran and why.",
    ]
    if catalog:
        out += ["", catalog]
    print("\n".join(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never block
        sys.stderr.write(f"kernel-context: non-fatal: {e}\n")
    sys.exit(0)
