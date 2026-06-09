---
id: term.drift
kind: term
status: ratified
ratified-by: pedro
ratified-at: 2026-06-04
applies-at: logos            # framework-level term, not a Pod-domain term
supersedes: []
cites:
  - flow.cca-f-readiness@experimental   # the run where drift was first observed
linked-rules:
  - rule.distill-promotes-craft-only
revision: r001
---

# term.drift

**Drift** — the gradual, cumulative divergence of a Pod's working behavior and output from
its ratified record, produced by the interaction of model, human, and context over time.

Drift is emergent and multi-factor: no single component — model capability, human input, or
accumulated context — causes it; their interaction accrues it. It appears even when the Flow
and Pod are losslessly shaped and the model is capable, so it is a standing property of
sustained human–AI work, not a defect of a particular setup.

Its increments are minimal — small enough that no single step looks wrong. Drift is therefore
invisible step-to-step and detectable only against a fixed anchor: the ratified record
(ontology, decisions, specs). Comparing the present state against that anchor reveals
accumulated divergence that turn-to-turn comparison misses.

Drift is countered, not cured, by two means: **re-anchoring** each session to the durable
files (bounded participation + the boot-sequence reads), which washes out accumulated
conversational drift rather than letting it compound; and **promotion-boundary guards** (e.g.
`rule.distill-promotes-craft-only`) that keep drifted, non-craft output from crossing into the
record.

Drift *becoming durable* is a failure. Drift *in conversation* is expected and is managed by
re-anchoring, not prevented.
