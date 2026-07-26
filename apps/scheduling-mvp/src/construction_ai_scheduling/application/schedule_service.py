"""Coordinate validation, forward calculation, canonical policy, and immutable runs."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from construction_ai_orchestrator.errors import ContractValidationError
from construction_ai_orchestrator.policies.engine import SCHEDULE, AccuracyPolicyEngine
from construction_ai_orchestrator.validation import SchemaCatalog

from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.schedule_engine import ENGINE_VERSION, calculate_forward_pass
from construction_ai_scheduling.domain.schedule_models import ScheduleRun
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository

from .planning_contracts import SCHEDULE_RUN_SCHEMA, SCHEDULE_WORKSPACE_SCHEMA
from .schedule_adapter import to_canonical_schedule


class ScheduleService:
    def __init__(self, repository: SQLiteRepository, catalog: SchemaCatalog) -> None:
        self.repository = repository
        self.catalog = catalog
        self.policy = AccuracyPolicyEngine(catalog)

    def calculate(self, schedule_id: str) -> ScheduleRun:
        workspace = self.repository.get_schedule(schedule_id)
        project = self.repository.get_project(workspace.project_id) if workspace else None
        if workspace is None or project is None:
            raise SchedulingInputError("Schedule workspace or project was not found.")
        now = datetime.now(timezone.utc)
        wbs_nodes = self.repository.list_wbs_nodes(schedule_id)
        calendars = self.repository.list_calendars(schedule_id)
        activities = self.repository.list_activities(schedule_id)
        relationships = self.repository.list_relationships(schedule_id)
        try:
            calculation = calculate_forward_pass(
                project=project,
                workspace=workspace,
                wbs_nodes=wbs_nodes,
                calendars=calendars,
                activities=activities,
                relationships=relationships,
            )
        except SchedulingInputError as exc:
            run = ScheduleRun(
                f"RUN-{uuid4().hex[:12].upper()}",
                schedule_id,
                ENGINE_VERSION,
                "blocked",
                now,
                None,
                None,
                tuple(exc.issues),
                (),
            )
            return self._save_run(workspace, run)

        canonical = to_canonical_schedule(
            project=project,
            workspace=workspace,
            wbs_nodes=wbs_nodes,
            calendars=calendars,
            activities=activities,
            relationships=relationships,
            results=calculation.results,
        )
        try:
            policy_report = self.policy.evaluate(SCHEDULE, canonical)
            policy_issues = policy_report.issues
        except ContractValidationError as exc:
            policy_issues = (
                {
                    "code": "CANONICAL_SCHEDULE_INVALID",
                    "message": "The calculated schedule could not be mapped to the canonical contract.",
                    "field": "schedule",
                    "severity": "error",
                    "details": exc.details,
                },
            )
        validation_issues = tuple(calculation.validation_issues) + tuple(policy_issues)
        status = "blocked" if any(item.get("severity", "error") == "error" for item in validation_issues) else "calculated"
        run = ScheduleRun(
            run_id=f"RUN-{uuid4().hex[:12].upper()}",
            schedule_id=schedule_id,
            engine_version=ENGINE_VERSION,
            status=status,
            calculated_at=now,
            project_planned_finish=calculation.project_planned_finish,
            completion_variance_days=calculation.completion_variance_days,
            validation_issues=validation_issues,
            results=calculation.results,
        )
        return self._save_run(workspace, run)

    def _save_run(self, workspace, run: ScheduleRun) -> ScheduleRun:
        self.catalog.assert_valid(run.to_dict(), SCHEDULE_RUN_SCHEMA)
        self.repository.save_schedule_run(run)
        updated = replace(workspace, status=run.status, updated_at=datetime.now(timezone.utc))
        self.catalog.assert_valid(updated.to_dict(), SCHEDULE_WORKSPACE_SCHEMA)
        self.repository.save_schedule(updated)
        return run

    def latest_run(self, schedule_id: str) -> ScheduleRun | None:
        return self.repository.latest_schedule_run(schedule_id)
