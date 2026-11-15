# Phase 7 integration audit

## 1. Executive conclusion

The repository contains three strong domain specifications with extensive prompts, schemas, workflow contracts, templates, safety controls, and review guidance. It is not yet an integrated executable platform.

The Estimation Agent, Planning & Primavera P6 Agent, and Tender Manager Agent are internally coherent at specification level, but there is no central orchestrator, shared canonical data model, executable validator, deterministic calculation service, document/Excel/P6 renderer, automated test runner, or end-to-end demonstration. All 44 workflows remain marked `specification`.

The recommended Phase 7 strategy is additive: preserve the three agents and legacy prompts, introduce shared contracts and a namespaced registry, add a thin central orchestrator and validators, then implement tests and one synthetic end-to-end pipeline. Mass renaming or deletion is not required.

## 2. Audit scope and evidence

Audited revision: `d985df3 feat: add Tender Manager Agent foundation`.

Repository inventory:

| Measure | Result |
|---|---:|
| Tracked files | 513 |
| Estimation Agent files | 122 |
| Planning & P6 Agent files | 153 |
| Tender Manager Agent files | 162 |
| Workflow contracts | 44 |
| Workflow input schemas | 44 |
| Workflow output schemas | 44 |
| Workflow safety files | 44 |
| Workflow changelogs | 44 |
| Specialist workflow prompts | 44 |
| JSON files parsed | 102 |
| Unique JSON Schema IDs | 96 |
| Synthetic example JSON files | 6 |
| Evaluation case declarations | 39 |
| Reviewed expected evaluation artifacts | 0 |

The audit read all tracked files through inventory and content hashing, inspected agent manifests and representative prompts/schemas, scanned all workflow IDs and JSON Schema IDs, searched references and placeholder markers, and ran repository integrity and whitespace checks.

## 3. What is complete and useful

### 3.1 Common agent structure

All three agents contain the intended top-level areas: documentation, evaluations, examples, knowledge, prompts, schemas, templates, tools, and workflows. Every workflow directory has the expected five-file contract: `workflow.yaml`, `input.schema.json`, `output.schema.json`, `safety.md`, and `CHANGELOG.md`.

### 3.2 Safety and professional authority

The agents consistently prohibit autonomous approval, external issue, price commitment, schedule/source overwrite, and tender submission. They require source traceability, explicit assumptions/gaps, deterministic calculations where applicable, and named professional reviewers.

### 3.3 Domain coverage

- Estimation covers RFP analysis, scope/gaps, RFIs and queries, design basis, BOQ/CBS, cost model specification, quotation comparison, risk, proposal drafts, and bid-package review.
- Planning covers WBS, activities, calendars, logic, baseline, resources, costs, cash flow, procurement/design schedules, progress, delay, recovery, and TIA.
- Tender covers package/revision control, folder organization, compliance, clarifications/RFIs, assumptions/exclusions, methodology, organization, equipment, manpower, schedule coordination, proposals, and submission preflight.

### 3.4 Reference and repository integrity

- No byte-for-byte duplicate tracked files were found.
- All JSON files parsed successfully.
- No duplicate JSON Schema `$id` values were found.
- Existing Markdown links found by the audit resolve to tracked targets.
- JSON references use the expected local common/workflow-schema targets.
- Git object integrity completed without fatal errors; unreachable local blobs were reported but do not affect tracked content.

## 4. Duplicate and conflicting content

### 4.1 Global workflow identity collisions

Three workflow IDs exist in both Estimation and Tender:

- `rfi-generation`
- `technical-proposal`
- `commercial-proposal`

The content is not identical, but an orchestrator cannot safely route an unqualified workflow ID. Workflow identity must be the composite `agent_id/workflow_id`. Friendly aliases may exist only when the registry resolves them unambiguously.

### 4.2 Overlapping bid-package ownership

Estimation `final-bid-package` and Tender `submission-package` both claim complete bid compliance, technical/commercial consistency, manifests, packaging, approvals, and readiness. This is a responsibility conflict.

