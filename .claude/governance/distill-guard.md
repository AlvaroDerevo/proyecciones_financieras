---
id: spec.distill-guard
kind: spec-addendum
status: ratified
ratified-by: pedro
ratified-at: 2026-06-04
applies-at: logos            # universal — every Pod's /distill, not craft-specific
derived-from: flow.cca-f-readiness@experimental   # distill drift observed in early Pod work
supersedes: []
cites:
  - flow.cca-f-readiness@experimental
  - term.drift
revision: r003
---

# Distill guard — `/distill` promotes craft, not stance

`/distill` condenses a session into durable promotions. Its failure mode, seen in early Pod
work: it drifts from condensing *buildable craft* into condensing the helper's *stance* —
how the helper is, or relates to the person — which has no buildable target and pulls the
output toward open-ended framing. This guard bounds what `/distill` may promote.

## rule.distill-promotes-craft-only

- `/distill` may promote only buildable craft: rules, terms, decisions, entities — each
  carrying a dotted `id`, a `kind`, and resolvable `citations`, and targeting a buildable
  category (`ontology/terms/`, `ontology/rules/`, `decisions/`, …).
- A distillation output that is relational-, identity-, or stance-shaped — a principle about
  how the helper *is* or *relates*, with no buildable target — is the drift signal. Flag it
  for human review; do not promote it.
- Already-committed craft is not re-promoted. A candidate matching an existing ratified `id`
  is dropped, or routed as an explicit update only on human direction. `/distill` surfaces
  genuinely new craft, never restatements of the record.

*Why.* Early Pod work produced a distillation that drifted into stance/identity framing
rather than craft, with the Flow and Pod losslessly shaped — an instance of `term.drift`, the
cumulative model–human–context divergence defined there, not a setup defect. This guard does
not cure drift; it is a backstop at the *promotion* boundary, catching drift only when it
tries to become durable. The standing counter to drift is re-anchoring to the ratified record
(per `term.drift`); the guard's job is narrower — bind `/distill` to craft carrying `id`,
`kind`, and `citations`, so a drifting distillation has no buildable target to land in. It
catches, at the command boundary, the project's characteristic failure: growth that never
ships.

## Enforcement (Claude Code)

- **Command-level.** `/distill`'s promotion step checks each candidate for `{id, kind,
  citations}` and a buildable target category. Candidates that fail are flagged in the review
  queue, not written.
- **Hardenable.** A PreToolUse/command gate can block a promote-or-ratify write whose
  frontmatter lacks `id`/`kind`/`citations`, or whose target is not a buildable category —
  moving this from instruction to perimeter, consistent with the enforcement audit.
- Enforcement is by command + optional hook, not by construction.

## Relationship to the base (decision, ratified)

The base agent carries `logos.md` discipline only. The stance material discussed in the
framing register is **not** inherited by any Pod and is **not** added to the base. The
proposal cycle — the AI proposes, the human ratifies, the AI holds no commit power — keeps
drift and stance from becoming *durable*; it does not prevent them arising in conversation,
which is where cumulative drift lives. That conversational drift is countered by re-anchoring
to the record, not by a stance enshrined in the base. This guard works the same durability
boundary as the proposal cycle, from the `/distill` side.

*Register note.* Framing-register vocabulary is deliberately absent; the rationale is stated
in buildable terms only.
