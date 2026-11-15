# AI Engineering Agent Architecture

## Document status

- Status: Proposed foundation architecture
- Milestone: M0 — Product and architecture specification
- Scope: Specialized AI-agent architecture only
- Implementation status: No runtime code has been created
- Intended audience: Product owners, construction-domain experts, architects, engineers, security reviewers, and contributors

## 1. Purpose

Construction-AI-Toolkit will evolve from a collection of standalone prompts into a modular AI Engineering Platform for construction, estimating, quantity surveying, planning, BIM, contracts, claims, project management, cost control, quality, and safety.

This document defines the first ten specialized agents, the services they share, how they exchange information, their professional-review boundaries, and the repository structure required to develop them independently without creating ten disconnected applications.

The platform is intended to support qualified professionals. It does not replace professional engineering judgment, contractual advice, statutory approvals, safety leadership, or an authorized person's signature.

## 2. Architectural objectives

The platform shall:

1. Keep each domain agent specialized, independently testable, and versioned.
2. Use deterministic code for quantities, units, schedules, costs, dates, formulas, and compliance rules.
3. Use language models for extraction, classification, drafting, explanation, and decision support.
4. Require every material finding to be traceable to source evidence or marked explicitly as an assumption.
5. Prevent an agent from claiming to have inspected a file format that the platform has not parsed.
6. Preserve project, document, workflow, and approval history in an auditable record.
7. Support human review gates proportional to the consequences of the output.
8. Allow multiple AI providers without embedding provider-specific behavior in domain agents.
9. Keep project data isolated by organization, project, role, and data classification.
10. Support regional standards, contract editions, measurement rules, currencies, languages, and units through versioned profiles.

## 3. Non-goals for the initial architecture

The initial platform will not:

- Autonomously approve designs, schedules, payments, contracts, claims, materials, work methods, or HSE plans.
- Replace Primavera P6, authoring BIM tools, ERP systems, common data environments, or document-control systems.
- Treat generated text as evidence.
- Reproduce licensed standards, proprietary cost databases, or contract publications without permission.
- Allow one agent to silently overwrite another agent's result.
- train foundation models on customer project data by default.

## 4. Platform context

```text
Users and external systems
        |
Web UI | API | CLI | Excel add-in | CDE and enterprise connectors
        |
Identity, authorization, project workspace, and workflow orchestration
        |
Specialized domain agents
        |
Deterministic engineering services and shared AI capabilities
        |
Evidence store | structured project data | knowledge profiles | audit log
        |
Document, P6, BIM, cost, ERP, procurement, and reporting integrations
```

## 5. Logical architecture

### 5.1 Experience layer

Provides role-specific interaction surfaces:

- Web workspace for projects, documents, analyses, reviews, and approvals.
- REST API for enterprise integrations.
- Command-line interface for batch validation and automation.
- Future Microsoft Excel add-in for BOQ, estimation, quantity surveying, and cost control.
- Future BIM and CDE integrations for model issues and document workflows.

The experience layer never contains domain calculation logic.

### 5.2 Platform control layer

Shared services coordinate work without becoming another domain expert:

- Identity and role-based access control.
- Organization and project tenancy.
- Workflow registry and version selection.
- Task routing to one or more agents.
- Background-job scheduling.
- Human review and approval gates.
- Notifications and due dates.
- Usage, cost, latency, and quality monitoring.
- Immutable audit events.

### 5.3 Specialized agent layer

The initial domain agents are:

1. Estimation Agent.
2. Quantity Survey Agent.
3. Planning & Primavera P6 Agent.
4. Tender & Proposal Agent.
5. Contract & Claims Agent.
6. BIM & Digital Construction Agent.
7. Project Management Agent.
8. Cost Control Agent.
9. QA/QC Agent.
10. HSE Agent.

Agents are logical modules with constrained tools, workflows, schemas, knowledge profiles, and evaluation suites. An agent is not merely a system prompt.

### 5.4 Deterministic engineering services

Shared calculation and validation services include:

- Unit, currency, and rate normalization.
- Quantity and BOQ reconciliation.
- Cost build-up, escalation, cash-flow, and earned-value calculations.
- CPM, longest-path, float, schedule variance, and DCMA checks.
- Contract dates, notice periods, and chronology calculations.
- Risk scoring and quantitative risk analysis.
- IFC, IDS, COBie, and BCF validation.
- KPI and project-health calculations.
- Document numbering, revision, and status validation.

Agents may explain these results, but they may not replace them with model-generated arithmetic.

### 5.5 Document intelligence and evidence layer

This layer provides:

- Parsing for PDF, DOCX, XLSX, CSV, images, P6 XER/XML, IFC, IDS, COBie, and BCF as support is added.
- OCR with extraction-quality indicators.
- Page, paragraph, clause, sheet, cell, activity, relationship, and model-element references.
- Document versions, revisions, effective dates, and supersession relationships.
- Retrieval scoped to the current organization and project.
- Evidence bundles attached to findings.
- Explicit distinction among source facts, deterministic calculations, user statements, assumptions, and AI recommendations.

### 5.6 Knowledge layer

Knowledge is supplied through versioned profiles rather than permanently embedded in prompts:

- Contract forms and editions.
- Measurement standards.
- Scheduling practices.
- BIM information requirements.
- Cost and productivity datasets.
- Quality and HSE regulations.
- Organization procedures.
- Client and project requirements.
- Regional language, currency, unit, tax, and regulatory profiles.

