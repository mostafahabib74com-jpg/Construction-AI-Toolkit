# High-priority milestone 1: accuracy foundation

## Objective

Prevent unsupported engineering data from being released as validated or final output, and provide explicit common-data mappings from the three existing agent models into canonical contracts.

No new agents, domain generators, or external integrations are included.

## Implemented safeguards

### Quantities and BOQ

- Confirmed quantities require a value, measurement basis, and source reference.
- Allowances require a value and a linked assumption.
- Unknown/not-applicable quantities cannot conceal a numeric value.
- Negative quantities are blocked.
- Nested BOQ quantities receive the same controls.
- Priced BOQ items require a rate reference and calculated total.

### Rates and pricing

- Negative rates are blocked.
- Zero rates require an explicit zero-cost justification.
- Quoted and historical rates require a source reference.
- Unverified rates cannot be released as validated pricing.
- Unpriced BOQ items cannot carry commercial totals.

### Contract requirements

- A stated contract fact requires controlled evidence.
- Assumed/inferred requirements require a linked assumption.
- Assumptions and inferences cannot be labelled as confirmed contract facts.

### Schedule logic

- WBS, activity, and calendar IDs are checked for duplicates.
- WBS parents, activity WBS assignments, calendar assignments, and relationship endpoints must exist.
- WBS and activity logic cycles are blocked.
- Milestones must have zero duration.
- Finish-before-start dates are blocked.
- Negative/excessive lag and open ends are reported for planner review.

### Deliverables and approvals

- Mandatory field names are checked against actual field values.
- Validated/released deliverables require a registered artifact reference.
- Approved/submitted deliverables require an approved review.
- Approved artifacts require an identified professional reviewer.
- Only approved artifacts appear in the consolidated `final_deliverables` list.

## Adapter coverage

The Estimation, Planning & P6, and Tender Manager adapters map:

- project metadata, with explicit time-zone/unit-system input when absent;
- source document identity, revision, status, dates, checksums, classification, extraction method, confidence, and lineage;
- review statuses without manufacturing approval;
- Estimation money and quantity common types;
- Planning schedule references;
- Tender project context and cross-agent artifact references.

Existing agent files and schemas remain unchanged. These adapters are a compatibility boundary, not a silent migration.

## Defect impact

- **INT-024:** release-time non-invention, schedule, and mandatory-field safeguards are implemented for canonical artifacts.
- **INT-015, INT-016, INT-017:** common source, review, artifact, project, units, currency, and date mappings are implemented; workflow-specific adapters remain future work.
- **INT-004:** final-deliverable approval is tightened, but Estimation-versus-Tender package ownership still requires a separate reviewed change.

## Remaining high-priority work

- Full workflow-specific adapters for every agent input/output contract.
- Estimate-release versus Tender submission-package ownership correction.
- Excel generator and formula verification.
- Primavera P6 XER/XML adapter and round-trip checks.
- Deterministic domain workflow handlers.
- Shared standards/knowledge governance.
- Conversion of all 39 evaluation declarations to executable fixtures.
- Full CI gates and the end-to-end demonstration project.

These items require the next approval and are not implemented here.
