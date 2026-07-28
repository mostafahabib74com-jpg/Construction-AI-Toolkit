# CPM and logic

CPM calculations require a validated scheduling engine. The agent may propose or review logic but cannot calculate dates or float mentally.

## Logic controls

- Except authorized project start/finish nodes, activities should have valid predecessors and successors.
- Finish-to-start is preferred where it represents the work; SS/FF relationships require clear physical rationale.
- Leads are discouraged and require approval. Lags require documented rationale and should be replaced by explicit activities when they represent work or waiting that must be monitored.
- Constraints must reflect a real requirement and cannot be used to conceal missing logic.
- Calendars, relationship-lag calendars, scheduling options, retained logic/progress override, and out-of-sequence settings materially affect results and must be recorded.
- Critical and longest path are calculated according to approved project settings. Float ownership and contractual interpretation are not assumed.

## Validation

Review missing logic, loops, redundant logic, dangling paths, excessive lags, unusual relationship types, constraints, long activities, negative/high float, invalid dates, excessive criticality, and discontinuous paths using configured thresholds.