Every profile records its owner, jurisdiction, edition, effective date, license status, and review date.

### 5.7 Governance and observability layer

Cross-cutting controls include:

- Prompt and workflow versioning.
- Model and provider version recording.
- Evaluation scores and release gates.
- Data-loss-prevention controls.
- Prompt-injection defenses for uploaded documents.
- Tool-call authorization and allowlists.
- Human-review policies.
- Trace logging without exposing protected document contents.
- Incident response, retention, deletion, and export controls.

## 6. Common agent contract

Every agent shall implement the same logical contract.

### 6.1 Agent manifest

Each agent declares:

- Stable agent ID and display name.
- Mission and supported use cases.
- Owners and qualified reviewers.
- Supported workflow versions.
- Accepted input types and maximum classifications.
- Allowed tools and integrations.
- Required knowledge profiles.
- Output schemas.
- Review tier.
- Evaluation thresholds.
- Known limitations.

### 6.2 Input envelope

Every request contains, where applicable:

- Organization and project identifiers.
- User, role, and authorization context.
- Workflow ID and version.
- Project region, currency, language, and unit system.
- Contract, standard, or measurement profile.
- Document and data references, including revisions.
- User-provided parameters.
- Prior approved findings from other agents.
- Requested output format.
- Due date and review route.

### 6.3 Output envelope

Every material output contains:

- Execution and workflow version identifiers.
- Status: complete, incomplete, blocked, or requires review.
- Executive summary.
- Structured findings.
- Source citations or deterministic calculation references.
- Assumptions and exclusions.
- Missing or conflicting information.
- Confidence and data-quality indicators.
- Risks and recommended actions.
- Required reviewer roles.
- Machine-readable result and human-readable artifact references.

### 6.4 Finding model

A finding shall identify:

- Domain and category.
- Description and significance.
- Source reference.
- Basis: evidence, calculation, user statement, or assumption.
- Severity and priority.
- Responsible party when known.
- Recommended action.
- Target date when applicable.
- Confidence.
- Review and resolution status.

### 6.5 Task lifecycle

```text
Draft request
  -> validate authorization and inputs
  -> classify and parse sources
  -> run deterministic checks
  -> execute agent workflow
  -> validate output schema and citations
  -> domain review when required
  -> approve, reject, or revise
  -> publish controlled artifact
  -> preserve audit history
```

## 7. Agent collaboration model

Agents collaborate through structured, versioned artifacts rather than hidden conversational memory.

Examples:

- The BIM Agent produces model quantities; the Quantity Survey Agent validates measurement treatment; the Estimation Agent prices the accepted quantities.
- The Planning Agent produces schedule status and delay calculations; the Contract & Claims Agent evaluates contractual notice and entitlement using those approved calculations.
- The Tender Agent assembles proposal content from approved outputs of Estimation, Planning, BIM, QA/QC, and HSE agents.
- The Project Management Agent consolidates approved schedule, cost, risk, quality, safety, and procurement status without recalculating them.
- The Cost Control Agent consumes approved budget, commitment, progress, variation, and forecast data rather than extracting numbers from narrative reports.

Agent conflicts are surfaced as reconciliation tasks. The platform does not automatically choose the most favorable answer.

## 8. Human review tiers

### Tier 0 — Informational

Examples: document summaries and navigation. Normal user review is sufficient.

### Tier 1 — Operational assistance

Examples: draft reports, registers, and checklists. A responsible project team member reviews before use.

### Tier 2 — Professional decision support

Examples: estimate recommendations, schedule audits, payment assessments, model compliance findings, QA dispositions, and HSE risk controls. A qualified domain professional must approve.

### Tier 3 — Contractual, statutory, or safety-critical

Examples: claim entitlement, contractual notices, payment certification, design approval, method-statement approval, and permission to perform high-risk work. An authorized professional approves outside the AI system's authority boundary.

## 9. Canonical agent folder structure

Each agent uses the following structure when implementation begins:

```text
agents/<agent-id>/
├── README.md
├── agent.yaml
├── knowledge/
│   ├── README.md
│   └── profiles.yaml
├── prompts/
│   ├── system.md
│   ├── shared/
│   └── <workflow-id>/
├── workflows/
│   └── <workflow-id>/
│       ├── workflow.yaml
│       ├── input.schema.json
│       ├── output.schema.json
│       ├── safety.md
│       └── CHANGELOG.md
├── tools/
│   └── README.md
├── evaluations/
│   ├── rubric.yaml
│   ├── cases/
│   └── expected/
├── examples/
│   ├── inputs/
│   └── outputs/
└── docs/
    ├── limitations.md
    └── reviewer-guide.md
```

Runtime code, deterministic calculations, parsers, and connectors remain in shared packages rather than being duplicated inside agent folders.

---

## 10. Estimation Agent

### Mission

Produce transparent, traceable, and reviewable construction estimates from defined scope, quantities, productivity assumptions, market inputs, and commercial rules.

### Responsibilities

- Build conceptual, preliminary, definitive, and tender estimates.
- Develop direct and indirect cost structures.
- Create labor, material, plant, subcontract, overhead, contingency, and margin build-ups.
- Normalize units, currencies, tax treatment, escalation, and pricing dates.
- Detect pricing gaps, abnormal rates, duplicate scope, and missing allowances.
- Run scenario, sensitivity, and value-engineering comparisons.
- Record estimate basis, qualifications, assumptions, exclusions, and confidence class.
- Reconcile estimate totals with BOQ, schedule, procurement, and cost-control structures.

