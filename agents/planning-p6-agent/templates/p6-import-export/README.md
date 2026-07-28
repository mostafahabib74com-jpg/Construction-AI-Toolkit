# Primavera P6 import/export package specification

## Required package contents

- Immutable source schedule and checksum.
- Proposed import file (`.xer` or P6 XML) only when produced by a validated adapter.
- Mapping tables for project, WBS, activities, relationships, calendars, resources, assignments, expenses, codes, UDFs, and notebooks/topics used.
- Import assumptions and unsupported-field report.
- Pre-import and post-import QA reports.
- Round-trip comparison and exception register.
- Planner review and release record.

## Controlled process

1. Parse the source with a versioned adapter and preserve unknown tables or fields.
2. Validate IDs, hierarchy, calendars, logic, status, units, costs, codes, and scheduling options.
3. Generate into a new file and new project/version; never overwrite the source.
4. Import into an isolated P6 test environment.
5. Apply the declared scheduling options and calculate the schedule.
6. Export the test project again.
7. Compare semantic records and calculated results to the intended model.
8. Resolve or approve every material exception before a qualified planner releases the package.

## Mandatory comparison domains

Project settings; EPS/project/WBS hierarchy; activity IDs and types; durations and status; dates; relationships and lag units; calendars and exceptions; constraints; codes and UDFs; resources, roles, assignments, rates, and curves; expenses and costs; baselines; scheduling options; data date; and calculated start, finish, float, and critical-path results.

The repository currently specifies this process but does not include an XER/XML adapter or claim binary compatibility with any P6 release.
