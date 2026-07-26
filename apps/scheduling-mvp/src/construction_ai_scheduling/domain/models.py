"""Milestone 1 domain records with canonical serialization."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    field: str
    code: str
    message: str
    category: str = "invalid"


@dataclass(frozen=True, slots=True)
class Project:
    project_id: str
    name: str
    client: str
    contractor: str
    consultant: str
    project_type: str
    location: str
    planned_start_date: date
    required_completion_date: date
    working_days_per_week: int
    working_hours_per_day: float
    working_weekdays: tuple[str, ...]
    workday_start_time: time
    currency: str
    unit_system: str
    time_zone: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "client": self.client,
            "contractor": self.contractor,
            "consultant": self.consultant,
            "project_type": self.project_type,
            "location": self.location,
            "planned_start_date": self.planned_start_date.isoformat(),
            "required_completion_date": self.required_completion_date.isoformat(),
            "working_days_per_week": self.working_days_per_week,
            "working_hours_per_day": self.working_hours_per_day,
            "working_weekdays": list(self.working_weekdays),
            "workday_start_time": self.workday_start_time.strftime("%H:%M"),
            "currency": self.currency,
            "unit_system": self.unit_system,
            "time_zone": self.time_zone,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Project":
        return cls(
            project_id=value["project_id"],
            name=value["name"],
            client=value["client"],
            contractor=value["contractor"],
            consultant=value["consultant"],
            project_type=value["project_type"],
            location=value["location"],
            planned_start_date=date.fromisoformat(value["planned_start_date"]),
            required_completion_date=date.fromisoformat(value["required_completion_date"]),
            working_days_per_week=int(value["working_days_per_week"]),
            working_hours_per_day=float(value["working_hours_per_day"]),
            working_weekdays=tuple(value["working_weekdays"]),
            workday_start_time=time.fromisoformat(value["workday_start_time"]),
            currency=value["currency"],
            unit_system=value["unit_system"],
            time_zone=value["time_zone"],
            created_at=datetime.fromisoformat(value["created_at"]),
            updated_at=datetime.fromisoformat(value["updated_at"]),
        )


@dataclass(frozen=True, slots=True)
class BOQRow:
    row_id: str
    project_id: str
    import_id: str
    source_row_number: int
    item_code: str | None
    description: str | None
    quantity: float | None
    quantity_raw: str | float | int | None
    unit: str | None
    normalized_unit: str | None
    validation_status: str
    validation_errors: tuple[str, ...]
    raw_data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["validation_errors"] = list(self.validation_errors)
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "BOQRow":
        return cls(
            row_id=value["row_id"],
            project_id=value["project_id"],
            import_id=value["import_id"],
            source_row_number=int(value["source_row_number"]),
            item_code=value.get("item_code"),
            description=value.get("description"),
            quantity=float(value["quantity"]) if value.get("quantity") is not None else None,
            quantity_raw=value.get("quantity_raw"),
            unit=value.get("unit"),
            normalized_unit=value.get("normalized_unit"),
            validation_status=value["validation_status"],
            validation_errors=tuple(value.get("validation_errors") or ()),
            raw_data=dict(value.get("raw_data") or {}),
        )


@dataclass(frozen=True, slots=True)
class BOQImport:
    import_id: str
    project_id: str
    source_file_name: str
    source_type: str
    source_sheet: str | None
    imported_at: datetime
    rows: tuple[BOQRow, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "import_id": self.import_id,
            "project_id": self.project_id,
            "source_file_name": self.source_file_name,
            "source_type": self.source_type,
            "source_sheet": self.source_sheet,
            "imported_at": self.imported_at.isoformat(),
            "row_count": len(self.rows),
            "rows": [row.to_dict() for row in self.rows],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "BOQImport":
        return cls(
            import_id=value["import_id"],
            project_id=value["project_id"],
            source_file_name=value["source_file_name"],
            source_type=value["source_type"],
            source_sheet=value.get("source_sheet"),
            imported_at=datetime.fromisoformat(value["imported_at"]),
            rows=tuple(BOQRow.from_dict(row) for row in value.get("rows") or ()),
        )
