# Submission package specification

## Release candidate

The release candidate is an immutable set of approved files plus an authoritative manifest. Any content or metadata change creates a new candidate and reopens affected checks.

## Required controls

- Freeze tender version, source cutoff, latest addendum, deadline, time zone, package version, and authorized submitter.
- Map every mandatory requirement, form, and portal field to the exact file/version and response location.
- Separate technical and commercial envelopes exactly as instructed.
- Verify approvals and signatures against the authority matrix.
- Reconcile scope, price, quantities, dates, milestones, resources, assumptions, exclusions, qualifications, deviations, and forms.
- Open final files and validate format, pagination, bookmarks, links, fonts, images, searchable text, metadata, redaction, formulas/values, file size, and total package size.
- Run malware scanning, encryption/password validation, and cryptographic checksum recording.
- Plan upload start with contingency before the deadline; record escalation contacts.
- Do not mark `submitted` without controlled portal or client receipt evidence.

## Readiness states

- `not_ready`: one or more mandatory blockers remain.
- `conditionally_ready`: only explicitly authorized waivers remain; release still requires executive authority.
- `ready_for_authorized_release`: all preflight gates passed, exact versions approved, checksum frozen, and an authorized submitter is assigned.
- `submitted`: external receipt evidence is recorded after authorized submission.

The Tender Manager Agent may recommend a readiness state but cannot authorize or perform submission.
