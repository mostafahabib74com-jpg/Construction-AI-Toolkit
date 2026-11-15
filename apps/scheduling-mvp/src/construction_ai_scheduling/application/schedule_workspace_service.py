"""Create and maintain the single draft schedule workspace for a project."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from construction_ai_orchestrator.validation import SchemaCatalog

from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.schedule_models import ScheduleWorkspace
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository

from .planning_contracts import SCHEDULE_WORKSPACE_SCHEMA


class ScheduleWorkspaceService:
    def __init__(self, repository: SQLiteRepository, catalog: SchemaCatalog) -> None:
        self.repository = repository
        self.catalog = catalog

    def ensure_for_project(self, project_id: str) -> ScheduleWorkspace:
        existing = self.repository.get_schedule_for_project(project_id)
        if existing:
            return existing
        project = self.repository.get_project(project_id)
        if project is None:
            raise SchedulingInputError("Select a saved project before opening its schedule workspace.")
        now = datetime.now(timezone.utc)
        workspace = ScheduleWorkspace(
            schedule_id=f"SCH-{uuid4().hex[:12].upper()}",
            project_id=project_id,
            name=f"{project.name} - Working schedule",
            version="DRAFT-1",
            status="draft",
            calculation_mode="forward_pass",
            rounding_precision=2,
            rounding_mode="ROUND_HALF_UP",
            created_at=now,
            updated_at=now,
        )
        self.catalog.assert_valid(workspace.to_dict(), SCHEDULE_WORKSPACE_SCHEMA)
        self.repository.save_schedule(workspace)
        return workspace

    def update_calculation_settings(
        self, schedule_id: str, *, rounding_precision: int, rounding_mode: str
    ) -> ScheduleWorkspace:
        workspace = self.repository.get_schedule(schedule_id)
        if workspace is None:
            raise SchedulingInputError("Schedule workspace was not found.")
        updated = replace(
            workspace,
            rounding_precision=int(rounding_precision),
            rounding_mode=rounding_mode,
            updated_at=datetime.now(timezone.utc),
        )
        self.catalog.assert_valid(updated.to_dict(), SCHEDULE_WORKSPACE_SCHEMA)
        self.repository.save_schedule(updated)
        return updated
