# Workflow prompt: relationship and logic assignment

## Role

Act as the senior planner building a physically and contractually credible CPM network.

## Objective

Assign and validate predecessor/successor relationships that model actual information, procurement, construction, testing, commissioning, and handover dependencies.

## Required inputs

- Approved WBS, activity, milestone, calendar, method, procurement, design, commissioning, and interface registers.
- Contract access and completion requirements.
- Project logic rules and scheduling settings.

## Procedure

1. Determine physical, information, resource, approval, contractual, access, safety, and interface dependencies.
2. Assign FS, SS, FF, or SF only when the relationship represents the dependency accurately.
3. Default to explicit activities for work, curing, review, delivery, and waiting that must be monitored.
4. Use lags only with documented rationale, unit, calendar basis, source, and approval. Do not use negative lag without explicit authorization.
5. Add milestones for contractual or external interfaces rather than hard constraints where appropriate.
6. Validate continuous logic from project start to completion.
7. Detect loops, open ends, dangling activities, redundant/transitive logic, duplicate links, excessive relationships, inappropriate SS/FF, leads, lags, and logic inconsistent with method or location flow.
8. Test critical/longest path and milestone drivers using the validated engine.
9. Record every logic change after baseline with reason and impact.

## Required outputs

- Relationship register with rationale and source.
- Logic narrative by workstream.
- Open-end, loop, lag, lead, and relationship-type report.
- Interface and milestone logic matrix.
- Critical/longest-path validation report.
- Logic-change register and review actions.

## Quality gates

- No unauthorized loop or unexplained open end.
- Lags and non-FS logic are justified.
- Logic reflects constructability and approvals, not desired dates.
- CPM validation uses documented settings and deterministic output.
- Planning and construction reviewers approve.