Recommended ownership:

- Estimation owns an `estimate-release-package`: approved price, BOQ/CBS, cost model, pricing basis, risk, queries, assumptions/exclusions, and reconciliation.
- Tender owns final proposal assembly, forms, signatures, envelopes, file preflight, submission manifest, and readiness.

Existing files should be preserved initially and clarified through registry metadata and documentation before any optional rename.

### 4.3 Semantic schema duplication

Each agent defines its own `common.schema.json`. Similar concepts differ in name and rules:

- Estimation uses `documentReference`; Planning and Tender use `sourceReference`.
- Source dates are `date`, absent, or `issue_date`.
- Tender requires `controlled_status`; the other agents do not.
- Register items have different required fields, status enums, date precision, and basis treatment.
- Finding basis enums are domain-specific and not interoperable.
- Artifact references exist only in the Tender common schema.
- Review objects differ because only Tender includes `authorization_reference`.

These are not exact duplicate files, but they prevent reliable cross-agent exchange without mapping.

### 4.4 Legacy prompt overlap

`AI-Prompts/` intentionally overlaps with agent workflows. The agent migration guides preserve this content, so it is not an immediate deletion candidate. Legacy files use uppercase, numbered, and special-character paths while agent modules use lowercase kebab-case. The two naming regimes should remain separated and explicitly labeled `legacy` versus `platform`.

## 5. Conflicting instructions and naming

| Area | Current inconsistency | Risk |
|---|---|---|
| Tender agent identity | Architecture uses `Tender & Proposal Agent` and `tender-proposal-agent`; implementation uses `Tender Manager Agent` and `tender-manager-agent` | Registry, documentation, and link ambiguity |
| Proposal ownership | Estimation and Tender both produce technical/commercial proposals | Conflicting versions and reviewer routes |
| Final package ownership | Estimation and Tender both perform final bid packaging/readiness | Duplicate gates and unclear authority |
| Workflow identity | Three unqualified IDs collide | Incorrect routing |
| Prompt structure | Estimation uses Role/Required context/Analysis procedure/Required outputs/Quality gates; Planning uses Role/Required inputs/Procedure/Required outputs/Quality gates; Tender uses Objective/Required inputs/Procedure/Deliverables/Completion gates | Harder prompt linting and orchestration |
| Workflow catalog | Only Estimation has `workflows/catalog.yaml` | No uniform machine registry |
| Workflow schemas | Estimation repeats full schemas; Planning/Tender use shared per-agent envelopes with `allOf` | Validator complexity and drift |
| Standards register | Only Estimation has `knowledge/standards-register.yaml` | Inconsistent knowledge governance |
| Dates | Date-only and date-time fields vary; cutoff fields are sometimes unformatted strings | Ambiguous comparisons and deadlines |
| Units | Estimation declares SI/imperial/mixed; Planning fixes durations/lags in hours; Tender lacks shared unit metadata | Unsafe calculations and handoffs |
| Output capability | Manifests list DOCX/XLSX/PDF/XER/XML/ZIP-like outputs although renderers/writers do not exist | Capability overstatement if status is ignored |

No direct contradiction was found in the core safety rules; the main conflicts concern ownership, identity, and data contracts.

## 6. Broken references and missing dependencies

### 6.1 Broken file references

No broken local Markdown link or JSON `$ref` target was found by the current static checks. Each agent's workflow-to-prompt links was validated during its implementation milestone.

Cross-agent references are a different problem: they are narrative strings, not resolvable artifact contracts. A Tender workflow can request an `approved_planning_agent_artifact`, but no registry or shared schema proves what it is, where it is stored, or whether its approval/version is valid.

### 6.2 Missing executable dependencies

The repository has no `package.json`, Python project manifest, dependency lockfile, build command, test command, executable source package, or CI workflow. Required future tools are listed in documentation but have no implementation or dependency declaration.

Missing runtime dependencies include:

- YAML parsing and schema validation.
- JSON Schema Draft 2020-12 validation and reference resolution.
- Document/OCR parsing and evidence extraction.
- Unit/currency/date normalization.
- Quantity, rate, price, CPM, resource, cost, cash-flow, and histogram engines.
- DOCX/XLSX/PDF rendering and validation.
- XER/P6 XML parsing/writing and round-trip validation.
- File preflight, malware scanning, checksums, packaging, and portal connectors.

## 7. Incomplete workflows and placeholders

All 44 workflow contracts are complete as specifications but incomplete as executable workflows. There is no handler behind any declared tool category, no persistent artifact store, no orchestrator state machine, and no consolidated-result generator.

Placeholder scan findings:

- Root `README.md` still describes planned sections and says the project is currently under development.
- `AI-Prompts/Tendering/README.md` says that legacy section is currently under development.
- Tender `tools/README.md` explicitly states that tool categories are declared but none are implemented.
- Estimation `README.md` explicitly states that runtime parsers, engines, and generators are not implemented.

No `TODO`, `TBD`, lorem ipsum, or blank placeholder artifacts were found in the implemented agent content. Evaluation `expected/` directories contain only explanatory READMEs and no expected results.

## 8. Files planned but not implemented

The architecture describes `apps/`, shared `packages/`, `connectors/`, standards libraries, governance services, and ten specialized agents. Only the three current agent specifications exist. The seven unimplemented initial agents are Quantity Survey, Contract & Claims, BIM & Digital Construction, Project Management, Cost Control, QA/QC, and HSE.

For Phase 7 specifically, the following requested components are absent:

- Shared canonical schemas for project, BOQ, activity, WBS, resource, rate, risk, RFI, clarification, assumption, exclusion, and deliverable data.
- Central orchestrator and workflow registry.
- Cross-agent artifact handoff and consolidated-result schema.
- Mandatory validation policies executable in code.
- Automated tests and test data.
- Excel generation implementation and tests.
- Error/missing-data runtime behavior.
- End-to-end demonstration project and outputs.
- Testing report from executable workflows.

## 9. Standardization target

Preserve agent folders and introduce shared contracts above them.

### Folder and identity

- Keep `agents/<agent-id>/...` unchanged.
- Use lowercase kebab-case for platform directories and workflow IDs.
- Use fully qualified workflow identity: `<agent-id>/<workflow-id>`.
- Treat `AI-Prompts/` as a legacy namespace; do not mass-rename it during integration.

### Prompt contract

Standard workflow prompts should contain:

1. Title.
2. Role.
3. Objective.
4. Required inputs.
5. Procedure.
6. Required outputs.
7. Quality gates.
8. Authority and escalation.

Machine metadata remains in `workflow.yaml`; prompts should not duplicate versions or routing configuration.

### Metadata and engineering conventions

- Currency: ISO 4217 uppercase code; amount and price base date required where material.
- Dates: ISO 8601; deadlines and events use date-time with explicit UTC offset plus IANA time zone in project/tender metadata.
- Durations/lags: canonical hours plus assigned calendar; display-day conversion must name its calendar.
- Units: controlled unit code, dimension, unit system, precision, and conversion source; never free-text-only for calculations.
- Documents: stable source ID, original filename, document number, title, revision, issue date, controlled status, classification, checksum, location, extraction method, confidence, and precise locator.
- Artifacts: stable ID, owning agent, workflow, version, schema ID, status, checksum, approval, source set, created time, and URI/path.
- Suggested controlled filename: `<project-or-tender>-<discipline>-<document-type>-<sequence>-<revision>-<status>.<ext>`, with client rules overriding when required.

## 10. Audit decision

Proceed to a shared-contract and orchestrator foundation only after approving:

1. Additive `packages/contracts` and `packages/orchestrator` locations.
2. Python runtime and dependency policy proposed in `RECOMMENDED-CORRECTIONS.md`.
3. Composite workflow identity without immediate file renames.
4. Compatibility adapters that preserve existing agent schemas during migration.

No files are recommended for deletion in Milestones 7.1–7.3.
