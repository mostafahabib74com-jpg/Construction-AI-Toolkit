# Missing components

## Required for the requested Phase 7 scope

### Shared contracts

- Project information.
- Opportunity/tender information.
- Source document and evidence locator.
- Immutable artifact and approval record.
- BOQ item and quantity.
- WBS node and activity.
- Calendar, relationship, resource, resource assignment, and rate.
- Money, currency/exchange, and calculation trace.
- Risk, RFI, tender clarification, assumption, exclusion, qualification, and deviation.
- Deliverable and submission manifest item.
- Workflow request, result, finding, blocker/error, review, and consolidated result.
- Schema-version compatibility and agent-adapter mappings.

### Central orchestration

- Agent/workflow registry.
- Intent-to-workflow router.
- Prerequisite graph and cycle detection.
- Capability/tool availability registry.
- Input/output schema validator.
- Artifact handoff mapper and immutable artifact store interface.
- Review/approval gate service.
- Consolidated-result builder.
- Run state, correlation ID, audit events, and deterministic retry/error policy.
- A dry-run mode that reports planned routing without invoking unavailable tools.

### Executable safeguards

- Missing quantity and quantity-source validator.
- Missing price/rate/currency/pricing-date validator.
- Contract requirement/assumption/qualification validator.
- Schedule WBS/activity/calendar/logic/open-end/constraint validator.
- Mandatory-field and submission-manifest validator.
- Cross-agent artifact version, status, checksum, and approval validator.
- Technical/commercial/schedule/estimate reconciliation checks.

### Generation and integration services

- Excel estimate workbook generator and validator.
- Controlled chart generation for manpower and organization data.
- DOCX/PDF rendering and preflight.
- Document/OCR parsing.
- P6 XER/XML parser/writer and round-trip validator.
- Secure packaging/checksum/malware interfaces.
- External connectors and portal submission remain later and human-authorized.

### Automated quality system

- Project/dependency manifest and reproducible environment.
- Unit, schema, workflow, routing, handoff, policy, Excel, and error tests.
- Synthetic fixtures and golden expected outputs.
- CI checks for JSON/YAML/schema/reference/prompt/path validation.
- Coverage and evaluation score reporting.

### Demonstration

- Synthetic tender package and company/reference data.
- Tender intake and compliance outputs.
- Scope and RFI outputs.
- BOQ/CBS/preliminary estimate and workbook.
- WBS/activity/schedule/resource outputs.
- Tender checklist/manifest/readiness output.
- Final consolidated result and test evidence.

## Planned platform components outside the immediate three-agent integration

- Quantity Survey Agent.
- Contract & Claims Agent.
- BIM & Digital Construction Agent.
- Project Management Agent.
- Cost Control Agent.
- QA/QC Agent.
- HSE Agent.
- Web/API/CLI/worker applications.
- Identity, tenancy, permissions, persistence, retrieval, observability, retention, and deployment infrastructure.

These should remain backlog items and must not delay a minimal, testable integration of the three implemented agents.
