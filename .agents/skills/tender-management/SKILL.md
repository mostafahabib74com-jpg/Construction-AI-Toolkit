---
name: tender-management
description: Review construction tender packages end-to-end, reconcile scope and BOQ, identify gaps and risks, coordinate pricing inputs, and prepare technical/commercial bid deliverables.
---

# Tender Management

## Purpose
Run a disciplined construction tender workflow from document intake through final bid review.

## Trigger
Use for tender review, RFQ/RFP analysis, bid preparation, BOQ reconciliation, technical proposal, commercial proposal, tender clarifications, and final submission review.

## Inputs
Required where available:
- invitation/RFQ/RFP;
- BOQ;
- drawings;
- specifications;
- general/special conditions;
- scope of work;
- schedules/appendices;
- addenda and clarifications.

Optional:
- client templates;
- site information;
- vendor/subcontractor quotations;
- historical rates;
- construction programme;
- company profile and credentials.

## Workflow
### 1. Intake and document register
Inventory all files, revisions, dates, disciplines, and apparent superseded documents. Record missing expected documents.

### 2. Scope extraction
Build a structured scope by discipline/package. Identify inclusions, exclusions, interfaces, temporary works, testing, commissioning, handover, warranties, permits, logistics, and client-supplied items.

### 3. Cross-document reconciliation
Cross-check BOQ against drawings, specifications, scope, conditions, schedules, addenda, and clarifications. Log omissions, duplicated scope, inconsistent quantities/descriptions, undefined interfaces, provisional items, and conflicts.

### 4. Commercial and contractual review
Identify payment terms, retention, advance payment, bonds/guarantees, insurance, taxes where stated, LDs, warranty/DLP, variations, measurement/payment rules, price adjustment, programme obligations, and unusual risk transfer.

### 5. Clarifications and RFIs
Create prioritized tender queries. Each query must state the source/reference, issue, impact, and requested clarification.

### 6. Pricing coordination
Route measurable quantity work to quantity-takeoff; unit-rate build-ups to rate-analysis; estimate compilation to construction-estimating; contract issues to contract-management; programme requirements to primavera-p6 when those skills exist. Until then, clearly mark manual/assumption-based work.

### 7. Technical proposal
Prepare scope understanding, methodology, execution strategy, organization, programme narrative, procurement/submittals approach, QA/QC, HSE, logistics, resources, testing/commissioning, and handover as applicable.

### 8. Commercial proposal
Prepare priced summary/BOQ as requested, assumptions, qualifications, exclusions, validity, payment terms, schedule basis, taxes only as supported, and required commercial forms.

### 9. Final bid review
Check completeness, arithmetic, document revision, scope coverage, price consistency, qualifications, signatures/placeholders, submission instructions, and unresolved high-risk items.

## Core checks
Never price from BOQ alone when other tender documents are available. Never silently resolve contradictions. Never invent legal/tax/company data. Keep quantity, rate, amount, currency, and unit traceable.

## Legacy references
Use the existing material in `AI-Prompts/Tendering/` as supporting reference, especially Tender Document Review, BOQ Analysis, Technical Proposal, Commercial Proposal, Risk Assessment, RFI, Method Statement, Execution Plan, and Final Bid Review.

## Deliverables
Depending on the request:
- tender document register;
- scope matrix;
- BOQ reconciliation/gap log;
- risk and opportunity register;
- clarification/RFI schedule;
- pricing assumptions and exclusions;
- technical proposal;
- commercial proposal;
- final bid QA checklist.

## QA/QC
Before submission confirm:
- all available tender documents were reviewed;
- latest known revisions were used;
- BOQ and scope were reconciled;
- major assumptions are explicit;
- unresolved conflicts are visible;
- totals and units are checked;
- technical and commercial narratives agree;
- submission requirements are satisfied.

## Stop conditions
Do not fabricate missing quantities, drawings, specifications, rates, legal data, or contractual terms. If missing information materially prevents a defensible bid, identify the gap and prepare a clarification/assumption rather than concealing it.
