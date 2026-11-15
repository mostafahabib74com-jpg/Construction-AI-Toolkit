# Hierarchical BOQ intake follow-up

Real workbook intake exposed layouts that need explicit handling: scope headings mixed with priced rows, composite items with one vertically merged quantity and separate description rows, common Arabic headers and engineering units, and a distinction between blank prices and zero cost.

## Delivered controls

- Add opt-in preparation under the BOQ import column mapping. Both preparation options default to off.
- Combine a composite item only when item code and quantity share the same vertical merged span. Preserve every component description, original source row and cell data; use the quantity once. Reject conflicting units instead of allocating or duplicating quantity.
- Let users review section/scope headings and total rows before excluding them from measurable items. Keep coded incomplete items as incomplete. Carry source scope context into BOQ raw evidence, draft activity notes and estimate evidence.
- Recognize the Arabic work-description header and common linear-meter, set and lump-sum labels while retaining source units for display.
- Preserve estimate source evidence through item edits and show a compact unpriced-item count instead of an apparent zero-value final estimate.
- Support project/workspace deep links and explicitly label import-only trial projects with placeholder setup metadata. No dates, prices, productivity or crew values are inferred from a BOQ.

## Validation

The complete Windows/Python 3.12 suite passed **185 tests**. Added tests cover opt-in behavior, combined-row provenance, one shared quantity, missing quantity retention, conflicting units, source scope retention, Arabic header/unit recognition and direct project navigation.

A private intake trial preserved the source workbook unchanged and reconciled every nonblank source row to an imported item, an excluded structural row or a documented composite continuation. All resulting measured items passed the application's field/unit validation. Both the estimate's final price and actual schedule remained unavailable until required user inputs are supplied. Source files, client quantities, pricing and trial databases are excluded from the public repository.
