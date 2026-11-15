"""Create and retrieve validated local scheduling projects."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any
from uuid import uuid4

from construction_ai_orchestrator.validation import SchemaCatalog

from construction_ai_scheduling.domain.errors import InputValidationError
from construction_ai_scheduling.domain.models import Project
from construction_ai_scheduling.domain.validation import validate_project_input
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository

from .planning_contracts import SCHEDULING_PROJECT_SCHEMA


def _clean_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _as_time(value: Any) -> time | str | None:
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    if isinstance(value, str):
        return value.strip()
    return None


class ProjectService:
    def __init__(self, repository: SQLiteRepository, catalog: SchemaCatalog) -> None:
        self.repository = repository
        self.catalog = catalog

    @staticmethod
    def normalize_input(value: dict[str, Any]) -> dict[str, Any]:
        days = value.get("working_days_per_week")
        if isinstance(days, float) and days.is_integer():
            days = int(days)
        hours = value.get("working_hours_per_day")
        if isinstance(hours, int) and not isinstance(hours, bool):
            hours = float(hours)
        return {
            "name": _clean_text(value.get("name")),
            "client": _clean_text(value.get("client")),
            "contractor": _clean_text(value.get("contractor")),
            "consultant": _clean_text(value.get("consultant")),
            "project_type": _clean_text(value.get("project_type")),
            "location": _clean_text(value.get("location")),
            "planned_start_date": _as_date(value.get("planned_start_date")),
            "required_completion_date": _as_date(value.get("required_completion_date")),
            "working_days_per_week": days,
            "working_hours_per_day": hours,
            "working_weekdays": [str(day).lower() for day in (value.get("working_weekdays") or [])],
            "workday_start_time": _as_time(value.get("workday_start_time")),
            "currency": _clean_text(value.get("currency")).upper(),
            "unit_system": _clean_text(value.get("unit_system")),
            "time_zone": _clean_text(value.get("time_zone")),
        }

    def create_project(self, value: dict[str, Any]) -> Project:
        normalized = self.normalize_input(value)
        issues = validate_project_input(normalized)
        if issues:
            raise InputValidationError("Project setup contains required or invalid fields.", issues)

        workday_start = normalized["workday_start_time"]
        if isinstance(workday_start, str):
            workday_start = time.fromisoformat(workday_start)
        now = datetime.now(timezone.utc)
        project = Project(
            project_id=f"PRJ-{uuid4().hex[:12].upper()}",
            name=normalized["name"],
            client=normalized["client"],
            contractor=normalized["contractor"],
            consultant=normalized["consultant"],
            project_type=normalized["project_type"],
            location=normalized["location"],
            planned_start_date=normalized["planned_start_date"],
            required_completion_date=normalized["required_completion_date"],
            working_days_per_week=normalized["working_days_per_week"],
            working_hours_per_day=float(normalized["working_hours_per_day"]),
            working_weekdays=tuple(normalized["working_weekdays"]),
            workday_start_time=workday_start,
            currency=normalized["currency"],
            unit_system=normalized["unit_system"],
            time_zone=normalized["time_zone"],
            created_at=now,
            updated_at=now,
        )
        self.catalog.assert_valid(project.to_dict(), SCHEDULING_PROJECT_SCHEMA)
        self.repository.create_project(project)
        return project

    def list_projects(self) -> list[Project]:
        return self.repository.list_projects()

    def get_project(self, project_id: str) -> Project | None:
        return self.repository.get_project(project_id)
