# Prompt catalog

Every workflow prompt is a controlled planning instruction, not a free-form request. Apply `system.md`, all prompts in `shared/`, the workflow prompt, the selected knowledge profile, and the workflow schemas together.

## Schedule construction

- `wbs-development`: scope-complete WBS, dictionary, coding, and coverage checks.
- `activity-list-development`: measurable activities, milestones, durations, and traceability.
- `calendar-assignment`: workweeks, holidays, shifts, exceptions, and activity assignments.
- `relationship-assignment`: CPM logic, interfaces, lags, constraints, and open-end checks.
- `baseline-schedule-generation`: controlled baseline assembly, CPM validation, and P6 exchange package.

## Time-phased controls

- `resource-loading`: labor, plant, nonlabor, availability, and histograms.
- `cost-loading`: CBS allocation, reconciliation, and cost-loaded schedule.
- `cash-flow`: gross/net cash flow, payment mechanics, curves, and reconciliation.

## Design and procurement

- `procurement-schedule`: package cycle from strategy to required-on-site date.
- `material-submittal-schedule`: technical submittal, review, resubmission, release, and delivery.
- `shop-drawing-schedule`: production, coordination, review, resubmission, and construction release.

## Updating and analysis

- `progress-update`: verified actuals, remaining work, out-of-sequence handling, and forecast.
- `delay-analysis`: method selection, chronology, critical path, and evidence limitations.
- `recovery-schedule`: feasible recovery options, resource/cost effects, and implementation controls.
- `time-impact-analysis`: contemporaneous model selection, fragnet, impact test, and sensitivity.

No prompt authorizes baseline approval, progress certification, entitlement determination, historical-data rewriting, or direct publication to production P6.
