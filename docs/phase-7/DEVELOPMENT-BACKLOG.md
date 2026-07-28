# Phase 7 development backlog

## Priority model

- **P0**: prevents safe integration or permits materially unreliable output.
- **P1**: required for a credible Phase 7 release candidate.
- **P2**: important hardening or usability work that can follow the first integrated demonstration.

Effort is an engineering estimate in focused person-days and should be recalibrated after each milestone.

## Milestone plan

### 7.1 - Integration audit baseline

**Status:** Complete in this branch, pending review.

**Objective:** Establish a verified inventory, system map, defect baseline, missing-component list, test baseline, and correction proposal without changing runtime behavior.

**Deliverables:** The nine reports in `docs/phase-7/`.

**Files to create:** Documentation files listed in `CHANGE-INVENTORY.md`.

**Files to modify:** None.

**Dependencies:** Existing repository only.

**Estimated effort:** 2-3 days.

### 7.2 - Shared contracts and conventions

**Status:** Awaiting architectural approval.

**Objective:** Define the canonical project, commercial, schedule, tender, evidence, artifact, review, error, and result models used across all agents.

**Deliverables:** Versioned JSON Schemas, controlled vocabularies, metadata conventions, prompt convention, legacy-schema mapping documents, fixtures, and schema tests.

**Files to create:** `packages/contracts/**` and `tests/contracts/**` as scoped at milestone start.

**Files to modify:** Agent schema references only where an approved compatibility mapping requires it; prefer adapters first.

**Dependencies:** Approval of the additive Python architecture, schema version policy, units policy, and workflow identity convention.

**Estimated effort:** 4-6 days.

### 7.3 - Orchestrator foundation and dry-run pipeline

**Status:** Pending 7.2.

**Objective:** Route a normalized request to qualified workflows, validate inputs/outputs, preserve artifact lineage, and produce a consolidated dry-run result without external model or office integrations.

**Deliverables:** Python project manifest and lock policy, agent/workflow registry, router, pipeline graph, artifact registry, typed errors, dry-run runner, tender-to-bid pipeline definition, and unit tests.

**Files to create:** `packages/orchestrator/**` and `tests/orchestrator/**`.

**Files to modify:** Root developer documentation and, if approved, agent catalog references.

**Dependencies:** 7.2 schemas and conventions.

**Estimated effort:** 5-8 days.

### 7.4 - Agent adapters and executable validation

**Status:** Pending 7.3.

**Objective:** Connect Estimation, Planning, and Tender specifications to canonical contracts and enforce non-invention, schedule-logic, provenance, and document-release rules.

**Deliverables:** Three agent adapters, workflow contract loader, quantity/rate/contract/schedule/document validators, handoff tests, missing-data tests, and correction of ambiguous workflow routing.

**Files to create:** `packages/contracts/adapters/**`, validator modules, and `tests/agents/**`, `tests/handoffs/**`, `tests/error_handling/**`.

**Files to modify:** Only the agent contracts/prompts required to close documented incompatibilities; every change must preserve domain content and include a changelog entry.

**Dependencies:** 7.2 and 7.3.

**Estimated effort:** 6-10 days.

### 7.5 - Deterministic cost-model generation

**Status:** Pending 7.4.

**Objective:** Generate and validate professional Excel cost models from canonical BOQ, resource, rate, risk, and project data.

**Deliverables:** Workbook generator, template/version rules, calculation engine, formula and formatting checks, sample workbooks, and regression tests.

**Files to create:** A scoped document-generation service, workbook templates, and `tests/excel/**`.

**Files to modify:** Estimation output declarations and capability registry after the generator passes acceptance tests.

**Dependencies:** Canonical schemas, validation services, approved Excel library, and rate/quantity test fixtures.

**Estimated effort:** 4-7 days.

### 7.6 - Automated quality gates and CI

**Status:** Pending executable runtime.

**Objective:** Convert the existing 39 evaluation declarations and the Phase 7 test matrix into reproducible automated quality gates.

