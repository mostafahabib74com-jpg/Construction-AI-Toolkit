# Tender Package Ingestion safety and review rules

## Required controls

- Apply the Tender Manager Agent system prompt and every declared shared prompt.
- Use controlled sources, the exact tender version, source cutoff, and latest addendum.
- Preserve original evidence and approved upstream artifacts; create new versions for drafts and revisions.
- Do not invent requirements, responses, credentials, resources, prices, dates, signatures, approvals, submissions, or receipts.
- Use validated deterministic tools for calculations, reconciliations, rendering, file checks, and package checks.
- Keep assumptions, exclusions, qualifications, deviations, and client responses distinct.
- Do not approve, commit, issue, sign, authorize submission, or upload.

## Workflow-specific blockers

- `missing_invitation_or_document_index`
- `unconfirmed_submission_deadline_or_time_zone`
- `material_unreadable_source`
- `incomplete_addendum_reconciliation`

## Mandatory reviewers

- Tender Manager
- Document Control Manager

A blocker may be cleared only by new controlled evidence or an authorized, recorded decision.
