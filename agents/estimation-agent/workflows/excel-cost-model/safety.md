# Professional Excel Cost Model safety and review rules

## Required controls

- Apply the Estimation Agent system prompt and all shared prompts.
- Use only controlled project sources, approved upstream outputs, and approved knowledge profiles.
- Preserve source, revision, unit, currency, formula, tool, and approval provenance.
- Use validated deterministic tools for all numerical results and reconciliations.
- Keep assumptions, allowances, exclusions, qualifications, deviations, and risks explicit.
- Protect tender, estimate, margin, customer, supplier, and subcontractor confidentiality.
- Do not approve, sign, issue externally, commit a price, or submit a bid.

## Workflow-specific blockers

- `invalid_estimate_schema`
- `unapproved_commercial_adjustment`
- `formula_error`
- `reconciliation_failure`
- `visual_review_incomplete`

## Mandatory reviewers

- Estimation Manager
- Commercial Manager

A blocked condition may be cleared only by new controlled evidence or an authorized, recorded decision.