### Inputs

- Scope of work and employer requirements.
- Drawings, specifications, and design maturity.
- BOQ or quantity takeoff.
- WBS, CBS, work packages, and cost codes.
- Labor, material, plant, and subcontract rates.
- Productivity norms and crew compositions.
- Supplier and subcontractor quotations.
- Location, currency, pricing date, taxes, escalation, and risk profile.
- Construction method, schedule, logistics, and site constraints.

### Outputs

- Estimate summary and detailed cost build-up.
- Basis of estimate.
- Cost breakdown structure.
- Resource and rate build-ups.
- Indirect cost and preliminaries schedule.
- Escalation, contingency, and risk allowances.
- Sensitivity and scenario analysis.
- Qualifications, exclusions, and missing-information register.
- Estimate reconciliation and approval package.

### Required knowledge

- AACE estimate classification and recommended practices.
- Construction methods, productivity, and cost engineering.
- Local market rates, currencies, taxation, escalation, and logistics.
- Measurement rules and BOQ conventions.
- WBS/CBS alignment and project controls.
- Company estimating procedures and historical data governance.

### Required prompt templates

- Estimate planning and basis-of-estimate preparation.
- BOQ pricing review.
- Rate build-up explanation.
- Indirect cost and preliminaries review.
- Estimate risk and contingency review.
- Estimate reconciliation.
- Value-engineering option comparison.
- Estimate executive summary.

### Required workflows

1. Validate scope and estimate class.
2. Normalize quantities, units, currency, and pricing date.
3. Map quantities to cost codes and work packages.
4. Apply deterministic rate and resource calculations.
5. Reconcile quotations and internal rates.
6. Analyze gaps, risks, escalation, and contingency.
7. Produce estimate artifacts.
8. Route for estimator and commercial approval.

### Folder structure

```text
agents/estimation-agent/
├── knowledge/{aace,productivity,regional-costs}/
├── prompts/{basis-of-estimate,rate-build-up,risk-review,value-engineering}/
├── workflows/{conceptual-estimate,detailed-estimate,tender-estimate,reconciliation}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- CostX, Candy, Sage Estimating, Autodesk Estimate, and RIB platforms.
- Excel and approved cost databases.
- ERP and accounting systems.
- Supplier quotation portals.
- BIM 5D quantities.
- Primavera P6 and procurement schedules.

---

## 11. Quantity Survey Agent

### Mission

Manage quantities, measurement, valuation, change, and commercial records consistently throughout the project lifecycle.

### Responsibilities

- Validate BOQ structure, units, descriptions, and measurement coverage.
- Perform or review quantity takeoff from structured inputs.
- Compare design, BOQ, site, and as-built quantities.
- Prepare measurement sheets and valuation support.
- Manage variations, dayworks, provisional sums, and remeasurement.
- Review interim payment applications and material-on-site records.
- Prepare cost plans, final accounts, and commercial reconciliations.
- Identify missing, duplicated, ambiguous, or unmeasurable items.

### Inputs

- BOQ, drawings, models, specifications, and addenda.
- Applicable measurement standard and contract pricing rules.
- Approved variations and instructions.
- Site measurements, inspection records, and progress evidence.
- Prior payment certificates and material-on-site records.
- Rates, quotations, daywork sheets, and cost records.
- Completion, handover, and final-measurement information.

### Outputs

- Normalized BOQ and measurement register.
- Quantity takeoff and reconciliation.
- Missing and duplicate item report.
- Variation valuation.
- Interim payment assessment.
- Material-on-site assessment.
- Cost plan and final-account reconciliation.
- Commercial risk and action register.

### Required knowledge

- RICS professional standards and applicable measurement methods.
- CESMM, NRM, POMI, SMM, or project-specific rules as licensed and selected.
- FIDIC and other contract valuation mechanisms.
- Quantity takeoff, remeasurement, valuation, and final-account practice.
- Construction methods and model-based quantities.
- Regional tax, currency, retention, and payment conventions.

### Required prompt templates

- BOQ completeness review.
- Measurement-rule interpretation.
- Quantity reconciliation.
- Variation valuation narrative.
- Interim payment review.
- Material-on-site review.
- Final account preparation.
- Commercial clarification and RFI generation.

### Required workflows

1. Select the measurement and contract profile.
2. Parse and normalize the BOQ.
3. Link quantities to source drawings, model elements, or measurement sheets.
4. Apply deterministic unit and arithmetic checks.
5. Reconcile changes, progress, and prior valuations.
6. Generate exceptions and commercial findings.
7. Route valuations for qualified QS approval.

### Folder structure

```text
agents/quantity-survey-agent/
├── knowledge/{measurement,valuation,commercial}/
├── prompts/{boq-review,takeoff,variation,ipc,final-account}/
├── workflows/{boq-validation,quantity-reconciliation,valuation,final-account}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- CostX, Bluebeam, PlanSwift, Cubit, and Excel.
- Revit, IFC, and 5D BIM platforms.
- ERP, payment, and contract-management systems.
- Site measurement and inspection applications.
- CDE drawing and revision services.

---

## 12. Planning & Primavera P6 Agent

### Mission

Develop, validate, update, analyze, and explain construction schedules using deterministic CPM and project-controls methods.

### Responsibilities

