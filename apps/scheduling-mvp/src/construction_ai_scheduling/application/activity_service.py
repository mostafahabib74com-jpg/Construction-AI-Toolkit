"""Explicit BOQ-to-activity conversion and draft activity editing."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from construction_ai_orchestrator.validation import SchemaCatalog

from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.schedule_models import ScheduleActivity, parse_decimal
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository

from .planning_contracts import SCHEDULE_ACTIVITY_SCHEMA


@dataclass(frozen=True, slots=True)
class BOQConversionResult:
    created: tuple[ScheduleActivity, ...]
    skipped_row_ids: tuple[str, ...]


class ActivityService:
    def __init__(self, repository: SQLiteRepository, catalog: SchemaCatalog) -> None:
        self.repository = repository
        self.catalog = catalog

    def list(self, schedule_id: str) -> list[ScheduleActivity]:
        return self.repository.list_activities(schedule_id)

    def convert_boq_rows(self, schedule_id: str, import_id: str, row_ids: list[str]) -> BOQConversionResult:
        selected = set(row_ids)
        source_rows = [item for item in self.repository.get_boq_rows(import_id) if item.row_id in selected]
        if len(source_rows) != len(selected):
            raise SchedulingInputError("One or more selected BOQ rows do not exist in this import.")
        existing_sources = {item.source_boq_row_id for item in self.list(schedule_id) if item.source_boq_row_id}
        created: list[ScheduleActivity] = []
        skipped: list[str] = []
        next_order = max((item.sort_order for item in self.list(schedule_id)), default=-1) + 1
        for row in source_rows:
            if row.validation_status != "valid" or row.row_id in existing_sources:
                skipped.append(row.row_id)
                continue
            activity = self.save(
                schedule_id=schedule_id,
                activity_id=f"A{(next_order + 1) * 10:04d}",
                activity_name=row.description or "",
                activity_type="task_dependent",
                quantity=str(row.quantity) if row.quantity is not None else None,
                unit=row.unit,
                normalized_unit=row.normalized_unit,
                wbs_id=None,
                productivity_rate=None,
                productivity_basis=None,
                crew_count=None,
                calendar_id=None,
                notes=None,
                assumptions=[],
                sort_order=next_order,
                source_boq_row_id=row.row_id,
                boq_item_code=row.item_code,
                boq_description=row.description,
                source_row_number=row.source_row_number,
            )
            created.append(activity)
            next_order += 1
        return BOQConversionResult(tuple(created), tuple(skipped))

    def create_split_activity(self, source_activity_pk: str, *, activity_id: str, activity_name: str) -> ScheduleActivity:
        source = self.repository.get_activity(source_activity_pk)
        if source is None:
            raise SchedulingInputError("Source activity was not found.")
        next_order = max((item.sort_order for item in self.list(source.schedule_id)), default=-1) + 1
        return self.save(
            schedule_id=source.schedule_id,
            activity_id=activity_id,
            activity_name=activity_name,
            activity_type="task_dependent",
            quantity=None,
            unit=source.unit,
            normalized_unit=source.normalized_unit,
            wbs_id=source.wbs_id,
            productivity_rate=None,
            productivity_basis=None,
            crew_count=None,
            calendar_id=source.calendar_id,
            notes="Split from BOQ-linked activity; quantity allocation requires user input.",
            assumptions=[],
            sort_order=next_order,
            source_boq_row_id=source.source_boq_row_id,
            boq_item_code=source.boq_item_code,
            boq_description=source.boq_description,
            source_row_number=source.source_row_number,
        )

    def save(self, **value: Any) -> ScheduleActivity:
        now = datetime.now(timezone.utc)
        activity_pk = value.get("activity_pk") or f"ACT-{uuid4().hex[:12].upper()}"
        existing = self.repository.get_activity(activity_pk)
        activity = ScheduleActivity(
            activity_pk=activity_pk,
            schedule_id=value["schedule_id"],
            activity_id=str(value.get("activity_id") or "").strip(),
            activity_name=str(value.get("activity_name") or "").strip(),
            activity_type=value.get("activity_type") or "task_dependent",
            source_boq_row_id=value.get("source_boq_row_id") if not existing else existing.source_boq_row_id,
            boq_item_code=value.get("boq_item_code") if not existing else existing.boq_item_code,
            boq_description=value.get("boq_description") if not existing else existing.boq_description,
            source_row_number=value.get("source_row_number") if not existing else existing.source_row_number,
            quantity=parse_decimal(value.get("quantity")),
            unit=str(value["unit"]).strip() if value.get("unit") else None,
            normalized_unit=str(value["normalized_unit"]).strip() if value.get("normalized_unit") else None,
            wbs_id=value.get("wbs_id") or None,
            productivity_rate=parse_decimal(value.get("productivity_rate")),
            productivity_basis=value.get("productivity_basis") or None,
            crew_count=int(value["crew_count"]) if value.get("crew_count") not in {None, ""} else None,
            calendar_id=value.get("calendar_id") or None,
            notes=str(value["notes"]).strip() if value.get("notes") else None,
            assumptions=tuple(dict.fromkeys(item.strip() for item in value.get("assumptions") or [] if item.strip())),
            sort_order=int(value.get("sort_order") or 0),
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        self.catalog.assert_valid(activity.to_dict(), SCHEDULE_ACTIVITY_SCHEMA)
        try:
            self.repository.save_activity(activity)
        except sqlite3.IntegrityError as exc:
            raise SchedulingInputError("Activity IDs must be unique and references must exist.") from exc
        return activity

    def delete(self, activity_pk: str) -> None:
        activity = self.repository.get_activity(activity_pk)
        if activity is None:
            return
        if any(
            item.predecessor_activity_pk == activity_pk or item.successor_activity_pk == activity_pk
            for item in self.repository.list_relationships(activity.schedule_id)
        ):
            raise SchedulingInputError("Remove relationships before deleting this activity.")
        self.repository.delete_activity(activity_pk)
