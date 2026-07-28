# Planning control workbook specification

## Purpose

This specification defines an import-friendly, reviewable workbook for building and controlling Planning & Primavera P6 Agent inputs and outputs. It is not a substitute for the controlled P6 database or the contractual schedule file.

## Workbook controls

- Freeze a unique `Project_ID`, `Schedule_ID`, `Schedule_Version`, `Data_Date`, `Time_Zone`, `Source_Cutoff`, and `Currency` on the Control sheet.
- Never overwrite an approved or previously issued version. Copy forward into a new version and record the change reason.
- Use stable identifiers. Names may change; WBS, activity, relationship, calendar, resource, package, submittal, drawing, event, and scenario IDs must not be recycled.
- Store P6 durations and lags in hours. Display conversions may use the assigned calendar, never a universal hours-per-day assumption.
- Use ISO 8601 dates/times and an explicit IANA time zone.
- Use decimal numbers without thousands separators in exchange tables.
- Keep formula cells distinct from controlled input cells and protect validated formulas.
- Do not use merged cells, hidden rows, color alone as meaning, or formulas in import CSV extracts.

## Required sheets

| Order | Sheet | Purpose | Primary key |
|---:|---|---|---|
| 1 | Control | Project, version, data date, time zone, basis, approvals | `Schedule_ID + Schedule_Version` |
| 2 | Sources | Document and schedule provenance | `Source_ID` |
| 3 | WBS | Hierarchy, ownership, scope boundary | `WBS_ID` |
| 4 | Activities | Activities, milestones, durations, dates, status, codes | `Activity_ID` |
| 5 | Relationships | Predecessor/successor logic and rationale | `Relationship_ID` |
| 6 | Calendars | Workweek, shifts, holidays, and exceptions | `Calendar_ID` |
| 7 | Resources | Labor, plant, and nonlabor dictionary | `Resource_ID` |
| 8 | Resource Assignments | Budgeted and remaining units by activity | `Assignment_ID` |
| 9 | Cost Loading | CBS allocation and activity costs | `Cost_Assignment_ID` |
| 10 | Cash Flow | Periodized cost, billing, retention, advance, and net cash | `Period_ID + Scenario_ID` |
| 11 | Procurement | Package lifecycle and required-on-site control | `Package_ID` |
| 12 | Material Submittals | Material approval and delivery cycle | `Submittal_ID` |
| 13 | Shop Drawings | Design production and approval cycle | `Drawing_ID` |
| 14 | Progress Update | Status evidence, actuals, remaining work, and forecast | `Activity_ID + Data_Date` |
| 15 | Delay Events | Event chronology, notice, cause, effect, and evidence | `Delay_Event_ID` |
| 16 | Recovery Actions | Scenario changes, feasibility, cost, and approvals | `Recovery_Action_ID` |
| 17 | TIA Fragnet | Inserted activities and relationships for one impact event | `TIA_ID + Fragnet_Row_ID` |
| 18 | QA Checks | Structural, CPM, calendar, progress, resource, cost, and exchange checks | `Check_ID` |
| 19 | Registers | Assumptions, constraints, gaps, changes, and actions | `Register_Item_ID` |

## Validation requirements

- All foreign keys must resolve to active records in the same controlled version.
- WBS must form one valid hierarchy without duplicate codes or orphan nodes.
- Activities must use defined WBS and calendar IDs; milestones have zero duration.
- Relationships must not self-reference or form cycles; non-FS logic, lags, and constraints require rationale.
- Baseline networks must have justified starts/finishes and no unexplained open ends.
- Actual starts cannot be after actual finishes; actual data must be supported by a source reference.
- Costs must reconcile to the approved CBS control total before cash-flow generation.
- Procurement, submittal, and drawing dates must link backward from an activity or approved required-on-site/need date.
- Delay, recovery, and TIA models must reference an immutable source schedule and identify every inserted, deleted, or changed record.
- XER or P6 XML exports require schema checks, import into a test environment, rescheduling, and round-trip comparison before release.

## Formula policy

Deterministic engines—not language-model arithmetic—calculate CPM dates, float, resource demand, earned or remaining units, time-phased cost, payment timing, cash flow, and impact deltas. Workbook formulas must be documented, independently testable, and reconciled to controlled totals.
