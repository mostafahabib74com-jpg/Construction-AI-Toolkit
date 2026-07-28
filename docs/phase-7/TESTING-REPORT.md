# Phase 7 testing report

## Status

The repository currently contains specification artifacts rather than an executable platform. Static audit checks could be completed, but workflow, schema, document-generation, and end-to-end tests cannot run until the required runtime and test harness exist.

## Checks performed

| Check | Result | Evidence |
|---|---|---|
| Tracked-file inventory | PASS | 513 tracked files were enumerated. |
| Exact duplicate-file scan | PASS | No tracked files share the same SHA-256 digest. |
| JSON syntax | PASS | All 102 tracked JSON files parsed successfully. |
| JSON Schema identifiers | PASS | 96 schema identifiers were found and all are unique. |
| Workflow-package completeness | PASS | All 44 workflow packages contain a contract, input schema, output schema, safety file, changelog, and specialist prompt. |
| Markdown links | PASS | Checked repository-relative Markdown links resolve; the root README links resolve. |
| JSON references | PASS | Local references resolve to the expected common or workflow schema, or to an internal fragment. |
| Placeholder scan | WARN | Development-status text remains in the root and legacy tendering documentation; tools are explicitly unimplemented. |
| Workflow identifiers | FAIL | `rfi-generation`, `technical-proposal`, and `commercial-proposal` collide across agents. |
| Dependency/build discovery | FAIL | No package manifest, lock file, build definition, or reproducible environment is present. |
| Executable test discovery | FAIL | No automated test files or CI workflow are present. |
| YAML semantic validation | NOT RUN | The repository declares no YAML parser or validation environment. |
| JSON Schema instance validation | NOT RUN | No JSON Schema validation dependency or executable test fixtures are present. |
| Estimation workflow execution | NOT RUN | No workflow runner or deterministic estimation services exist. |
| Planning workflow execution | NOT RUN | No workflow runner or Primavera adapter exists. |
| Tender workflow execution | NOT RUN | No workflow runner or document assembler exists. |
| Agent-to-agent handoff | NOT RUN | No shared contracts, adapters, or handoff engine exist. |
| Excel generation | NOT RUN | No workbook generator or formula-validation service exists. |
| Error and missing-data handling | NOT RUN | The policy exists in prompts, not executable guards. |
| End-to-end demonstration | NOT RUN | No demonstration project or consolidated-result generator exists. |
| Git object integrity | PASS WITH INFO | `git fsck` succeeded; local dangling blobs are unreachable objects and do not affect tracked content. |
| Patch hygiene | PASS | `git diff --check` reported no whitespace errors before this report set was finalized. |

## Existing evaluation material

The agent specifications declare 39 evaluation scenarios:

- Estimation Agent: 10.
- Planning & Primavera P6 Agent: 12.
- Tender Manager Agent: 17.

These declarations are useful acceptance-test designs, but none currently has executable input fixtures, expected output fixtures, assertions, or a runner. Each should become a parameterized test case rather than being replaced.

## Required automated test matrix

### Estimation workflow

- Tender-document intake preserves document identity, revision, page, and evidence references.
- Scope extraction separates stated scope, inferred scope, exclusions, and unknowns.
- Missing quantities remain unknown and generate an RFI or assumption request.
- Missing rates remain unpriced and do not become zero-cost or invented prices.
- BOQ arithmetic, unit consistency, rate build-up, markups, contingencies, and totals reconcile.
- Quote comparison normalizes scope and commercial terms without hiding exclusions.
- Final estimate release is blocked when mandatory fields or approvals are absent.

### Planning workflow

- WBS identifiers are unique and preserve parent-child integrity.
- Activities have valid calendars, durations, milestones, and WBS assignments.
- Relationships reference valid activities and do not create circular logic.
- Open ends, negative lags, excessive lags, constraints, and calendar conflicts are reported.
- Resource and cost loading reconcile with activity and estimate data.
- Progress updates preserve data dates and actual/remaining boundaries.
- Delay, recovery, and time-impact outputs state their method, evidence, and assumptions.

### Tender workflow

- Tender folders and document registers preserve all source documents and revisions.
- Compliance-matrix rows link to evidence and an accountable owner.
- Clarifications, RFIs, assumptions, and exclusions remain distinct artifact types.
- Technical and commercial proposal sections reconcile with the estimate and schedule.
- Mandatory submission forms and fields block package release when incomplete.
- Package manifest checks filenames, revisions, hashes, and submission readiness.

### Agent handoff

- Tender scope and clarification outputs map to Estimation inputs without losing evidence.
- Estimation BOQ and cost outputs map to Planning cost-loading inputs with explicit units, currency, and base date.
- Planning dates, resources, and cash flow return to Tender without changing source ownership.
- Conflicting updates generate a review task rather than silently overwriting an artifact.
- Every handoff records producer, consumer, schema version, artifact version, and provenance.

### Excel generation

- Workbook sheets, headers, number formats, formulas, named ranges, and protection are deterministic.
- Formula totals match independently calculated expected values.
- Currency, units, and rate basis are visible and consistent.
- Missing data is visibly flagged and cannot be mistaken for a confirmed zero.
- Workbook reopen/round-trip tests succeed and no formulas contain broken references.

### Error and missing-data handling

- Unsupported request, ambiguous workflow, schema error, missing document, missing quantity, missing rate, and conflicting revision produce typed errors.
- Recoverable errors include remediation guidance and preserve partial results.
- Non-recoverable validation errors prevent final-release status.
- No stack trace, credential, or local path leaks into user-facing output.

### End-to-end demonstration

- Intake through final consolidated output runs from versioned sample data.
- All artifacts are reproducible, traceable, schema-valid, and listed in a manifest.
- Deliberately missing data creates RFIs and release blockers rather than invented facts.
- The final report reconciles scope, BOQ, cost, WBS, schedule, clarifications, and checklist status.

## Proposed acceptance thresholds

- 100% schema validation for released artifacts.
- 100% traceability for quantities, rates, requirements, dates, and controlled assumptions.
- Zero silent workflow-ID collisions.
- Zero invented quantity, price, or contract requirement in negative fixtures.
- Zero broken spreadsheet formulas in generated workbooks.
- Zero invalid schedule references or circular logic in release candidates.
- 100% completion of mandatory document fields before `release-ready` status.
- All P0 and P1 defects closed before a Phase 7 release candidate.

## Limitations

This report does not claim functional correctness. It establishes the verified static baseline and the tests needed to prove correctness once the approved runtime, shared contracts, services, and fixtures are implemented.
