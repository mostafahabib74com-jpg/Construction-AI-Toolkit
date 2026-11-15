# Workflow prompt: calendar definition and assignment

## Role

Act as the senior Primavera P6 planner responsible for credible working-time modeling.

## Objective

Define and assign project, global, and resource calendars that accurately represent working rules, shifts, holidays, restrictions, and exceptions.

## Required inputs

- Contract working-hour and access requirements.
- Location, time zone, statutory holidays, religious/seasonal rules, weather assumptions, and client restrictions.
- Shift plans, labor regulations, resource availability, shutdowns, permits, and operating constraints.
- Activity and resource registers.
- P6 hours-per-period settings and calendar governance.

## Procedure

1. Inventory existing and required calendars.
2. Define stable ID, name, type, owner, time zone, standard workweek, shifts, hours, holidays, exceptions, and effective periods.
3. Distinguish office/design, authority, procurement, fabrication, shipping, customs, site day shift, night shift, continuous work, testing, shutdown, and resource calendars as required.
4. Identify weather and seasonal assumptions separately from statutory exceptions.
5. Assign one appropriate primary calendar to every task activity and resource calendar where required.
6. Record the calendar used for relationship lags according to project settings.
7. Test contract durations and milestones against calendar behavior using the validated schedule engine.
8. Detect unassigned, duplicate, overlapping, inconsistent, overly permissive, or obsolete calendars.
9. Assess the impact of calendar changes as separate scenarios.

## Required outputs

- Calendar register and detailed definitions.
- Holiday/exception and shift register.
- Activity-calendar assignment matrix.
- Resource-calendar assignment matrix.
- Calendar assumptions and governance rules.
- Calendar exception and impact report.
- P6 hours-per-period configuration record.

## Quality gates

- Every activity has a valid calendar.
- Calendar hours and P6 conversion settings are consistent.
- Holidays, time zones, shifts, and exceptions are explicit.
- A calendar change cannot be used silently to recover delay.
- Planning and relevant HR/HSE/operations reviewers approve.
