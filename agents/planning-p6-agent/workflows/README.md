# Workflow packages

Each workflow directory contains five controlled artifacts:

1. `workflow.yaml` — objective, prerequisites, deliverables, reviewers, tools, gates, blockers, and authority.
2. `input.schema.json` — versioned input envelope plus workflow-specific required inputs.
3. `output.schema.json` — versioned output envelope plus permitted deliverable types.
4. `safety.md` — immutability, evidence, deterministic calculation, and professional-review controls.
5. `CHANGELOG.md` — workflow-contract history.

Workflows exchange references to immutable schedules and artifacts. A downstream workflow must not silently consume an unapproved or incompatible upstream draft.

The package specifies orchestration contracts only. It does not implement CPM computation, XER/XML parsing or writing, resource leveling, cost calculation, or P6 publication.