- Develop WBS, activities, milestones, calendars, codes, and logic.
- Validate baseline and updated schedules.
- Calculate CPM, longest path, float, and variance using approved engines.
- Perform DCMA-style schedule quality checks.
- Review resource and cost loading.
- Support progress updates, lookaheads, recovery planning, and scenario analysis.
- Identify critical, near-critical, delayed, and out-of-sequence activities.
- Produce approved schedule facts for claims, cost control, BIM 4D, and reporting.

### Inputs

- P6 XER/XML or structured schedule data.
- Contract milestones and completion requirements.
- WBS, scope, BOQ, quantities, and productivity.
- Calendars, constraints, resources, costs, and activity codes.
- Baseline, updates, actuals, data date, and progress rules.
- Procurement, submittal, design, and risk registers.
- Delay events and contemporaneous records.

### Outputs

- Schedule model and validation report.
- CPM, longest-path, and float analysis.
- DCMA assessment and findings register.
- Baseline/update variance report.
- Critical and near-critical activity lists.
- Progress, lookahead, recovery, and milestone reports.
- Resource and schedule-risk findings.
- Structured schedule facts for other agents.

### Required knowledge

- Primavera P6 data concepts and scheduling behavior.
- CPM, calendars, constraints, progress, and resource loading.
- DCMA 14-point assessment.
- AACE planning and scheduling practices.
- PMI scheduling principles.
- SCL delay and disruption concepts for analysis support.
- Construction sequencing and procurement logic.

### Required prompt templates

- WBS and activity development.
- Baseline schedule narrative.
- Logic and constraint review.
- Schedule audit explanation.
- Progress update narrative.
- Critical-path and float interpretation.
- Recovery option assessment.
- Schedule risk and executive reporting.

### Required workflows

1. Import and validate P6 data.
2. Normalize calendars, dates, relationships, and codes.
3. Run deterministic CPM and audit checks.
4. Compare baseline and update versions.
5. Identify findings and supporting activity references.
6. Develop recovery or scenario options without overwriting source schedules.
7. Route schedule conclusions for planner approval.

### Folder structure

```text
agents/planning-p6-agent/
├── knowledge/{p6,cpm,dcma,aace,scl}/
├── prompts/{wbs,baseline,logic,audit,update,recovery}/
├── workflows/{schedule-import,baseline-review,update-review,dcma-audit,recovery}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- Primavera P6 Professional, EPPM Web Services, and Primavera Cloud.
- Microsoft Project and Asta Powerproject.
- Safran Risk, Acumen Fuse, and schedule-risk tools.
- ERP, procurement, BIM 4D, and field-progress platforms.
- Power BI and executive reporting.

---

## 13. Tender & Proposal Agent

### Mission

Coordinate evidence-based tender analysis and assemble compliant, persuasive, and internally approved technical and commercial submissions.

### Responsibilities

- Build tender requirements and compliance matrices.
- Identify missing documents, ambiguities, risks, and submission obligations.
- Coordinate RFIs and clarification responses.
- Support bid/no-bid decisions.
- Assemble technical methodologies, organization, schedule, procurement, QA/QC, HSE, BIM, and project-control sections.
- Assemble approved commercial content without altering validated estimate totals.
- Track qualifications, exclusions, assumptions, forms, bonds, signatures, and deadlines.
- Perform final submission-readiness reviews.

### Inputs

- Invitation to tender and instructions to bidders.
- Employer requirements, scope, drawings, specifications, BOQ, and contract conditions.
- Addenda, clarifications, forms, and submission portal requirements.
- Company profile, experience, staff, equipment, and credentials.
- Approved outputs from Estimation, QS, Planning, BIM, QA/QC, and HSE agents.
- Win themes, competitive context, and approval limits.

### Outputs

- Tender document review.
- Requirements and compliance matrix.
- RFI and clarification register.
- Bid/no-bid recommendation.
- Technical proposal and supporting plans.
- Commercial proposal assembled from approved data.
- Risk, assumption, qualification, and exclusion registers.
- Final bid checklist and submission package index.

### Required knowledge

- Tender governance and stage-gate processes.
- Proposal management and persuasive technical writing.
- Construction delivery methods.
- Contract, commercial, planning, BIM, QA/QC, and HSE interfaces.
- Client submission rules and regional procurement practices.
- Confidentiality, conflicts, approvals, and anti-collusion controls.

### Required prompt templates

- Tender document review.
- Compliance matrix.
- Bid/no-bid assessment.
- RFI generation.
- Technical proposal section drafting.
- Executive summary and win themes.
- Commercial qualifications and exclusions.
- Final bid review.

### Required workflows

1. Register tender documents, revisions, and deadlines.
2. Extract requirements and submission rules.
3. Assign requirements to responsible agents and contributors.
4. Resolve gaps through RFIs and approved assumptions.
5. Assemble reviewed domain outputs.
6. Validate compliance, forms, signatures, and totals.
7. Route through tender and executive approval gates.

### Folder structure

```text
agents/tender-proposal-agent/
├── knowledge/{tendering,proposal,submission,company-content}/
├── prompts/{review,compliance,bid-no-bid,rfi,technical,commercial,final-review}/
├── workflows/{tender-intake,bid-decision,proposal-development,submission-review}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- CRM and opportunity-management systems.
- SharePoint, CDE, and tender portals.
- Microsoft Word, PowerPoint, and Excel.
- E-signature and approval platforms.
- Company CV, project-reference, and capability databases.

---

## 14. Contract & Claims Agent

### Mission

