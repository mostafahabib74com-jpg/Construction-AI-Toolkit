---
name: quantity-takeoff
description: Measure and reconcile construction quantities from drawings, BOQs, specifications, schedules, and other project evidence with traceable calculations and no silent assumptions.
---

# Quantity Takeoff

## Purpose
Produce defensible, traceable construction quantities and reconcile them against BOQ quantities without mixing measurement with pricing.

## Trigger
Use for quantity takeoff, quantity verification, BOQ quantity checking, remeasurement, drawing-based measurement, quantity reconciliation, or preparation of measurable quantities for estimating.

## Inputs
Use all relevant evidence available:
- latest drawings and revisions;
- BOQ and item descriptions;
- specifications;
- schedules;
- scope of work;
- addenda/clarifications;
- project measurement rules or method of measurement;
- approved shop drawings or as-built information when the task is post-award.

Optional:
- previous takeoff sheets;
- BIM/model exports;
- survey data;
- marked-up drawings;
- client quantity templates.

## Workflow
### 1. Establish measurement basis
Identify the project stage, required measurement standard/rules, drawing revision set, units, inclusions/exclusions, and whether the exercise is tender, construction, variation, interim payment, or final account.

### 2. Build source register
List each source used with document number/title, discipline, revision/date, and status. Flag superseded, missing, illegible, or contradictory evidence.

### 3. Build takeoff structure
Break the scope into measurable packages and elements aligned with the BOQ/WBS where useful. Maintain unique item identifiers to prevent duplication.

### 4. Measure
For each item record:
- description;
- source drawing/specification;
- location/grid/level/zone;
- dimensions;
- formula;
- gross quantity;
- deductions/additions;
- net quantity;
- unit;
- assumptions/clarifications.

### 5. Apply measurement rules
Follow the project-specified method of measurement. Do not import SMM/NRM/CESMM or any other convention unless the project requires it or the user explicitly requests it.

### 6. Cross-check
Use independent checks where possible:
- geometry and dimensional consistency;
- plan/elevation/section agreement;
- schedule-to-drawing agreement;
- floor/zone totals;
- repeated-element counts;
- area/volume reasonableness;
- BOQ quantity comparison.

### 7. Reconcile against BOQ
Classify differences as:
- matched;
- BOQ overstatement;
- BOQ understatement;
- missing BOQ item;
- drawing/specification ambiguity;
- duplication risk;
- scope/interface uncertainty.

State both absolute and percentage variance when useful.

### 8. Raise queries
Where evidence is insufficient or conflicting, issue a clarification/RFI entry with source references and quantity impact range if it can be bounded defensibly.

### 9. Deliver takeoff package
Provide the takeoff, reconciliation, assumptions, exclusions, source register, and unresolved quantity risks.

## Core controls
- Never invent dimensions that are not evidenced.
- Never scale dimensions from an image/PDF unless explicitly permitted and scale reliability is verified.
- Never double-count the same physical scope under multiple BOQ items.
- Keep units consistent and show conversions explicitly.
- Separate measured net quantity from waste, laps, cutting allowance, bulking, compaction, overbreak, or productivity factors unless the governing measurement rule requires them.
- Pricing belongs to `rate-analysis` / `construction-estimating`; do not silently add rates.
- Distinguish design quantity, procurement quantity, and payable/measurable quantity when they differ.
- For reinforcement, clearly distinguish theoretical/design steel from procurement/cutting/BBS quantities.
- For concrete/formwork/masonry/finishes, apply openings, deductions, interfaces, and surface definitions only according to the governing measurement rules.

## Deliverables
Depending on the request:
- quantity takeoff sheet/register;
- drawing/source register;
- BOQ reconciliation table;
- variance analysis;
- assumptions and exclusions;
- clarification/RFI log;
- quantity summary by package/WBS/zone/level;
- audit trail linking every material quantity to its source.

## QA/QC
Before finalizing:
1. confirm latest known revisions;
2. check units and conversions;
3. verify no duplicated scope;
4. check arithmetic/formulas;
5. perform at least one independent reasonableness check for major quantities;
6. reconcile totals to BOQ where applicable;
7. make assumptions and unresolved conflicts visible;
8. confirm the output is measurement-only unless pricing was explicitly requested and routed.

## Stop conditions
Stop and flag the issue instead of guessing when:
- critical dimensions are missing;
- revision status is uncertain;
- drawings conflict materially;
- measurement rules change the result and are unknown;
- image/PDF scale is unreliable;
- scope ownership/interface cannot be determined.

When possible, state exactly what information is needed to continue.
