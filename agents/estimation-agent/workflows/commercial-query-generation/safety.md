# Commercial Query Generation safety and review rules

## Required controls

- Apply the Estimation Agent system prompt and all shared prompts.
- Use only controlled project sources and approved knowledge profiles.
- Preserve source, revision, unit, currency, calculation, and approval provenance.
- Mark missing, conflicting, assumed, provisional, and low-confidence information explicitly.
- Use validated deterministic tools for every numerical calculation.
- Keep confidential tender and bidder information within authorized project scope.
- Do not approve, sign, issue externally, commit a price, or submit a bid.

## Workflow-specific blockers

- `missing_contract_basis`
- `missing_source_reference`
- `unapproved_legal_or_tax_position`

## Mandatory reviewers

- Estimation Manager
- Commercial Manager
- Contracts Manager

A blocked condition may be cleared only by new controlled evidence or an authorized, recorded decision.
