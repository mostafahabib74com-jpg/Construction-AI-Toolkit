# Scope Extraction safety and review rules

## Required controls

- Apply the Estimation Agent system prompt and all shared prompts.
- Use only controlled project sources and approved knowledge profiles.
- Preserve source, revision, unit, currency, calculation, and approval provenance.
- Mark missing, conflicting, assumed, provisional, and low-confidence information explicitly.
- Use validated deterministic tools for every numerical calculation.
- Keep confidential tender and bidder information within authorized project scope.
- Do not approve, sign, issue externally, commit a price, or submit a bid.

## Workflow-specific blockers

- `unapproved_rfp_analysis`
- `undefined_scope_boundary`
- `unresolved_critical_conflict`

## Mandatory reviewers

- Estimation Manager
- Technical Manager

A blocked condition may be cleared only by new controlled evidence or an authorized, recorded decision.
