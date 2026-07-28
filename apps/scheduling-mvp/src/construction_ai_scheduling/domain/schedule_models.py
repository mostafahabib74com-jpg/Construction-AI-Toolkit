"""Milestone 2 scheduling records with exact decimal serialization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any


def decimal_text(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def parse_decimal(value: Any) -> Decimal | None:
    return None if value is None or value == "" else Decimal(str(value))


@dataclass(frozen=True, slots=True)
class ScheduleWorkspace:
    schedule_id: str
    project_id: str
    name: str
    version: str
    status: str
    calculation_mode: str
    rounding_precision: int
    rounding_mode: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "schedule_id": self.schedule_id,
            "project_id": self.project_id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "calculation_mode": self.calculation_mode,
            "rounding_precision": self.rounding_precision,
            "rounding_mode": self.rounding_mode,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ScheduleWorkspace":
        return cls(
            schedule_id=value["schedule_id"],
            project_id=value["project_id"],
            name=value["name"],
            version=value["version"],
            status=value["status"],
            calculation_mode=value["calculation_mode"],
            rounding_precision=int(value["rounding_precision"]),
            rounding_mode=value["rounding_mode"],
            created_at=datetime.fromisoformat(value["created_at"]),
            updated_at=datetime.fromisoformat(value["updated_at"]),
        )


@dataclass(frozen=True, slots=True)
class WBSNode:
    wbs_id: str
    schedule_id: str
    code: str
    name: str
    parent_wbs_id: str | None
    sort_order: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "wbs_id": self.wbs_id,
            "schedule_id": self.schedule_id,
            "code": self.code,
            "name": self.name,
            "parent_wbs_id": self.parent_wbs_id,
            "sort_order": self.sort_order,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "WBSNode":
        return cls(
            wbs_id=value["wbs_id"],
            schedule_id=value["schedule_id"],
            code=value["code"],
            name=value["name"],
            parent_wbs_id=value.get("parent_wbs_id"),
            sort_order=int(value["sort_order"]),
            notes=value.get("notes"),
            created_at=datetime.fromisoformat(value["created_at"]),
            updated_at=datetime.fromisoformat(value["updated_at"]),
        )


@dataclass(frozen=True, slots=True)
class CalendarBreak:
    break_id: str
    start_time: time
    end_time: time

    def to_dict(self) -> dict[str, Any]:
        return {
            "break_id": self.break_id,
            "start_time": self.start_time.strftime("%H:%M"),
            "end_time": self.end_time.strftime("%H:%M"),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CalendarBreak":
        return cls(
            break_id=value["break_id"],
            start_time=time.fromisoformat(value["start_time"]),
            end_time=time.fromisoformat(value["end_time"]),
        )


@dataclass(frozen=True, slots=True)
class CalendarException:
    exception_id: str
    exception_date: date
    working: bool
    workday_start_time: time | None
    working_hours: Decimal | None
    reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "exception_id": self.exception_id,
            "date": self.exception_date.isoformat(),
            "working": self.working,
            "workday_start_time": self.workday_start_time.strftime("%H:%M") if self.workday_start_time else None,
            "working_hours": decimal_text(self.working_hours),
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CalendarException":
        return cls(
            exception_id=value["exception_id"],
            exception_date=date.fromisoformat(value.get("date") or value["exception_date"]),
            working=bool(value["working"]),
            workday_start_time=time.fromisoformat(value["workday_start_time"]) if value.get("workday_start_time") else None,
            working_hours=parse_decimal(value.get("working_hours")),
            reason=value.get("reason"),
        )


@dataclass(frozen=True, slots=True)
class ProjectCalendar:
    calendar_id: str
    schedule_id: str
    code: str
    name: str
    time_zone: str
    working_weekdays: tuple[str, ...]
    workday_start_time: time
    working_hours_per_day: Decimal
    breaks: tuple[CalendarBreak, ...]
    exceptions: tuple[CalendarException, ...]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "calendar_id": self.calendar_id,
            "schedule_id": self.schedule_id,
            "code": self.code,
            "name": self.name,
            "time_zone": self.time_zone,
            "working_weekdays": list(self.working_weekdays),
            "workday_start_time": self.workday_start_time.strftime("%H:%M"),
            "working_hours_per_day": decimal_text(self.working_hours_per_day),
            "breaks": [item.to_dict() for item in self.breaks],
            "exceptions": [item.to_dict() for item in self.exceptions],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ProjectCalendar":
        return cls(
            calendar_id=value["calendar_id"],
            schedule_id=value["schedule_id"],
            code=value["code"],
            name=value["name"],
            time_zone=value["time_zone"],
            working_weekdays=tuple(value["working_weekdays"]),
            workday_start_time=time.fromisoformat(value["workday_start_time"]),
            working_hours_per_day=Decimal(str(value["working_hours_per_day"])),
            breaks=tuple(CalendarBreak.from_dict(item) for item in value.get("breaks") or ()),
            exceptions=tuple(CalendarException.from_dict(item) for item in value.get("exceptions") or ()),
            created_at=datetime.fromisoformat(value["created_at"]),
            updated_at=datetime.fromisoformat(value["updated_at"]),
        )


@dataclass(frozen=True, slots=True)
class ScheduleActivity:
    activity_pk: str
    schedule_id: str
    activity_id: str
    activity_name: str
    activity_type: str
    source_boq_row_id: str | None
    boq_item_code: str | None
    boq_description: str | None
    source_row_number: int | None
    quantity: Decimal | None
    unit: str | None
    normalized_unit: str | None
    wbs_id: str | None
    productivity_rate: Decimal | None
    productivity_basis: str | None
    crew_count: int | None
    calendar_id: str | None
    notes: str | None
    assumptions: tuple[str, ...]
    sort_order: int
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "activity_pk": self.activity_pk,
            "schedule_id": self.schedule_id,
            "activity_id": self.activity_id,
            "activity_name": self.activity_name,
            "activity_type": self.activity_type,
            "source_boq_row_id": self.source_boq_row_id,
            "boq_item_code": self.boq_item_code,
            "boq_description": self.boq_description,
            "source_row_number": self.source_row_number,
            "quantity": decimal_text(self.quantity),
            "unit": self.unit,
            "normalized_unit": self.normalized_unit,
            "wbs_id": self.wbs_id,
            "productivity_rate": decimal_text(self.productivity_rate),
            "productivity_basis": self.productivity_basis,
            "crew_count": self.crew_count,
            "calendar_id": self.calendar_id,
            "notes": self.notes,
            "assumptions": list(self.assumptions),
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ScheduleActivity":
        return cls(
            activity_pk=value["activity_pk"],
            schedule_id=value["schedule_id"],
            activity_id=value["activity_id"],
            activity_name=value["activity_name"],
            activity_type=value["activity_type"],
            source_boq_row_id=value.get("source_boq_row_id"),
            boq_item_code=value.get("boq_item_code"),
            boq_description=value.get("boq_description"),
            source_row_number=int(value["source_row_number"]) if value.get("source_row_number") is not None else None,
            quantity=parse_decimal(value.get("quantity")),
            unit=value.get("unit"),
            normalized_unit=value.get("normalized_unit"),
            wbs_id=value.get("wbs_id"),
            productivity_rate=parse_decimal(value.get("productivity_rate")),
            productivity_basis=value.get("productivity_basis"),
            crew_count=int(value["crew_count"]) if value.get("crew_count") is not None else None,
            calendar_id=value.get("calendar_id"),
            notes=value.get("notes"),
            assumptions=tuple(value.get("assumptions") or ()),
            sort_order=int(value["sort_order"]),
            created_at=datetime.fromisoformat(value["created_at"]),
            updated_at=datetime.fromisoformat(value["updated_at"]),
        )


@dataclass(frozen=True, slots=True)
class ActivityRelationship:
    relationship_id: str
    schedule_id: str
    predecessor_activity_pk: str
    successor_activity_pk: str
    relationship_type: str
    lag_hours: Decimal
    notes: str | None
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "schedule_id": self.schedule_id,
            "predecessor_activity_pk": self.predecessor_activity_pk,
            "successor_activity_pk": self.successor_activity_pk,
            "relationship_type": self.relationship_type,
            "lag_hours": decimal_text(self.lag_hours),
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ActivityRelationship":
        return cls(
            relationship_id=value["relationship_id"],
            schedule_id=value["schedule_id"],
            predecessor_activity_pk=value["predecessor_activity_pk"],
            successor_activity_pk=value["successor_activity_pk"],
            relationship_type=value["relationship_type"],
            lag_hours=Decimal(str(value["lag_hours"])),
            notes=value.get("notes"),
            created_at=datetime.fromisoformat(value["created_at"]),
        )


@dataclass(frozen=True, slots=True)
class ActivityCalculationResult:
    activity_pk: str
    exact_duration_hours: Decimal
    exact_duration_days: Decimal
    display_duration_days: Decimal
    early_start: datetime
    early_finish: datetime
    formula: str
    calculation_trace: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "activity_pk": self.activity_pk,
            "exact_duration_hours": decimal_text(self.exact_duration_hours),
            "exact_duration_days": decimal_text(self.exact_duration_days),
            "display_duration_days": decimal_text(self.display_duration_days),
            "early_start": self.early_start.isoformat(),
            "early_finish": self.early_finish.isoformat(),
            "formula": self.formula,
            "calculation_trace": self.calculation_trace,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ActivityCalculationResult":
        return cls(
            activity_pk=value["activity_pk"],
            exact_duration_hours=Decimal(str(value["exact_duration_hours"])),
            exact_duration_days=Decimal(str(value["exact_duration_days"])),
            display_duration_days=Decimal(str(value["display_duration_days"])),
            early_start=datetime.fromisoformat(value["early_start"]),
            early_finish=datetime.fromisoformat(value["early_finish"]),
            formula=value["formula"],
            calculation_trace=dict(value.get("calculation_trace") or {}),
        )


@dataclass(frozen=True, slots=True)
class ScheduleRun:
    run_id: str
    schedule_id: str
    engine_version: str
    status: str
    calculated_at: datetime
    project_planned_finish: datetime | None
    completion_variance_days: int | None
    validation_issues: tuple[dict[str, Any], ...]
    results: tuple[ActivityCalculationResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "schedule_id": self.schedule_id,
            "engine_version": self.engine_version,
            "status": self.status,
            "calculated_at": self.calculated_at.isoformat(),
            "project_planned_finish": self.project_planned_finish.isoformat() if self.project_planned_finish else None,
            "completion_variance_days": self.completion_variance_days,
            "validation_issues": list(self.validation_issues),
            "results": [item.to_dict() for item in self.results],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ScheduleRun":
        return cls(
            run_id=value["run_id"],
            schedule_id=value["schedule_id"],
            engine_version=value["engine_version"],
            status=value["status"],
            calculated_at=datetime.fromisoformat(value["calculated_at"]),
            project_planned_finish=datetime.fromisoformat(value["project_planned_finish"]) if value.get("project_planned_finish") else None,
            completion_variance_days=int(value["completion_variance_days"]) if value.get("completion_variance_days") is not None else None,
            validation_issues=tuple(value.get("validation_issues") or ()),
            results=tuple(ActivityCalculationResult.from_dict(item) for item in value.get("results") or ()),
        )