**Deliverables:** Unit, contract, integration, negative, snapshot, and end-to-end tests; coverage reporting; lint/schema checks; CI workflow; release-blocking P0/P1 policy.

**Files to create:** Test fixtures, test modules, CI configuration, and quality configuration.

**Files to modify:** Evaluation documentation to link each declared scenario to an executable test ID.

**Dependencies:** 7.2-7.5.

**Estimated effort:** 5-8 days.

### 7.7 - End-to-end demonstration project

**Status:** Pending integrated workflow.

**Objective:** Demonstrate tender intake, scope extraction, RFI generation, BOQ, preliminary estimate, WBS/schedule, submission checklist, and final consolidated output using safe sample data.

**Deliverables:** Versioned sample tender data, expected artifacts, executable pipeline configuration, generated outputs, manifest, validation report, and reproducibility instructions.

**Files to create:** `examples/demo-project/**` and `tests/e2e/**`.

**Files to modify:** User documentation to link the validated demonstration.

**Dependencies:** 7.2-7.6 and approved sample-data licensing/provenance.

**Estimated effort:** 4-6 days.

### 7.8 - Hardening, documentation, and release readiness

**Status:** Pending demonstration.

**Objective:** Close release-blocking defects, reconcile documentation with actual capabilities, and prepare an auditable Phase 7 release candidate.

**Deliverables:** Security and failure-mode review, performance baseline, migration/deprecation notes, operator guide, updated architecture and roadmap, defect closure evidence, and release checklist.

**Files to create:** Operator/release documents and any approved migration notes.

**Files to modify:** Root README, roadmap, architecture, agent status statements, and capability registry.

**Dependencies:** Successful 7.7 demonstration and all P0/P1 tests passing.

**Estimated effort:** 3-5 days.

## Prioritized work items

| ID | Priority | Work item | Target milestone |
|---|---|---|---|
| BL-001 | P0 | Approve canonical architecture, runtime, and ownership boundaries | 7.2 |
| BL-002 | P0 | Implement shared project, artifact, evidence, workflow, error, and result schemas | 7.2 |
| BL-003 | P0 | Implement requested BOQ, activity, WBS, resource, rate, risk, RFI, clarification, assumption, exclusion, and deliverable schemas | 7.2 |
| BL-004 | P0 | Create conformance fixtures and schema validation tests | 7.2 |
| BL-005 | P0 | Build registry and qualified workflow routing | 7.3 |
| BL-006 | P0 | Build artifact lineage and consolidated-result handling | 7.3 |
| BL-007 | P0 | Enforce quantity, price, contract, schedule, and mandatory-field guards | 7.4 |
| BL-008 | P0 | Resolve final bid/submission responsibility overlap | 7.4 |
| BL-009 | P1 | Create compatibility adapters for all three implemented agents | 7.4 |
| BL-010 | P1 | Normalize prompt metadata and section format incrementally | 7.4 |
| BL-011 | P1 | Implement and verify Excel generation | 7.5 |
| BL-012 | P1 | Convert 39 evaluation declarations into executable fixtures | 7.6 |
| BL-013 | P1 | Add CI and release-blocking quality gates | 7.6 |
| BL-014 | P1 | Build and validate the end-to-end demonstration | 7.7 |
| BL-015 | P1 | Update README, roadmap, and capability claims to match reality | 7.8 |
| BL-016 | P2 | Implement DOCX/PDF packaging and rendering verification | Later Phase 7/8 |
| BL-017 | P2 | Implement Primavera P6 XER/XML integration | Later Phase 7/8 |
| BL-018 | P2 | Implement document extraction/OCR and evidence indexing | Later Phase 7/8 |
| BL-019 | P2 | Add durable artifact storage, access control, and audit logging | Later Phase 7/8 |
| BL-020 | P2 | Implement the remaining seven platform agents | Future phases |

## Release gate

Phase 7 is not complete when specifications alone exist. A release candidate requires all P0/P1 items applicable to milestones 7.2-7.8, executable tests, an end-to-end demonstration, and truthful capability documentation.
