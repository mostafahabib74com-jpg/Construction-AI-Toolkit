# Workflow packages

Every workflow directory contains:

1. `workflow.yaml` — objective, prerequisites, inputs, deliverables, reviewers, tools, gates, blockers, and authority.
2. `input.schema.json` — common tender envelope plus required workflow inputs.
3. `output.schema.json` — common controlled output plus permitted deliverables.
4. `safety.md` — source, revision, artifact, commercial, submission, and review controls.
5. `CHANGELOG.md` — contract-version history.

Workflow outputs are immutable versioned artifacts. Addenda, client answers, or new upstream artifact versions trigger impact review and downstream reapproval. These files specify orchestration contracts; they do not implement parsing, rendering, calculation, packaging, or portal operations.
