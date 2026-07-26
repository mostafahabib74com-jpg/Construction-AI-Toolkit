# Phase 8 Milestone 2 — Deterministic Scheduling Engine

## Delivered

Milestone 2 turns the intake application into a working forward-scheduling tool while preserving the existing agents, prompts, workflows, contracts, and Milestone 1 features.

The implementation adds application contracts and normalized SQLite records for schedule workspaces, WBS nodes, calendars, activities, relationships, and immutable runs. Exact quantities, productivity rates, lag, and duration values use decimal text at persistence boundaries.

The domain engine provides:

- quantity/productivity/crew duration formulas for per-day and per-hour productivity;
- time-zone-aware working intervals, breaks, weekly patterns, and date exceptions;
- a shared deterministic graph implementation for cycle detection and topological ordering;
- FS, SS, FF, and SF forward constraints;
- successor-calendar signed lag;
- planned early start and finish dates; and
- signed calendar-day variance against the required completion date.

## Safety behavior

Calculation is blocked when a task lacks an explicit positive quantity, productivity rate, productivity basis, crew count, WBS, or calendar. The system also blocks broken relationship endpoints, self-links, duplicate relationships, WBS cycles, and activity-logic cycles. Negative lag is allowed only with a visible planner-review warning.

BOQ conversion is user-triggered, accepts validated rows only, and does not populate productivity, crews, WBS, calendar, or relationships. Split activities deliberately receive no allocated quantity.

## Application workflow

The Streamlit schedule workspace provides Overview, WBS, Calendars, Activities, Relationships, and Calculate & review tabs. A successful calculation creates a new immutable run and leaves previous runs in SQLite for traceability.

## Explicitly excluded

This milestone does not implement Gantt visualization, Excel/CSV/Primavera export, backward-pass CPM, total/free float, critical path, resource loading, cost loading, cash flow, or any Estimation, Tender, Contracts, BIM, or other platform screen.

## Demonstration data

`apps/scheduling-mvp/sample_data/milestone_2_demo_schedule.json` is synthetic and clearly marked. Automated tests load it into an isolated temporary database; the application never injects it into user projects.
