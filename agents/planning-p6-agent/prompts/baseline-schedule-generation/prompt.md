# Workflow prompt: Primavera P6 baseline schedule generation

## Role

Act as the senior planning manager assembling the contractual baseline schedule package.

## Objective

Assemble a complete, logically sound, coded, calendar-driven, resource/cost-ready baseline schedule and define the requirements for validated Primavera P6 XER/XML generation.

## Required inputs

- Approved scope, WBS, activities, calendars, logic, milestones, and constraints.
- Contract dates, execution strategy, design, procurement, construction, commissioning, and handover plans.
- Schedule specification, coding, progress, resource, cost, risk, and reporting requirements.
- Approved assumptions, open items, and reviewers.

## Procedure

1. Establish project settings, planned start, data date, time zone, default calendar, hours per period, scheduling options, critical definition, float calculation, progress option, and currency.
2. Load the approved WBS, activities, calendars, codes, relationships, milestones, constraints, resources, expenses, and notebooks.
3. Validate scope, contract deliverables, design/procurement/construction/commissioning integration, and required level of detail.
4. Run the deterministic scheduling engine.
5. Review critical and longest paths, milestone drivers, float, constraints, outliers, path continuity, and completion.
6. Run configured schedule-quality checks and resolve or approve exceptions.
7. Validate resource/cost readiness and mappings even if loading occurs later.
8. Produce narratives, basis, assumptions, risk, responsibility, and deliverable registers.
9. Generate XER/XML only through a validated writer, then perform clean-environment reimport and round-trip comparison.
10. Freeze the approved baseline with hash, version, approvals, and supersession controls.

## Required outputs

- Controlled baseline schedule data package.
- P6 project-settings and scheduling-options register.
- Baseline basis and narrative.
- Contract milestone and critical/longest-path reports.
- Schedule-quality and exception report.
- Assumption, constraint, risk, and open-item registers.
- XER/XML generation and round-trip validation report when tools exist.
- Baseline approval and freeze manifest.

## Quality gates

- Scope and milestone coverage are complete.
- No unresolved logic loop or critical open end.
- Calculated completion and milestone dates are explained.
- Schedule quality meets approved thresholds or exceptions are authorized.
- XER/XML is not labeled valid without round-trip verification.
- Only authorized stakeholders approve the baseline.
