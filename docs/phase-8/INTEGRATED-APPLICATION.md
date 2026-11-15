# Integrated local application — 0.3

## Delivered behavior

The integration brings `codex-skills-foundation` into the scheduling application without deleting the original prompt library or specialized agents. The existing five skills remain repository-scoped and inspectable in **Engineering workflows**. The local app does not invoke an external AI provider.

**Planning:** project/BOQ intake, WBS, working calendars with breaks and exceptions, exact duration calculations, FS/SS/FF/SF relationships, signed working-hour lag, early dates, a Gantt chart, CSV/Excel/JSON exports and a shared-calendar CPM backward pass.

**Estimating:** explicit resource consumption and rate inputs, source/date/currency checks, material waste with a stated basis, direct unit costs, quantity extensions, separately justified project indirects/contingency/overhead, markup or gross margin, discount, explicit tax, per-project draft persistence and CSV/Excel/JSON output. BOQ copying imports quantities only and leaves resources unpriced. Unpriced or invalid items block the final selling price.

**Demonstration:** the sidebar demo button creates a separate synthetic project, calculated schedule and synthetic arithmetic estimate. It does not modify an existing project's quantities or prices. The demo estimate deliberately uses 100 cost per unit × 10 units and 25% markup to produce 1,250; these are not market rates.

## Scheduling method and boundaries

All forward relationship lags use the successor calendar. Durations retain exact Decimal values; display rounding does not drive dates. The existing validated forward pass remains the scheduling source of truth.

CPM applies when all activities use one calendar. In that calendar's productive-hour coordinate system, each relation enforces `ES_successor >= ES_predecessor + offset`, where:

| Relation | Offset |
| --- | --- |
| FS | predecessor duration + lag |
| SS | lag |
| FF | predecessor duration + lag − successor duration |
| SF | lag − successor duration |

The backward pass constrains every activity to the calculated project finish and its successors' latest starts. Total float is `LS − ES`; free float is the minimum unused outgoing constraint slack, capped by the common project finish. Critical activities have zero working-hour total float within numerical tolerance. Float is relative to planned finish, not contractual required finish. Contractual variance stays a separate signed calendar-day measure.

Multi-calendar schedules retain early dates but return `CPM_MULTIPLE_CALENDARS` with no float or critical classification. Negative lag remains flagged for planner review. Resource leveling, time-phased cost/resource loading, cash flow, native XER/XML and verified P6 round-trips are not included. Excel is a review workbook, not a certified Primavera import.

## Historical integrity

Migration `004_integrated_workspaces.sql` adds a complete JSON snapshot alongside normalized schedule result records, plus per-project estimate drafts. Each new run snapshots project, calculation settings, WBS, calendars, activities, relationships and results. Deleting an editable activity may cascade its normalized records, but the immutable run snapshot survives unchanged. Display/download labels come from the saved snapshot. Changed inputs trigger a stale-run warning.

Legacy runs without a full input snapshot require recalculation before charting/export. The app never reconstructs missing historical labels from a changed draft. Existing migrations remain unchanged and databases receive the new migration once.

## Export and arithmetic controls

CSV is UTF-8 with BOM and formula-like text is escaped. Excel cells containing user text are explicitly strings, preserving Arabic without executing formulas. Full original inputs remain available in JSON. Calculations retain Decimal precision until final two-decimal money presentation. Labor/equipment time and productivity must use the same period; users enter the resulting resource consumption per BOQ unit. No automatic currency conversion or tax assumption is made.

Source references are recorded, not independently authenticated. Users must review quotation validity, scope, units, minimum hire/shift charges, quantity evidence and allowance duplication before commercial approval.

## Validation

The integrated automated suite passed **176 tests** on Windows with Python 3.12 on 15 November 2026. New coverage includes:

- known parallel-branch critical path and total/free float;
- FS, SS, FF, SF and negative-lag examples;
- explicit withholding of multi-calendar float;
- immutable run/export identity after activity edits and deletion;
- synthetic project-to-schedule-to-export and estimate calculations;
- markup versus margin, tax after discount and the cost bridge;
- missing prices, nonfinite inputs, mixed currency, invalid commercial inputs and waste-basis checks;
- independent per-project estimate persistence;
- Arabic workbook content and formula-neutralized CSV/Excel;
- Streamlit demo creation, Gantt, downloads, estimate and five-skill browser.

A separate workflow trial used the rate-analysis and construction-estimating instructions on synthetic concrete inputs. It produced a direct unit cost of 255, total cost including the supplied allowance of 3,050, selling price of 3,812.50 at 25% markup, and 4,066.67 at 25% gross margin. It identified evidence needed for real tender use and did not fetch or invent market rates.

The browser trial created a separate demo through the actual sidebar, displayed the calculated five-activity schedule and Gantt, and exercised the estimate screen. See the screenshots in this folder when available.

Run the suite from the repository root:

```powershell
python -m pytest -q -p no:cacheprovider -c packages/orchestrator/pyproject.toml
```

Use `START_SCHEDULING_APP.bat` and `STOP_SCHEDULING_APP.bat` on Windows. Python 3.12 and the requirements in `requirements-scheduling-mvp.txt` are required.