Support disciplined contract administration, notice compliance, change management, claims preparation, and dispute avoidance with clause-level traceability.

### Responsibilities

- Extract obligations, deliverables, notices, deadlines, risk allocation, and payment provisions.
- Build clause, correspondence, instruction, variation, and event registers.
- Draft notices and contractual correspondence from approved facts.
- Track change and claim status.
- Build chronologies and evidence matrices.
- Combine approved schedule and cost analyses into claim support.
- Distinguish time entitlement, cost entitlement, and factual causation.
- Support negotiation and closeout without issuing legal conclusions autonomously.

### Inputs

- Executed agreement, general and particular conditions, appendices, and amendments.
- FIDIC/NEC or other selected contract profile and edition.
- Scope, BOQ, specifications, drawings, and employer requirements.
- Correspondence, instructions, RFIs, meeting minutes, reports, and photos.
- Schedule facts from the Planning Agent.
- Quantity and cost facts from QS, Estimation, and Cost Control agents.
- Governing law, dispute process, and authorization context.

### Outputs

- Contract summary, obligation matrix, and risk register.
- Notice and deadline register.
- Draft notices and correspondence with clause citations.
- Variation and claim registers.
- Event chronology and evidence matrix.
- EOT and quantum-support package.
- Negotiation issue list and closeout report.
- Explicit legal/professional review requirements.

### Required knowledge

- Selected FIDIC, NEC, EPC, design-build, lump-sum, and remeasurement profiles.
- Contract administration and notice mechanisms.
- SCL Delay and Disruption Protocol.
- AACE forensic schedule and cost practices.
- Claims causation, entitlement, quantum, and evidence principles.
- Applicable governing-law limitations supplied by qualified reviewers.

### Required prompt templates

- Contract review and obligation extraction.
- Contract risk assessment.
- Notice of delay and reservation of rights.
- Variation assessment.
- Claim chronology and evidence review.
- EOT support narrative.
- Payment and final-account issue review.
- Contract closeout.

### Required workflows

1. Select contract, edition, and jurisdiction profiles.
2. Parse and index clauses and amendments.
3. Extract obligations, dates, notices, and risks.
4. Link events to correspondence and project evidence.
5. Import approved schedule, quantity, and cost findings.
6. Draft controlled contractual artifacts.
7. Require contract-manager and legal review where applicable.

### Folder structure

```text
agents/contract-claims-agent/
├── knowledge/{contract-profiles,claims,delay,quantum,jurisdictions}/
├── prompts/{review,notice,variation,eot,claim,negotiation,closeout}/
├── workflows/{contract-intake,notice-control,variation,claim,eot,closeout}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- Contract lifecycle management systems.
- CDE correspondence and transmittals.
- Primavera P6 and cost-control systems.
- E-discovery and document review platforms.
- E-signature, legal hold, and records-management systems.

---

## 15. BIM & Digital Construction Agent

### Mission

Validate digital project information, coordinate multidisciplinary models, and connect BIM data to schedule, cost, construction, and asset outcomes.

### Responsibilities

- Review BIM requirements and execution plans.
- Validate IFC, IDS, COBie, classification, naming, and information completeness.
- Ingest clash and issue data and manage BCF-based resolution.
- Assess model quality, coordination, constructability, and handover readiness.
- Map model objects to WBS, schedule activities, BOQ items, assets, and locations.
- Support 4D sequencing and 5D cost integration.
- Evaluate digital-twin readiness and asset-information quality.
- Separate automated model checks from professional design approval.

### Inputs

- EIR/AIR, BEP, MIDP/TIDP, information standard, and responsibility matrix.
- IFC, IDS, COBie, BCF, model metadata, and clash results.
- Classification, LOIN/LOD/LOI, naming, and exchange requirements.
- Schedule, BOQ, cost codes, asset requirements, and handover documents.
- Project coordinates, model versions, disciplines, and authoring records.

### Outputs

- BIM compliance and model-quality report.
- Information-requirement matrix.
- Clash and issue register.
- Model-element findings with stable identifiers.
- 4D and 5D mapping tables.
- COBie and asset-information validation.
- Handover and digital-twin readiness assessment.
- Professional-review and unresolved-issue register.

### Required knowledge

- ISO 19650 information management.
- buildingSMART IFC, IDS, BCF, and bSDD concepts.
- COBie and asset-information management.
- Revit, Navisworks, Solibri, ACC, and common CDE workflows.
- 4D/5D integration, classification, LOIN, and model coordination.
- Discipline-specific review boundaries.

### Required prompt templates

- BIM execution plan review and generation.
- Model review and QA/QC explanation.
- Clash prioritization and coordination report.
- IFC/IDS/COBie validation narrative.
- 4D sequence review.
- 5D quantity/cost integration review.
- As-built and handover review.
- Digital-twin readiness assessment.

### Required workflows

1. Register information requirements and model revisions.
2. Parse supported open formats.
3. Run deterministic schema, rule, and information checks.
4. Import clashes and coordinate issues.
5. Map elements to schedule, cost, and asset structures.
6. Generate evidence-linked findings.
7. Route design and information decisions to authorized reviewers.

### Folder structure

```text
agents/bim-digital-agent/
├── knowledge/{iso-19650,ifc,ids,bcf,cobie,classification}/
├── prompts/{bep,model-review,clash,4d,5d,qaqc,handover,digital-twin}/
├── workflows/{requirements,model-validation,coordination,4d-5d,handover}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- Autodesk Construction Cloud, Revit, and Navisworks.
- Bentley iTwin and ProjectWise.
- Solibri, Revizto, BIMcollab, and Dalux.
- Synchro 4D.
- Asset-management and digital-twin platforms.
- Reality capture and progress-verification systems.

