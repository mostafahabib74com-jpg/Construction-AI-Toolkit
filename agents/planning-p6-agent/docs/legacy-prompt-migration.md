# Legacy Primavera P6 prompt migration

The repository's legacy Primavera P6 prompts remain educational source material. They are not workflow contracts and must not be used as autonomous production instructions. Migrate their intent as follows.

| Legacy topic | Controlled destination | Required upgrade |
|---|---|---|
| WBS creation | `wbs-development` | Scope traceability, code uniqueness, dictionary, ownership, coverage, review gates |
| Baseline schedule | `baseline-schedule-generation` | Approved upstream artifacts, explicit P6 settings, deterministic CPM, quality report, round-trip control |
| Activity and logic | `activity-list-development` + `relationship-assignment` | Duration basis, calendars, logic rationale, lag/constraint controls, open-end and loop checks |
| Resource loading | `resource-loading` | Resource dictionary, units, productivity provenance, availability, histogram, overallocation report |
| Cost loading | `cost-loading` | CBS mapping, currency/base date, allocation basis, activity/WBS/control-total reconciliation |
| Cash flow | `cash-flow` | Payment terms, advance/retention/tax timing, gross/net separation, deterministic periodization |
| Procurement schedule | `procurement-schedule` + material/shop-drawing workflows | Backward planning from need dates, approval/manufacture/logistics stages, P6 links, risk register |
| Recovery schedule | `recovery-schedule` | Immutable history, multiple feasible options, resource/cost/HSE/QA effects, implementation approval |
| EOT/delay | `delay-analysis` + `time-impact-analysis` | Contemporaneous evidence, declared methodology, fragnet audit trail, sensitivity, entitlement boundary |
| Progress update | `progress-update` | Fixed data date, verified actuals, remaining-duration basis, out-of-sequence policy, variance and QA |

## Migration rule

Do not copy a legacy prompt verbatim into orchestration. Extract the useful planning intent, bind it to the agent system prompt and shared controls, validate its inputs/outputs against the workflow schemas, apply the relevant knowledge profile, and require the named professional reviewers.

Legacy files may be deprecated only after coverage is confirmed and repository maintainers approve the change. This milestone does not remove or alter them.
