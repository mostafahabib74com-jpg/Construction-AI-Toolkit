# Professional Excel cost-model specification

## Purpose

Define a controlled workbook that can be generated from approved Estimation Agent data. This specification does not create the workbook engine; it defines the required sheets, formulas, controls, presentation, and verification behavior.

## Workbook principles

- Separate input, calculation, control, and presentation sheets.
- Never place an unexplained hard-coded value inside a calculated result.
- Use stable item IDs, named tables, structured references, validation lists, protected formulas, and visible input cells.
- Preserve original quotation currencies and units alongside normalized values.
- Provide formula traceability from final bid value to source quantity and rate.
- Use no macros in the default workbook.
- Keep a visible change log and estimate metadata sheet.
- Make error, missing-data, and reconciliation conditions prominent.

## Required sheets

1. `00_Cover_Control` — document metadata, version, status, preparer, reviewers, approvals, pricing date, currency, unit system, and revision history.
2. `01_Instructions` — workbook conventions, color legend, input rules, and warnings.
3. `02_Source_Register` — documents, drawings, addenda, quotations, rates, and revision status.
4. `03_Assumptions` — assumptions, exclusions, qualifications, allowances, and approvals.
5. `04_RFP_Requirements` — requirement and compliance matrix.
6. `05_Scope_Matrix` — included, excluded, by-others, optional, provisional, and unresolved scope.
7. `06_BOQ` — BOQ hierarchy, quantities, units, rates, extensions, source, and confidence.
8. `07_CBS_Map` — BOQ-to-CBS/WBS/work-package mapping.
9. `08_Labor_Buildups` — crews, wage components, hours, productivity, allowances, and unit labor cost.
10. `09_Material_Buildups` — base price, waste, freight, duties, handling, testing, and unit material cost.
11. `10_Plant_Buildups` — rental/ownership, operator, fuel, maintenance, mobilization, utilization, and unit plant cost.
12. `11_Subcontract_Quotes` — normalized bidder coverage and evaluated price.
13. `12_Rate_Buildups` — resource composition and unit-rate calculation.
14. `13_Direct_Costs` — direct-cost summary by CBS, WBS, discipline, area, and package.
15. `14_Preliminaries` — time-related and fixed indirect costs.
16. `15_Procurement_Logistics` — long-lead, freight, customs, storage, expediting, and handling allowances.
17. `16_Risk_Opportunity` — risk ranges, treatment, priced allowance, and opportunity status.
18. `17_Escalation_FX_Tax` — indices, periods, currencies, exchange rates, taxes, duties, and calculation basis.
19. `18_Overhead_Profit` — corporate overhead, margin, discounts, and approval limits.
20. `19_Bid_Summary` — base cost through final bid price with inclusion/exclusion labels.
21. `20_Reconciliation` — cross-footing, prior-version variance, quotation coverage, and control checks.
22. `21_Cash_Flow` — optional schedule-based cost and revenue profile.
23. `22_Dashboard` — executive cost, coverage, risk, and readiness indicators.
24. `23_Export` — clean upload/export tables for downstream systems.

## Required controls

- Sum of detailed BOQ extensions equals direct-cost summary.
- CBS and WBS mappings are complete and unique where required.
- Every priced item has a quantity, unit, rate, currency, source type, and confidence.
- Every quotation has validity, inclusions, exclusions, delivery, tax, currency, and normalization status.
- Base cost plus approved adjustments equals final bid price.
- No unapproved critical assumption or risk is hidden from the bid summary.
- No broken, inconsistent, circular, or manually overridden formula remains unresolved.
- All sheets state whether values include or exclude tax.

## Presentation

- Freeze headers and use filters on every data table.
- Use accessible colors with a documented legend.
- Distinguish controlled input, imported input, formulas, approved override, warning, and blocked cells.
- Use consistent number formats for quantities, percentages, dates, currencies, and exchange rates.
- Do not use merged cells inside data tables.
- Print areas, repeating headers, page titles, and PDF export settings must be configured.

## Verification

The generated workbook must undergo structural checks, formula checks, reconciliation checks, and visual review before release. The Estimation Manager approves the pricing model; the agent cannot approve it.
