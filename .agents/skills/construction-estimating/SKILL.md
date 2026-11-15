---
name: construction-estimating
description: Compile a construction estimate from verified quantities and unit rates, including direct cost, project indirects, risk, commercial adjustments, and final bid price with full traceability.
---

# Construction Estimating

## Purpose
Build a complete, auditable construction estimate from scope and quantities through unit rates, project indirects, risk, commercial adjustments, and final selling price.

## Trigger
Use for tender estimate compilation, project cost estimate, BOQ pricing, cost plan, bid price build-up, estimate reconciliation, estimate review, or estimate-at-completion preparation.

## Inputs
Use all relevant available evidence:
- tender/RFQ/RFP documents;
- BOQ and quantity-takeoff outputs;
- drawings/specifications/scope;
- rate-analysis outputs;
- supplier/subcontractor quotations;
- construction programme and duration assumptions;
- site logistics and mobilization requirements;
- staffing/resource plan;
- temporary works;
- project commercial conditions;
- contract risk review;
- taxes and statutory/commercial additions where applicable;
- client pricing forms and submission templates.

## Skill coordination
This skill should coordinate rather than duplicate specialist work:
- use `tender-management` for document/scope/risk review;
- use `quantity-takeoff` for measured quantities and reconciliation;
- use `rate-analysis` for unit-rate build-ups;
- use `contract-management` for contractual/commercial risk when available;
- use `primavera-p6` for duration/resource/cash-flow logic when available.

If a dependent skill is unavailable, state the manual assumption or unresolved dependency explicitly.

## Workflow
### 1. Define estimate basis
Confirm:
- estimate purpose and stage;
- currency;
- pricing date;
- BOQ version/revision;
- measurement basis;
- project duration;
- location/site conditions;
- scope boundary;
- exclusions;
- tax basis;
- required selling-price structure.

### 2. Establish estimate register
Create a register of:
- BOQ items/packages;
- quantities and quantity source;
- rate source;
- quotation source;
- status: verified / assumed / provisional / excluded / pending;
- key dependencies and clarifications.

### 3. Validate scope and quantities
Reconcile the estimate against tender-management and quantity-takeoff outputs. Do not price only the BOQ if drawings/specifications/conditions identify additional scope.

### 4. Assign unit rates
For each measurable item:
- use an approved/verified rate-analysis where available;
- otherwise identify the rate source;
- do not invent unsupported unit rates;
- distinguish supplier, subcontract, historical, budget, and analytical rates;
- record quotation validity and commercial basis.

### 5. Calculate direct works cost
For each item:
`Amount = Quantity × Unit Rate`

Summarize direct cost by useful package/WBS/discipline such as:
- civil/structural;
- architectural;
- MEP;
- external works;
- specialist systems;
- temporary works;
- testing/commissioning where directly attributable.

### 6. Build project preliminaries and site indirects
Estimate time-related and fixed project costs separately.

Typical categories may include:
- project/site management staff;
- site offices and facilities;
- temporary utilities;
- HSE and QA/QC;
- security;
- mobilization/demobilization;
- access/logistics;
- cranes/hoists/shared plant;
- surveying;
- permits and site services;
- insurance/bonds where project-specific;
- temporary works not included in item rates;
- testing/commissioning support;
- document control/submittals;
- closeout/handover.

For time-related costs:
`Time-related cost = Monthly/weekly cost × justified project duration`

Do not duplicate indirects already embedded in unit rates.

### 7. Add procurement/logistics allowances
Account for freight, unloading, storage, long-lead handling, minimum order effects, import duties/customs only where relevant and evidenced, and procurement risks not already in rates.

### 8. Price risk and contingency
Create an explicit risk allowance rather than hiding risk inside arbitrary rate increases.

Where risk is quantifiable:
`Expected risk allowance = Probability × Cost impact`