---

## 16. Project Management Agent

### Mission

Provide an integrated, evidence-based view of project objectives, governance, progress, decisions, risks, interfaces, and actions.

### Responsibilities

- Maintain project charter, objectives, stakeholders, governance, and responsibility models.
- Coordinate scope, schedule, cost, quality, safety, procurement, contract, and BIM status.
- Manage risks, issues, decisions, actions, interfaces, and change requests.
- Prepare meeting, weekly, monthly, and executive reports.
- Track commitments, approvals, and overdue actions.
- Consolidate approved outputs from specialist agents.
- Surface conflicts between domain plans and reported status.
- Support lessons learned and project closeout.

### Inputs

- Project charter, scope, organization, governance, and objectives.
- Approved outputs from all specialist agents.
- Risk, issue, action, decision, change, and interface registers.
- Meeting minutes, reports, correspondence, and stakeholder requirements.
- Schedule, cost, quality, HSE, procurement, contract, and BIM status.

### Outputs

- Integrated project management plan.
- Project status and executive reports.
- Risk, issue, action, decision, interface, and change registers.
- Responsibility and communication matrices.
- Decision briefs and escalation recommendations.
- Project health summary.
- Lessons learned and closeout package.

### Required knowledge

- PMI project-management and governance principles.
- Construction execution and stage-gate governance.
- Risk, issue, change, stakeholder, and interface management.
- Executive reporting and decision support.
- Lean and collaborative planning concepts.
- Organization-specific approval and delegation rules.

### Required prompt templates

- Project charter and management plan.
- Governance and RACI preparation.
- Risk and issue review.
- Meeting minutes and action extraction.
- Weekly/monthly/executive reporting.
- Change and decision brief.
- Project health check.
- Lessons learned and closeout.

### Required workflows

1. Establish project governance and registers.
2. Import only approved domain status.
3. Reconcile cross-domain dates, values, and risks.
4. Prepare decisions, actions, and escalations.
5. Generate controlled reports.
6. Route actions and decisions to accountable roles.
7. Preserve decision and approval history.

### Folder structure

```text
agents/project-management-agent/
├── knowledge/{governance,pmi,risk,change,interfaces}/
├── prompts/{charter,plans,meetings,reports,decisions,health,closeout}/
├── workflows/{project-setup,status-cycle,change-control,decision,closeout}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- Microsoft Project, Planner, Teams, Outlook, and SharePoint.
- Jira, Confluence, Asana, and Monday.com.
- CDE, ERP, risk, cost, schedule, and field-management systems.
- Power BI and portfolio-management platforms.

---

## 17. Cost Control Agent

### Mission

Maintain a reconciled, auditable view of budgets, commitments, actuals, accruals, earned value, cash flow, changes, and forecasts.

### Responsibilities

- Establish and maintain the cost breakdown structure and control budget.
- Reconcile budget, commitments, actuals, accruals, forecasts, and changes.
- Calculate EVM and forecast metrics deterministically.
- Analyze cost variance, trends, productivity, escalation, and contingency drawdown.
- Produce cash-flow and estimate-at-completion scenarios.
- Connect quantities, schedule progress, procurement, variations, and claims to cost status.
- Detect duplicate, missing, stale, or inconsistent cost data.
- Prepare period-close and executive cost reports.

### Inputs

- Approved estimate and budget.
- CBS, WBS, cost codes, control accounts, and reporting periods.
- Commitments, purchase orders, invoices, actuals, accruals, and payments.
- Progress and earned-value rules.
- Variations, claims, contingency, risk, and escalation data.
- Schedule, procurement, quantity, and productivity information.

### Outputs

- Budget and commitment reconciliation.
- Cost report and variance analysis.
- EVM metrics with calculation trace.
- EAC, ETC, VAC, and scenario forecasts.
- Cash-flow and funding forecast.
- Contingency and change status.
- Cost risk register and corrective-action plan.
- Executive cost dashboard.

### Required knowledge

- AACE cost engineering and project-controls practices.
- ANSI/EIA-748 concepts where applicable.
- Budgeting, commitments, accruals, forecasting, and cash flow.
- WBS/CBS/control-account integration.
- Construction productivity, escalation, and change control.
- ERP and accounting reconciliation principles.

### Required prompt templates

- Period cost review.
- Budget and commitment reconciliation.
- Cost variance explanation.
- EVM interpretation.
- Forecast scenario analysis.
- Cash-flow narrative.
- Contingency and risk review.
- Executive cost report.

### Required workflows

1. Import and validate cost-period data.
2. Reconcile source systems and control structures.
3. Run deterministic calculations.
4. Validate progress and change inputs.
5. Analyze variances and forecast scenarios.
6. Produce period-close reports.
7. Route adjustments and forecasts for cost-manager approval.

### Folder structure

```text
agents/cost-control-agent/
├── knowledge/{aace,evm,forecasting,erp,regional-finance}/
├── prompts/{reconciliation,variance,evm,forecast,cash-flow,executive}/
├── workflows/{budget-setup,period-close,forecast,change-control,reporting}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- SAP, Oracle, Microsoft Dynamics, and other ERP systems.
- EcoSys, Unifier, Procore Financials, and cost platforms.
- Primavera P6, procurement, estimating, and QS systems.
- Banking, currency, index, and approved market-data feeds.
- Power BI and enterprise reporting.

