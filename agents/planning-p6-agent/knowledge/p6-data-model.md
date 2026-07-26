# Primavera P6 data model

The schedule model must preserve, where available:

- EPS/project identifiers, project name, data date, planned start, must-finish date, default calendar, and scheduling options.
- WBS hierarchy, codes, names, descriptions, responsible managers, and sequence.
- Activities, activity types, durations, percent-complete types, status, dates, constraints, calendars, codes, notebooks, steps, and UDFs.
- Relationships with predecessor, successor, type, lag, and calendar basis.
- Calendars with workweek, hours per day/week/month/year, holidays, exceptions, shifts, and time zones.
- Resources, roles, units/time, rates, availability, assignments, curves, and leveling priorities.
- Expenses, costs, currencies, price/unit, budgeted/actual/remaining units, and earned-value settings.
- Baselines, layouts, filters, thresholds, issues, risks, and project preferences when supported.

Import and export must preserve stable identifiers and unknown supported fields. Round-trip comparison is required before a generated XER/XML artifact can be trusted.
