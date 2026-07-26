# Technical Proposal safety and review rules

## Required controls

- Apply the Tender Manager Agent system prompt and every declared shared prompt.
- Use controlled sources, the exact tender version, source cutoff, and latest addendum.
- Preserve original evidence and approved upstream artifacts; create new versions for drafts and revisions.
- Do not invent requirements, responses, credentials, resources, prices, dates, signatures, approvals, submissions, or receipts.
- Use validated deterministic tools for calculations, reconciliations, rendering, file checks, and package checks.
- Keep assumptions, exclusions, qualifications, deviations, and client responses distinct.
- Do not approve, commit, issue, sign, authorize submission, or upload.

## Workflow-specific blockers

- `mandatory_section_without_approved_content`
- `unverified_company_claim`
- `page_or_format_noncompliance`
- `technical_commercial_conflict`

## Mandatory reviewers

- Tender Manager
- Proposal Manager
- Technical Manager
- Responsible Discipline Leads

A blocker may be cleared only by new controlled evidence or an authorized, recorded decision.