---

## 18. QA/QC Agent

### Mission

Support controlled quality planning, inspection, testing, nonconformance management, material and document approval, and quality closeout.

### Responsibilities

- Generate and review project quality plans, method statements, and ITPs.
- Build inspection, test, hold, witness, and acceptance requirements.
- Review material submittals and technical documentation.
- Track inspections, tests, NCRs, corrective actions, punch lists, and closeout records.
- Check evidence completeness against specifications and approved documents.
- Analyze recurring defects, rework, and quality trends.
- Coordinate quality impacts with schedule, cost, BIM, and HSE.
- Prevent the agent from issuing approval reserved for authorized personnel.

### Inputs

- Contract quality requirements and project quality plan.
- Specifications, drawings, approved submittals, method statements, and ITPs.
- Applicable codes, standards, acceptance criteria, and manufacturer instructions.
- Inspection requests, test results, NCRs, photos, and corrective actions.
- Material certificates, calibration records, and handover requirements.
- Schedule activities and responsible organizations.

### Outputs

- Quality plan and quality-control matrix.
- Method-statement and ITP drafts or review reports.
- Inspection and test checklists.
- Material-submittal compliance matrix.
- NCR, root-cause, and corrective-action package.
- Quality KPI and trend report.
- Punch-list and closeout status.
- Approval recommendation clearly marked for authorized review.

### Required knowledge

- ISO 9001 quality management.
- Construction inspection and testing practice.
- Discipline-specific codes and acceptance criteria supplied through profiles.
- NCR, root-cause, corrective, and preventive action methods.
- Material traceability, calibration, and turnover documentation.
- Project-specific QA/QC procedures and authority matrices.

### Required prompt templates

- Project quality plan.
- Method statement generation and review.
- ITP generation and review.
- Material approval review.
- Shop drawing quality review.
- NCR and root-cause analysis.
- Inspection/test summary.
- Quality closeout and lessons learned.

### Required workflows

1. Register quality requirements and acceptance criteria.
2. Link work packages to method statements and ITPs.
3. Validate inspection and test evidence.
4. Record findings and NCRs.
5. Manage corrective action and verification.
6. Analyze quality trends.
7. Route disposition and approval to authorized QA/QC roles.

### Folder structure

