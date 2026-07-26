# Recommended corrections

## Recommendation summary

Preserve the three agent specification trees and integrate them through an additive shared-contract and orchestration layer. Do not mass-rename files or replace agent schemas in the first integration step. Introduce adapters, validate compatibility, and migrate incrementally.

This is a proposed major architecture and requires approval before implementation.

## Proposed additive structure

```text
packages/
  contracts/
    schemas/
      core/
        artifact.schema.json
        consolidated-result.schema.json
        error.schema.json
        evidence.schema.json
        money.schema.json
        project.schema.json
        quantity.schema.json
        rate.schema.json
        review.schema.json
        source-document.schema.json
        unit.schema.json
        workflow-request.schema.json
        workflow-result.schema.json
      domain/
        activity.schema.json
        assumption.schema.json
        boq-item.schema.json
        calendar.schema.json
        deliverable.schema.json
        exclusion.schema.json
        relationship.schema.json
        resource-assignment.schema.json
        resource.schema.json
        rfi.schema.json
        risk.schema.json
        tender-clarification.schema.json
        wbs.schema.json
    adapters/
      estimation/
      planning/
      tender/
    conventions/
      currencies.md
      dates-and-time.md
      document-naming.md
      metadata.md
      prompt-format.md
      units.md
  orchestrator/
    pyproject.toml
    config/
      agent-registry.yaml
    pipelines/
      tender-to-bid.yaml
    src/construction_ai_orchestrator/
      artifacts.py
      consolidation.py
      errors.py
      graph.py
      registry.py
      router.py
      runner.py
      validation.py
tests/
  agents/
  contracts/
  e2e/
  error_handling/
  excel/
  handoffs/
  orchestrator/
examples/
  demo-project/
```

The exact file list for each implementation milestone should be confirmed immediately before work begins.

## Runtime decision requiring approval

Use Python 3.12 for the first orchestration runtime, with:

- `PyYAML` for the existing YAML specifications and pipeline definitions.
- `jsonschema` using JSON Schema Draft 2020-12.
- `pytest` for unit, contract, integration, and end-to-end tests.
- `openpyxl` for deterministic Excel workbook generation and verification.

A reproducible project manifest and lock policy must be committed. The runtime should be provider-neutral: language-model calls, document extraction, storage, Primavera, BIM, and office-document services should be ports/adapters rather than embedded in domain logic.

## Compatibility strategy

1. Freeze the current agent specifications as the Phase 7 input baseline.
2. Create versioned shared canonical schemas.
3. Map each existing agent schema to and from the canonical form through an explicit adapter.
4. Add conformance tests for lossless fields and documented lossy mappings.
5. Migrate agent contracts one workflow at a time only after the adapter tests pass.
6. Deprecate old fields with a stated window; do not silently remove them.

No tracked file currently requires deletion. Moves or renames should wait until compatibility and inbound-link checks exist.

## Workflow identity and routing

Keep existing workflow IDs inside their agent domains, but use a qualified runtime key:

```text
<agent-id>/<workflow-id>
```

Examples:

- `estimation-agent/rfi-generation`
- `tender-manager-agent/rfi-generation`
- `estimation-agent/commercial-proposal`
- `tender-manager-agent/commercial-proposal`

An unqualified colliding identifier must return an ambiguity error. The registry may support the alias `tender-proposal-agent` for architecture-document compatibility, while `tender-manager-agent` becomes the canonical implementation identifier.

## Responsibility boundary correction

- Estimation owns estimate development, commercial normalization, pricing risk, and an approved estimate release package.
- Planning owns WBS, activities, logic, calendars, resources, cost loading, schedule analysis, and schedule release artifacts.
- Tender Manager owns tender governance, compliance, proposal assembly, submission forms, package manifest, and final submission readiness.
- The central Orchestrator owns cross-agent routing, artifact lineage, status, validation sequencing, review gates, and consolidated result generation.

Rename or redefine the Estimation `final-bid-package` responsibility in a later reviewed migration so it cannot compete with Tender Manager's `submission-package` authority. Until then, the orchestrator should treat the Estimation output as an estimate-release input to Tender.

## Shared schema principles

- Every schema has `$schema`, stable `$id`, semantic version, owner, and change policy.
- Every artifact has project ID, artifact ID, type, version, status, producer, creation time, source lineage, and review state.
- Every derived claim can reference one or more evidence records.
- Monetary values require amount, ISO 4217 currency, valuation/base date, and pricing basis.
- Quantities require numeric value, controlled unit, measurement basis, and source or declared assumption.
- Dates use ISO 8601; deadlines use an offset and an IANA time zone where local business rules matter.
- Durations and lags use a canonical hour value plus the applicable calendar.
- Enumerations are governed centrally and extended explicitly.
- Unknown, not-applicable, zero, and not-yet-reviewed remain distinct states.

## Prompt standard

All specialist prompts should converge on this section order without erasing useful domain content:

1. Title and workflow identity.
2. Role.
3. Objective.
4. Required inputs.
5. Procedure.
6. Required outputs.
7. Quality gates.
8. Authority, assumptions, and escalation.

Prompt headers should declare agent ID, workflow ID, prompt version, compatible contract version, and output schema. Prompt tests should check that safety rules and mandatory outputs are present.

## Executable validation policy

### Quantity guard

A quantity may be confirmed only when it has an accepted source or measurement derivation. Otherwise the system must use an explicit unknown/allowance state, record the basis, and create an RFI or review item when material.

### Price guard

A price requires currency, base date, source type, source reference or approved rate basis, inclusions, exclusions, and confidence/status. Missing rates remain unpriced; zero is accepted only when explicitly justified.

### Contract guard

A contract requirement requires a cited source. Inferred obligations must be labeled as assumptions and cannot be presented as contract facts.

### Schedule guard

Schedule release requires valid WBS assignment, unique activity IDs, valid calendars, valid relationship endpoints, cycle detection, open-end checks, constraint review, and data-date consistency.

### Document-release guard

Each deliverable type has a mandatory-field profile. Missing mandatory fields, unresolved critical validation findings, or absent required approvals prevent `release-ready` status.

## Orchestrator result model

The central consolidated result should contain:

- request and selected pipeline;
- workflow runs and statuses;
- artifact manifest and lineage;
- validations, warnings, and release blockers;
- assumptions, exclusions, RFIs, clarifications, and risks;
- review/approval requirements;
- final deliverable references;
- reproducibility metadata and configuration versions.

## Capability truthfulness

Registry capabilities should use explicit maturity states:

- `declared`: specified in prompts/contracts only.
- `available`: executable service exists.
- `validated`: automated acceptance tests pass.

User-facing documentation must not imply that XLSX, DOCX, PDF, XER, XML, or packaged submissions are generated until the relevant capability is at least `available`, and release claims should require `validated`.

## Correction sequence

1. Shared conventions and canonical schemas.
2. Schema conformance tests and legacy adapters.
3. Orchestrator registry, router, artifact store, and dry-run pipeline.
4. Executable validation guards.
5. Deterministic Excel generation and workbook tests.
6. Workflow services and agent handoffs.
7. End-to-end demonstration, CI, and release documentation.

This sequence integrates useful existing work and confines major changes to reviewable milestones.
