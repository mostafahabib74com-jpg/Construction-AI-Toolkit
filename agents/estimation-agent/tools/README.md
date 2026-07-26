# Estimation Agent tools

No runtime tools are implemented in this milestone. Future tools must be explicit, deterministic where numerical, permission-controlled, versioned, and independently testable.

## Required tool families

- Document and OCR parser.
- Spreadsheet parser and workbook generator.
- Unit and currency normalization.
- Quantity and rate calculation engine.
- BOQ and CBS mapper.
- Quotation normalization and comparison engine.
- Risk calculation engine.
- Document generator for DOCX/PDF deliverables.
- Bid-package manifest and reconciliation validator.

The agent must never imply that a tool ran when it did not. Tool output must be stored with execution ID, version, inputs, results, warnings, and validation status.
