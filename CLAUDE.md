# Proyecciones financieras de negocio — FlowPod Pod (empty, experimental)

A FlowPod workspace for business financial projections (proyecciones financieras de negocio). This Pod is **empty**: no goal is baked here. The agent's first
action is to confirm the goal with the expert (goal-first), then run Understand -> Plan -> Build ->
Verify with gated transitions, producing deliverables only in Build (previews before then).

The expert converses in plain language; the agent invokes the Pod operations itself -- orient, goal,
flowcheck, propose/ratify a rule or term, promote, distill, record an outcome -- and reports them.
The expert never runs commands.

Governance (kernel base 1.1.0) is in `.claude/governance/`: `phase-protocol.md` (goal-first +
gated transitions), `distill-guard.md`, `term.drift`, `operations-catalog.md`; carried by the
`logos` agent and the hooks in `.claude/`.

`id`/`kind` derive from path. Never write `flow/ontology`, `flow/techne`, or `pod/ontology`
directly. Run flowcheck before promoting; distill promotes craft only.
