# Shared contracts

This package contains provider-neutral, versioned JSON Schemas used by the platform control plane. Agent-specific schemas remain unchanged and require explicit adapters before their domain data is treated as canonical.

## Rules

- JSON Schema Draft 2020-12 is authoritative.
- Schema identifiers are stable HTTPS identifiers; validation resolves them from the local catalog and never requires network access.
- Runtime workflow identity is `<agent-id>/<workflow-id>`.
- Unknown, zero, not applicable, and unreviewed are distinct states.
- A schema-valid artifact is not automatically technically correct or approved.

The initial `v1` contracts establish interoperability. Accuracy policy validators and agent adapters are separate high-priority work.