Use scenario/range analysis where probability is not defensible. Separate:
- known scope cost;
- provisional sums;
- contingency;
- escalation where contract/project basis allows;
- unresolved commercial/technical risks.

### 9. Add corporate overhead and profit
Keep corporate overhead and profit visible according to the company pricing policy.

When percentages are used, state whether they are:
- markup on cost; or
- target gross margin on selling price.

Do not use markup and margin interchangeably. Follow the formulas defined in `rate-analysis`.

### 10. Apply commercial adjustments
Only apply items supported by the project basis, such as:
- discounts;
- bonds/guarantee costs;
- financing/cash-flow cost;
- retention financing;
- payment-term impact;
- price escalation;
- taxes/VAT;
- client-specific commercial requirements.

Keep each adjustment separately visible.

### 11. Compile selling price
A typical transparent structure is:

`Direct works cost`
`+ project preliminaries/site indirects`
`+ procurement/logistics additions`
`+ quantified risk/contingency`
`+ corporate overhead`
`+ profit`
`+ applicable commercial/tax adjustments`
`= final selling price`

Do not force the estimate to a target price without documenting the commercial adjustment separately.

### 12. Reconcile and benchmark
Check:
- BOQ total vs estimate total;
- estimate by discipline/package;
- major rate drivers;
- major quantity drivers;
- subcontract coverage;
- supplier coverage;
- price per m² / unit / key project metric when meaningful;
- sensitivity to duration, productivity, major material prices, and risk.

### 13. Final estimate review
Identify:
- unpriced items;
- provisional/assumed rates;
- pending quotations;
- scope gaps;
- duplicated cost;
- missing indirects;
- missing commercial costs;
- arithmetic/formula errors;
- high-sensitivity items;
- unresolved tender clarifications.

### 14. Deliver estimate package
Provide:
- estimate summary;
- detailed BOQ pricing;
- indirect/preliminaries build-up;
- quotation register;
- assumptions/exclusions;
- risk/contingency register;
- commercial adjustments;
- final selling-price bridge;
- estimate QA/QC report.

## Core controls
- Never invent quantities, supplier prices, rates, productivity, or contract terms.
- Separate quantity uncertainty from rate uncertainty.
- Separate direct cost from indirects, contingency, overhead, profit, and taxes.
- Avoid double-counting preliminaries, logistics, waste, supervision, bonds, or temporary works.
- Preserve quotation source, date, validity, currency, and scope.
- Distinguish verified, assumed, provisional, and excluded costs.
- Reconcile estimate scope against all available tender documents, not BOQ alone.
- Keep formulas and units auditable.
- Highlight large unsupported allowances rather than burying them.

## Deliverables
Depending on the request:
- priced BOQ;
- estimate summary by discipline/package/WBS;
- unit-rate source register;
- quotation comparison/register;
- preliminaries/site-indirects build-up;
- risk/contingency build-up;
- overhead/profit bridge;
- cash-flow-related commercial adjustments;
- assumptions/exclusions;
- estimate reconciliation and QA/QC;
- final client-facing price summary when requested.

## QA/QC
Before finalizing:
1. confirm latest known source revisions;
2. confirm all BOQ items have a price/status;
3. reconcile quantities to `quantity-takeoff`;
4. reconcile rates to `rate-analysis` or a stated source;
5. verify formulas, units, extensions, and totals;
6. check no duplicated cost;
7. verify preliminaries against duration;
8. review risk and contingency separately;
9. verify markup/margin basis;
10. reconcile technical scope and commercial price;
11. list all provisional/assumed/pending inputs;
12. perform at least one benchmark/sensitivity review.

## Stop conditions
Do not label an estimate as final/verified when major scope, quantity, rate, duration, or commercial inputs are unresolved. Instead:
- identify missing inputs;
- quantify only verified portions where useful;
- classify provisional allowances explicitly;
- prepare clarification/RFQ actions;
- show the effect on total price or risk range where defensible.
