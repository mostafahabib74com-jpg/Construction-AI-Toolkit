# Register templates

These CSV headers are canonical exchange templates for the planning control workbook. Copy them into a controlled workbook or validated data pipeline; do not edit the canonical headers casually.

## Rules

- Save CSV as UTF-8 with one header row and no formulas.
- Use ISO 8601 dates and explicit schedule version/data date fields.
- Express durations and lags in hours unless a template field explicitly says days.
- Use stable IDs and resolve every foreign key before import.
- Use semicolon-delimited ID lists only where a field is explicitly plural; structured JSON remains preferred for machine exchange.
- Keep blank, zero, not applicable, and unknown distinct.
- Treat the files as blank schemas, not approved defaults or project data.

For workbook controls, validation rules, and release gates, see `../planning-workbook/WORKBOOK-SPECIFICATION.md`.
