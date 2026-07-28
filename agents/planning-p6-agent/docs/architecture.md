# Planning & P6 Agent architecture

```text
Controlled scope and contract requirements
        |
WBS -> activity list -> calendars and logic -> baseline schedule
        |
Resources -> costs -> cash flow
        |
Design/procurement/submittal/shop-drawing integration
        |
Progress updates -> variance and delay analysis
        |
Recovery scenarios and Time Impact Analysis
```

The prompt layer defines planning behavior. Workflow contracts define inputs, outputs, tools, blockers, and review. The knowledge layer defines schedule concepts and configurable profiles. Deterministic services will calculate CPM, resource/cost time phasing, schedule quality, recovery, and TIA. The evidence layer preserves source and revision provenance. The review layer preserves planner, construction, procurement, design, cost, and contract authority.

Approved schedules are immutable. Every downstream schedule is a new version linked to its parent with a complete variance record.
