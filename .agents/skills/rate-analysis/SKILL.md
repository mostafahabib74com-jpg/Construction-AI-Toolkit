---
name: rate-analysis
description: Build transparent construction unit-rate analyses from verified quantities, resource consumption, productivity, supplier/subcontractor inputs, indirects, risk, and markup without inventing missing prices.
---

# Rate Analysis

## Purpose
Develop traceable unit-rate build-ups for construction work and make the cost logic auditable from resource inputs through final selling rate.

## Trigger
Use for unit-rate analysis, cost build-up, price analysis, subcontract comparison, material/labor/equipment breakdown, productivity-based pricing, tender pricing support, or variation/new-rate assessment.

## Inputs
Use available evidence such as:
- BOQ item description and unit;
- drawings/specifications/scope;
- quantity-takeoff outputs;
- material quotations;
- labor wages/cost rates;
- equipment ownership/rental rates;
- subcontractor quotations;
- productivity assumptions backed by project data or stated estimating assumptions;
- waste/loss factors;
- logistics, mobilization, access, temporary works, testing, supervision, and other direct requirements;
- project commercial rules for overhead, profit, contingency, taxes, bonds, retention, or other markups where applicable.

## Workflow
### 1. Define the priced item
Confirm exact scope boundary, unit of measure, inclusions, exclusions, location/conditions, specification, and whether the rate is supply-only, install-only, or supply-and-install.

### 2. Confirm quantity basis
Use the governing measurable unit. Where `quantity-takeoff` outputs exist, reconcile the priced item to them. Do not bury quantity uncertainty inside the rate.

### 3. Build resource model
Identify all resources required per unit:
- materials;
- labor trades/crew;
- equipment/plant;
- subcontract services;
- consumables;
- temporary works;
- testing/inspection;
- logistics and handling;
- direct supervision where appropriate.

### 4. Establish consumption and productivity
For each resource state:
- consumption or production basis;
- productivity;
- working hours/shifts where relevant;
- waste/loss allowance;
- conversion factors;
- source or assumption.

For crew-based work:
`Labor cost per unit = Crew cost per time period / Crew production per time period`

For equipment:
`Equipment cost per unit = Equipment cost per time period / Production per time period`

For materials:
`Material cost per unit = Net consumption × (1 + justified allowance) × delivered material rate`

### 5. Normalize quotations
Check currency, unit, delivery basis, taxes, validity, minimum order, lead time, exclusions, installation content, and commercial conditions before comparing quotations.

### 6. Calculate direct unit cost
Sum all direct resource costs attributable to one BOQ unit. Keep subtotals visible by material, labor, equipment, subcontract, and other direct cost.

### 7. Add project-specific indirects
Only add indirects where the pricing basis requires them. Examples may include:
- site overhead allocation;
- mobilization/demobilization;
- temporary facilities;
- permits;
- safety/QA/QC burden;
- engineering/submittals;
- bonds/insurance;
- financing/cash-flow cost.

State the allocation basis clearly.

### 8. Add risk/contingency and commercial markup
Keep these separate from base cost. Apply contingency/risk only when justified and document the basis. Keep overhead and profit distinguishable where possible.

### 9. Derive selling rate
Use an explicit build-up, for example:
`Selling rate = Direct cost + Allocated indirects + Risk/contingency + Overhead + Profit + applicable commercial additions`

Do not add VAT or any tax automatically unless the task/project basis requires it.

### 10. Benchmark and challenge
Compare the result, where evidence exists, against:
- supplier/subcontractor quotations;
- historical/project rates;
- alternative methods;
- sensitivity to productivity and key material prices.

Investigate material variances instead of forcing the result toward a target.

### 11. Deliver rate-analysis package
Provide the build-up, assumptions, quotation references, sensitivity/risk notes, and final recommended pricing basis.

## Core controls
- Never invent supplier prices, wages, rental rates, or productivity.
- Label every unverified input as an assumption.
- Do not mix BOQ quantity errors with unit-rate build-up.
- Avoid double-counting overhead, waste, preliminaries, logistics, or profit.
- Distinguish net consumption from procurement allowance.
- Normalize quotations before comparison.
- Keep direct cost, indirect cost, contingency, overhead, profit, and taxes separate.
- For subcontract quotations, identify whether materials, plant, supervision, testing, mobilization, and wastage are included.
- For remeasurable work, ensure the unit rate is compatible with the measurement rule.

## Deliverables
Depending on the request:
- detailed unit-rate analysis;
- resource consumption table;
- crew/productivity build-up;
- supplier/subcontract comparison;
- quotation normalization sheet;
- sensitivity analysis;
- pricing assumptions and exclusions;
- final pricing recommendation/basis;
- list of missing inputs that materially affect the rate.

## QA/QC
Before finalizing:
1. confirm BOQ unit and scope;
2. verify arithmetic and unit conversions;
3. check consumption/productivity logic;
4. confirm quotation units and commercial basis;
5. check no cost element is duplicated;
6. separate base cost from markups;
7. test sensitivity of major cost drivers;
8. confirm assumptions are visible;
9. reconcile with quantity-takeoff/tender-management where applicable.

## Stop conditions
Do not present a defensible final rate as verified when major price/productivity inputs are missing. Instead:
- identify the missing inputs;
- calculate only verified portions where useful;
- provide a provisional range only if the user explicitly requests it and the assumptions are stated;
- prepare RFQs/clarifications when external evidence is required.
