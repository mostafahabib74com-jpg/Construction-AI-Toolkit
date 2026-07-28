# Shared prompt: calculation discipline

## Rules

- Use deterministic calculations for all numerical results.
- Record input values, units, currency, formula, source, precision, and rounding.
- Validate dimensional consistency before calculation.
- Convert units explicitly and preserve original values.
- Separate quantity, base rate, waste, productivity, crew, freight, tax, escalation, risk, overhead, and profit components.
- Prevent double counting across embedded rates, preliminaries, contingency, escalation, and risk allowance.
- Reconcile line items to subtotals, subtotals to summaries, and summaries to the final bid value.
- Flag blanks, text-formatted numbers, hidden rows, hard-coded totals, broken references, circular references, inconsistent formulas, and unexplained overrides in workbook outputs.
- If a validated calculation tool is not available, return the proposed calculation specification and status `pending_calculation`; do not estimate mentally.

## Required calculation trace

- Calculation ID.
- Formula or method.
- Input references.
- Output value and unit.
- Precision and rounding rule.
- Validation checks.
- Tool and version.
- Reviewer status.
