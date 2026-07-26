# Planning & Primavera P6 Agent

The Planning & Primavera P6 Agent is a specialized project-planning and schedule-analysis module for the Construction-AI-Toolkit AI Engineering Platform.

## Mission

Create, validate, update, and explain complete construction schedules using controlled project evidence and deterministic scheduling calculations, while preserving the authority of qualified planners and contract professionals.

## Supported capabilities

1. WBS development.
2. Activity-list development.
3. Primavera P6 baseline schedule generation specifications.
4. Relationship and logic assignment.
5. Calendar definition and assignment.
6. Resource loading.
7. Cost loading.
8. Cash-flow forecasting.
9. Procurement schedule development.
10. Material-submittal schedule development.
11. Shop-drawing schedule development.
12. Progress updating.
13. Delay analysis.
14. Recovery scheduling.
15. Time Impact Analysis.

## Core principles

- The approved source schedule and each update remain immutable; scenarios are separate versions.
- CPM, dates, float, resource, cost, cash-flow, and delay calculations require validated deterministic engines.
- Every activity, relationship, calendar, constraint, progress value, delay event, and change has provenance.
- Data date, schedule version, calendar, time zone, progress method, and contractual basis are always explicit.
- The agent does not approve baselines, certify progress, determine contractual entitlement, or modify production P6 databases autonomously.
- XER/XML generation is not claimed until a validated parser/writer and round-trip verification exist.

## Maturity

This milestone provides the complete prompt, workflow, schema, template, evaluation, review, and integration specification. It contains no executable P6 parser, scheduler, or file writer.

See `docs/workflow-catalog.md` for the recommended workflow order.

Start with `templates/planning-workbook/WORKBOOK-SPECIFICATION.md` for controlled tabular inputs, `templates/registers/` for canonical CSV headers, and `templates/p6-import-export/README.md` for the P6 round-trip release process.
