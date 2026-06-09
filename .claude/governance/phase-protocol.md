---
id: spec.phase-protocol
kind: spec-addendum
status: ratified
ratified-by: pedro
ratified-at: 2026-06-04
applies-at: logos            # universal agent behavior, every Pod — not craft-specific
derived-from: pod.ccaf-readiness-cohort   # first Pod, verify-phase feedback (field expert: alvaro)
supersedes: []
cites:
  - flow.cca-f-readiness@experimental     # session 2026-06-04, the run these rules correct
revision: r002
---

# Phase Protocol — agent behavior across Understand → Plan → Build → Verify

The four-phase model defines *what content lives in each phase*. This addendum defines
*how the agent moves through them*. Two rules, both derived from the first Pod's run,
where their absence produced the session's two largest faults: a wrong goal carried
twelve minutes before the expert halted it, and output deliverables built two phases
early. Neither rule is craft-specific; both apply at the Lógos level to every Pod.

## rule.goal-first-understand

The agent's first action in a fresh Pod is to elicit the goal from the field expert —
what they are trying to solve, the objective of this Pod — and record it before any
other Understand work begins.

The goal is never inherited silently from a pre-filled field. If `pod.yml` carries an
`output:` or objective at scaffold time, the agent surfaces it for confirmation or
correction, not as a settled premise. Understand then proceeds as specified: context,
what is known and not known, inputs, constraints, stakeholders, open questions.

*Why.* In the first Pod the agent took `output: per-person analysis + banded read +
actionables` from `pod.yml` as given and ran toward it — ending the domain-map turn with
"how do you want to share the CVs?" The expert stopped it: the real problem was getting
ten people certified under a June deadline, not analyzing them individually. Eliciting
the goal at the start catches a wrong frame at minute one instead of minute twelve.

## rule.gated-phase-transition

The agent does not advance `current-phase` on its own. When it judges a phase's work done
— or the expert signals readiness — it asks whether to move to the next phase or whether
more remains in the current one. Advancing is a human decision, and it is recorded
(decision log + the phase-change event).

Scope clause — work belongs to the phase you are gated into. Understand *records
understanding* (context, sources, domain maps, open questions); Plan *records commitments*
(the plan itself, sequenced); Build *produces the output deliverables* — the artifacts the
Pod exists to hand off. Writing files in Understand and Plan is expected and is not
"building." Constructing the Pod's output deliverables before the Pod has been gated into
Build is out of phase.

*Why.* The first Pod never once asked before advancing, and it wrote two output
deliverables (the facilitator guide and the materials map) into `2-plan/sections/` while
`current-phase` still read `1`. The gate is the mechanism that keeps construction from
running ahead of a confirmed goal and an agreed plan.

*Rationale — the cost the gate protects is human time, not build time.* The first Pod's
friction was not generation latency; it was the expert's own complaint that the heavy
documents *"quita tiempo a las personas."* A long, complex, wrong deliverable is expensive
because a person must read, digest, and reject it — not because it took seconds to render.
So the gate is a *validation boundary measured in human-experienced wait*: cheap,
in-context previews come first and the expert steers on those; the heavy expansion into
complex external format is deferred until the shape is confirmed, and may run off the
expert's critical path. Total compute may rise under this trade, and that is acceptable —
human-experienced wait is the primary metric; the Pod's cost/rate budget is the backstop,
not the target. The preview→expand mechanism this points to — one canonical representation,
rendered cheap in-Pod and expanded to complex external format only on Build — is **not yet
locked**; recorded here as the gate's intent, to be specified once the mechanism settles.

---

## Inheritance — applying to every future Pod

These are Lógos invariants (`applies-at: logos`): true for every Pod regardless of craft,
not opt-in per Pod. For that to hold in practice the behavior must be carried by the
always-present base agent, not hand-copied into each Pod — copied invariants drift.

**Requirement.** Every Pod, at creation, boots with agent instructions that (i) open
Understand by eliciting and recording the goal, and (ii) gate phase transitions and
out-of-phase deliverable construction. A Pod that scaffolds without these is
non-conforming.

**Gap — the same one the events-hook hit.** This behavior lives in `.claude/` (CLAUDE.md
and the Pod-opening / transition commands), and `.claude/` machinery is not currently part
of the Pod Anatomy or the scaffold contract. Nothing in the toolchain today guarantees a
new Pod inherits it — in the first Pod these instructions were hand-present in the repo,
not inherited. So until the channel below is chosen, "applies to every future Pod" is
asserted in this spec but not yet enforced by construction.

**Decision that gates the fix — still open: where new Pods are initialized from.**
- *(a) Scaffolded from `pod-base.md` via the pod-base skill* → the skill's inflation step
  must emit the goal-first + gate instructions into every new Pod's `.claude/` (the same
  "§R repo machinery" slot already proposed for the events hook).
- *(b) Forked from a base / template Pod repo* → the base repo's `.claude/` carries the
  instructions and every fork inherits them by construction. Closest to a true Lógos base
  layer; least drift.

## Placement (not yet ratified)

Operative home is `pod-spec.md` (what the agent does); a charter-level echo could sit with
the gated-process postulates (P6/P8). Pedro to decide: `pod-spec.md`, the postulates, or both.

## Folded-in nuance

The "records vs. builds" scope clause (feedback point 2) is folded into
`rule.gated-phase-transition` because the gate is meaningless without it. Split it into its
own `rule.no-premature-deliverables` if you prefer it stand alone.