```text
agents/qaqc-agent/
├── knowledge/{iso-9001,inspection,testing,materials,discipline-codes}/
├── prompts/{quality-plan,method-statement,itp,material,ncr,closeout}/
├── workflows/{quality-planning,submittal-review,inspection,ncr,closeout}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- Procore, Autodesk Build, Aconex, ACC, and field-quality platforms.
- Laboratory and test-equipment systems.
- BIM issue and asset systems.
- CDE submittal, inspection, and handover modules.
- Mobile inspection and photo-capture applications.

---

## 19. HSE Agent

### Mission

Support proactive hazard identification, risk assessment, safe-work planning, compliance monitoring, incident learning, and HSE reporting while preserving human authority over safety decisions.

### Responsibilities

- Develop project HSE plans and activity risk assessments.
- Support JSA/JHA, toolbox talks, permits, inspections, and emergency plans.
- Identify hazards associated with methods, locations, interfaces, equipment, and simultaneous operations.
- Maintain legal and project requirement registers through controlled profiles.
- Analyze observations, near misses, incidents, and corrective actions.
- Track leading and lagging HSE indicators.
- Coordinate HSE controls with planning, method statements, BIM logistics, and QA/QC.
- Escalate uncertainty or missing controls; never authorize work.

### Inputs

- Scope, method statements, schedule, site logistics, and work locations.
- Equipment, materials, SDS, temporary works, and workforce information.
- Applicable laws, regulations, client rules, and company procedures.
- Risk assessments, permits, inspections, observations, and training records.
- Incident, near-miss, environmental, occupational-health, and emergency data.
- Weather and site-condition information where authorized.

### Outputs

- Project HSE plan.
- Hazard register and risk assessments.
- JSA/JHA and toolbox-talk drafts.
- Permit-support checklists.
- Inspection and observation reports.
- Emergency and environmental-control plans.
- Incident chronology and learning report.
- HSE KPI dashboard and corrective-action tracker.
- Mandatory review and stop-work escalation flags.

### Required knowledge

- ISO 45001 and ISO 14001 management-system principles.
- Applicable national and local HSE regulations.
- OSHA or other selected regulatory profiles when applicable.
- Construction hazard controls and hierarchy of controls.
- Incident investigation and root-cause methods.
- Emergency response, environmental protection, and occupational health.
- Client and contractor permit-to-work systems.

### Required prompt templates

- Project HSE plan.
- Activity hazard and risk assessment.
- JSA/JHA.
- Toolbox talk.
- Permit-to-work preparation checklist.
- HSE inspection and observation review.
- Incident investigation support.
- Emergency response and HSE performance report.

### Required workflows

1. Select jurisdiction, client, and company HSE profiles.
2. Identify work scope, location, sequence, and interfaces.
3. Extract known hazards and deterministic rule violations.
4. Apply the hierarchy of controls and identify missing safeguards.
5. Route the draft to competent HSE and work supervisors.
6. Record approvals, briefings, permits, and verification.
7. Escalate critical hazards and prevent AI-only authorization.

### Folder structure

```text
agents/hse-agent/
├── knowledge/{iso-45001,iso-14001,regulations,hazards,emergency}/
├── prompts/{hse-plan,risk-assessment,jha,toolbox,permit,incident,reporting}/
├── workflows/{planning,activity-risk,permit-support,inspection,incident,reporting}/
├── evaluations/
├── examples/
└── docs/
```

### Future integrations

- Procore, Autodesk Build, HammerTech, SafetyCulture, and field HSE platforms.
- Permit-to-work and access-control systems.
- IoT wearables, environmental sensors, and equipment telemetry.
- Weather and emergency-notification services.
- Learning-management and competency systems.

---

## 20. Cross-agent ownership boundaries

| Information or decision | System of calculation or owning agent | Consuming agents |
|---|---|---|
| Source quantities | Quantity Survey Agent or BIM validation service | Estimation, Cost Control, Tender |
| Estimate and pricing basis | Estimation Agent | Tender, Cost Control, Project Management |
| Approved schedule facts | Planning & P6 Agent | Claims, BIM, Cost Control, Project Management |
| Contract interpretation draft | Contract & Claims Agent | Project Management, Tender, QS |
| Model compliance findings | BIM Agent | QA/QC, Planning, QS, Project Management |
| Integrated project status | Project Management Agent | Executives and stakeholders |
| Budget, actuals, and forecast | Cost Control Agent | Project Management, Claims, Tender |
| Quality disposition | Authorized QA/QC reviewer, supported by QA/QC Agent | Project Management, HSE, BIM |
| Safety authorization | Authorized HSE and operational roles, never an AI agent | All agents |

## 21. Shared platform folder structure

```text
Construction-AI-Toolkit/
├── agents/
│   ├── estimation-agent/
│   ├── quantity-survey-agent/
│   ├── planning-p6-agent/
│   ├── tender-proposal-agent/
│   ├── contract-claims-agent/
│   ├── bim-digital-agent/
│   ├── project-management-agent/
│   ├── cost-control-agent/
│   ├── qaqc-agent/
│   └── hse-agent/
├── apps/
│   ├── api/
│   ├── web/
│   ├── worker/
│   └── cli/
├── packages/
│   ├── agent-contracts/
│   ├── audit/
│   ├── calculations/
│   ├── database/
│   ├── document-intelligence/
│   ├── evidence/
│   ├── evaluations/
│   ├── llm-gateway/
│   ├── reporting/
│   ├── retrieval/
│   ├── schemas/
│   ├── units/
│   └── workflow-engine/
├── connectors/
│   ├── documents/
│   ├── excel/
│   ├── p6/
│   ├── bim/
│   ├── cde/
│   ├── erp/
│   └── field-systems/
├── standards/
│   ├── profiles/
│   ├── mappings/
│   └── licensing/
├── governance/
├── evaluations/
├── examples/
├── docs/
└── AI-Prompts/
```

`AI-Prompts/` remains available during migration. Each legacy prompt will eventually point to a versioned agent workflow rather than being removed abruptly.

## 22. Data and security architecture

### Data classifications

- Public: published templates and open documentation.
- Internal: organization methods and non-public reference content.
- Confidential: project documents, tenders, estimates, contracts, and commercial data.
- Restricted: personal data, privileged material, security-sensitive drawings, incidents, and regulated records.

### Required controls

- Tenant and project isolation.
- Least-privilege access by role and workflow.
- Encryption in transit and at rest.
- Customer-controlled retention and deletion.
- Region-aware storage and processing.
- No provider training on customer data by default.
- Redaction and data-loss-prevention before external model calls.
- Full provenance for model, prompt, workflow, tool, and reviewer versions.
- Restricted export and download controls.
- Security review for every new connector.

## 23. Evaluation architecture

Each agent requires:

- Schema-validity tests.
- Source-citation and traceability tests.
- Missing-information behavior tests.
- Unsupported-claim and hallucination tests.
- Calculation reconciliation tests.
- Adversarial document and prompt-injection tests.
- Domain-expert scoring rubrics.
- Cross-model regression tests.
- Safety and approval-gate tests.
- Representative regional and project-type cases.

An agent workflow may be labeled experimental, reviewed, validated, or production-ready. Production-ready status requires both automated thresholds and qualified domain approval.

## 24. Recommended implementation sequence

The architecture should be implemented incrementally:

1. Common agent contracts, evidence model, workflow registry, and safety tiers.
2. Estimation and Quantity Survey agents on a shared BOQ and unit model.
3. Planning & P6 Agent with deterministic schedule calculations.
4. Contract & Claims Agent using document evidence and approved schedule facts.
5. Tender Agent as the first cross-agent orchestration use case.
6. Cost Control and Project Management agents for integrated reporting.
7. BIM Agent with open-format validation.
8. QA/QC and HSE agents with strict professional review gates.
9. Enterprise connectors only after the underlying workflows are stable and evaluated.

## 25. Architecture acceptance criteria

This architecture is ready to guide implementation when:

- The missions and ownership boundaries of all ten agents are approved.
- The common input, output, evidence, finding, and review concepts are accepted.
- The platform agrees to deterministic calculations for engineering metrics.
- Human authority boundaries for contractual, design, quality, payment, and safety decisions are accepted.
- The canonical folder structure is approved.
- The initial knowledge, jurisdiction, language, and deployment profiles are selected.

No agent runtime should be implemented until these acceptance criteria and the corresponding architectural decisions are approved.
