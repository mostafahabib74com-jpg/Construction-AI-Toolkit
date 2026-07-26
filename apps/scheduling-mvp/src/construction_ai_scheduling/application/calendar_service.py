"""Project-calendar draft editing and explicit project-setting reuse."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

from construction_ai_orchestrator.validation import SchemaCatalog

from construction_ai_scheduling.domain.calendar_engine import assert_valid_calendar
from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.schedule_models import CalendarBreak, CalendarException, ProjectCalendar, parse_decimal
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository

from .planning_contracts import SCHEDULE_CALENDAR_SCHEMA


class CalendarService:
    def __init__(self, repository: SQLiteRepository, catalog: SchemaCatalog) -> None:
        self.repository = repository
        self.catalog = catalog

    def list(self, schedule_id: str) -> list[ProjectCalendar]:
        return self.repository.list_calendars(schedule_id)

    def create_from_project(self, schedule_id: str) -> ProjectCalendar:
        workspace = self.repository.get_schedule(schedule_id)
        project = self.repository.get_project(workspace.project_id) if workspace else None
        if project is None:
            raise SchedulingInputError("The schedule project was not found.")
        return self.save(
            schedule_id=schedule_id,
            code=f"{project.working_days_per_week}D-{project.working_hours_per_day:g}H",
            name="Project setup calendar",
            time_zone=project.time_zone,
            working_weekdays=list(project.working_weekdays),
            workday_start_time=project.workday_start_time,
            working_hours_per_day=Decimal(str(project.working_hours_per_day)),
            breaks=[],
            exceptions=[],
        )

    def save(
        self,
        *,
        schedule_id: str,
        code: str,
        name: str,
        time_zone: str,
        working_weekdays: list[str] | tuple[str, ...],
        workday_start_time: time | str,
        working_hours_per_day: Decimal | str,
        breaks: list[dict[str, Any]],
        exceptions: list[dict[str, Any]],
        calendar_id: str | None = None,
    ) -> ProjectCalendar:
        now = datetime.now(timezone.utc)
        existing = self.repository.get_calendar(calendar_id) if calendar_id else None
        start = time.fromisoformat(workday_start_time) if isinstance(workday_start_time, str) else workday_start_time
        def exception_date(value: Any) -> date:
            if isinstance(value, datetime):
                return value.date()
            return date.fromisoformat(value) if isinstance(value, str) else value

        calendar = ProjectCalendar(
            calendar_id=calendar_id or f"CAL-{uuid4().hex[:12].upper()}",
            schedule_id=schedule_id,
            code=code.strip(),
            name=name.strip(),
            time_zone=time_zone.strip(),
            working_weekdays=tuple(str(item).lower() for item in working_weekdays),
            workday_start_time=start.replace(second=0, microsecond=0),
            working_hours_per_day=parse_decimal(working_hours_per_day) or Decimal("0"),
            breaks=tuple(
                CalendarBreak(
                    item.get("break_id") or f"BRK-{uuid4().hex[:12].upper()}",
                    time.fromisoformat(item["start_time"]) if isinstance(item["start_time"], str) else item["start_time"],
                    time.fromisoformat(item["end_time"]) if isinstance(item["end_time"], str) else item["end_time"],
                )
                for item in breaks
            ),
            exceptions=tuple(
                CalendarException(
                    item.get("exception_id") or f"EXC-{uuid4().hex[:12].upper()}",
                    exception_date(item["date"]),
                    bool(item["working"]),
                    time.fromisoformat(item["workday_start_time"]) if isinstance(item.get("workday_start_time"), str) else item.get("workday_start_time"),
                    parse_decimal(item.get("working_hours")),
                    item.get("reason") or None,
                )
                for item in exceptions
            ),
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        assert_valid_calendar(calendar)
        self.catalog.assert_valid(calendar.to_dict(), SCHEDULE_CALENDAR_SCHEMA)
        try:
            self.repository.save_calendar(calendar)
        except sqlite3.IntegrityError as exc:
            raise SchedulingInputError("Calendar codes must be unique inside the schedule.") from exc
        return calendar

    def delete(self, calendar_id: str) -> None:
        try:
            self.repository.delete_calendar(calendar_id)
        except sqlite3.IntegrityError as exc:
            raise SchedulingInputError("This calendar cannot be deleted while an activity references it.") from exc
