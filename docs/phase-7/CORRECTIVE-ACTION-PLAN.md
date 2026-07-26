# Phase 7 corrective action plan

## Current authorized scope: critical issues only

The critical milestone establishes a safe, testable integration control plane around the existing Estimation, Planning & Primavera P6, and Tender Manager specifications. Existing agent content remains authoritative and unchanged.

## Critical corrective actions

### C1 - Shared contracts and validation

**Addresses:** INT-002, INT-006, INT-009, INT-013, and the contract portion of INT-014.

**Actions:**

1. Add canonical JSON Schemas for projects, evidence, artifacts, workflow requests/results, consolidated results, errors, review, units, money, quantities, BOQ items, WBS, activities, resources, rates, risks, RFIs, tender clarifications, assumptions, exclusions, and deliverables.
2. Add a schema catalog that resolves local schema identifiers without network access.
3. Validate schemas themselves and validate runtime instances using JSON Schema Draft 2020-12.
4. Add a Python 3.12 manifest and exact direct-dependency lock.

**Acceptance criteria:**

- Every shared schema loads and passes meta-schema validation.
- Valid fixtures pass and malformed fixtures return stable path-based issues.
- Validation never fetches schemas over the network.

### C2 - Registry and unambiguous routing

**Addresses:** INT-001 and INT-003.

**Actions:**

1. Load the three existing agent manifests and all 44 workflow contracts.
2. Register each workflow using `<agent-id>/<workflow-id>`.
3. Reject an unqualified colliding workflow ID with a typed ambiguity error.
4. Support exact agent/workflow requests and deterministic text-based routing.
5. Expose routing through a small command-line interface.

**Acceptance criteria:**

- All 44 workflows are discoverable.
- Qualified routing is deterministic.
- The three known collisions cannot route silently.
- Unknown and ambiguous requests return safe, actionable errors.

### C3 - Artifact handoff, execution boundary, and consolidation

**Addresses:** INT-013, INT-014, and INT-023.

**Actions:**

1. Add immutable artifact records with producer, schema, version, lineage, and review state.
2. Define a handler interface so domain services can be added later without changing orchestration logic.
3. Pass artifact references between sequential workflow runs.
4. Return a consolidated result with run status, artifacts, issues, blockers, and final deliverable references.
5. Return an explicit `handler_not_available` blocker for specification-only workflows rather than fabricating output.

**Acceptance criteria:**

- A test handler can complete a workflow and register outputs.
- A second workflow receives the first workflow's artifact references.
- Duplicate artifact identity/version conflicts are rejected.
- Missing handlers produce a valid blocked result without a stack trace or invented deliverable.

### C4 - Critical regression tests and reporting

**Addresses:** proof of closure for all critical items; this is not the full high-priority test program in INT-007/INT-008.

**Actions:**

1. Add contract, registry, routing, orchestration, handoff, and failure tests.
2. Run the original static checks plus the new automated test suite.
3. Record commands, versions, results, limitations, and unresolved high-priority work.

**Acceptance criteria:**

- All critical tests pass.
- Static repository checks remain clean.
- No new agent, move, rename, or deletion is introduced.

## Deferred high-priority sequence

No deferred item starts without approval after the critical test report.

1. Accuracy policy validators and negative test fixtures.
2. Legacy-agent adapters and governed vocabularies.
3. Estimate/submission ownership correction.
4. Deterministic Excel generation.
5. Primavera P6 adapter and schedule integrity checks.
6. Executable agent workflow handlers and the 39 evaluation cases.
7. Full CI, demonstration project, and release gates.

## Rollback and compatibility

- All implementation is additive.
- Existing agent folders, contracts, prompts, examples, and documentation are preserved.
- No workflow maturity status changes in this milestone.
- The orchestrator exposes absence of a handler as a blocker; it does not simulate domain completion.
