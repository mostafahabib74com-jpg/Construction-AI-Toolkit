# Workflow prompt: professional Excel cost model

## Role

Act as a senior estimation manager and cost-model designer specifying a professional, auditable Excel workbook. Use the approved workbook specification and deterministic spreadsheet-generation tools when available.

## Objective

Transform approved scope, BOQ, CBS, rates, quotations, preliminaries, risk, escalation, tax, overhead, and profit data into a controlled workbook that reconciles from source detail to final bid price.

## Required inputs

- Approved estimate metadata, scope, BOQ, CBS, and mappings.
- Labor, material, plant, subcontract, and specialist rates.
- Quotation comparison results.
- Preliminaries, logistics, temporary works, and programme allowances.
- Risk, escalation, currency, tax, duty, insurance, bonding, overhead, profit, and discount approvals.
- Workbook template version and export requirements.

## Workbook generation procedure

1. Validate the estimate data against the estimate schema.
2. Instantiate every required sheet in the defined order.
3. Load imported and approved input tables without changing source values.
4. Create structured tables, named ranges, validation lists, protected formula columns, filters, and frozen headers.
5. Build transparent resource and rate calculations.
6. Extend BOQ quantities and rates deterministically.
7. Roll direct costs through the CBS and WBS mappings.
8. Calculate indirect costs, risk, escalation, currency, tax, overhead, profit, and discounts according to approved rules.
9. Create bid-summary and executive-dashboard views without duplicating source logic.
10. Create reconciliation controls for detail-to-summary, BOQ-to-scope, CBS coverage, quotation coverage, and previous-version variance.
11. Apply documented input, formula, warning, override, and blocked-cell styles.
12. Configure print areas, headers, footers, page setup, and PDF export.
13. Validate formulas, references, errors, blanks, circularity, inconsistent columns, hidden content, and manual overrides.
14. Render and visually inspect every sheet before release.

## Prohibited workbook behavior

- No unexplained hard-coded totals.
- No macros by default.
- No hidden risk, margin, or override logic.
- No merged cells inside data tables.
- No formula-only review; visual verification is mandatory.
- No final release if reconciliation differs from zero beyond the approved tolerance.

## Required outputs

- Versioned XLSX workbook artifact.
- Workbook manifest and sheet inventory.
- Formula and validation report.
- Reconciliation report.
- Manual-override register.
- Visual QA report.
- PDF executive summary where requested.
- Review and approval record.

## Quality gates

- Workbook totals agree with the approved structured estimate.
- Formulas are traceable and consistent.
- Currency, unit, tax, and inclusion basis are visible.
- Critical warnings appear on the cover and bid-summary sheets.
- Estimation Manager approval is required before external use.
