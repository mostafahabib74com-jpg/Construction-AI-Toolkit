"""Activity relationship editing with immediate endpoint and cycle checks."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from construction_ai_orchestrator.scheduling.graph import find_cycle
from construction_ai_orchestrator.validation import SchemaCatalog

from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.schedule_models import ActivityRelationship, parse_decimal
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository

from .planning_contracts import SCHEDULE_RELATIONSHIP_SCHEMA


class RelationshipService:
    def __init__(self, repository: SQLiteRepository, catalog: SchemaCatalog) -> None:
        self.repository = repository
        self.catalog = catalog

    def list(self, schedule_id: str) -> list[ActivityRelationship]:
        return self.repository.list_relationships(schedule_id)

    def save(
        self,
        *,
        schedule_id: str,
        predecessor_activity_pk: str,
        successor_activity_pk: str,
        relationship_type: str,
        lag_hours: Decimal | str | int,
        notes: str | None = None,
        relationship_id: str | None = None,
    ) -> ActivityRelationship:
        activity_ids = {item.activity_pk for item in self.repository.list_activities(schedule_id)}
        if predecessor_activity_pk not in activity_ids or successor_activity_pk not in activity_ids:
            raise SchedulingInputError("Both relationship activities must exist in this schedule.")
        if predecessor_activity_pk == successor_activity_pk:
            raise SchedulingInputError("An activity cannot depend on itself.")
        if relationship_type not in {"FS", "SS", "FF", "SF"}:
            raise SchedulingInputError("Relationship type must be FS, SS, FF, or SF.")
        parsed_lag = parse_decimal(lag_hours)
        if parsed_lag is None:
            raise SchedulingInputError("Lag hours are required. Enter zero when there is no lag.")
        existing = [item for item in self.list(schedule_id) if item.relationship_id != relationship_id]
        key = (predecessor_activity_pk, successor_activity_pk, relationship_type, parsed_lag)
        if any(
            (item.predecessor_activity_pk, item.successor_activity_pk, item.relationship_type, item.lag_hours) == key
            for item in existing
        ):
            raise SchedulingInputError("The same relationship already exists.")
        edges = [(item.predecessor_activity_pk, item.successor_activity_pk) for item in existing]
        edges.append((predecessor_activity_pk, successor_activity_pk))
        cycle = find_cycle(activity_ids, edges)
        if cycle:
            raise SchedulingInputError(f"This relationship would create a cycle: {' -> '.join(cycle)}")
        relationship = ActivityRelationship(
            relationship_id=relationship_id or f"REL-{uuid4().hex[:12].upper()}",
            schedule_id=schedule_id,
            predecessor_activity_pk=predecessor_activity_pk,
            successor_activity_pk=successor_activity_pk,
            relationship_type=relationship_type,
            lag_hours=parsed_lag,
            notes=notes.strip() if notes and notes.strip() else None,
            created_at=datetime.now(timezone.utc),
        )
        self.catalog.assert_valid(relationship.to_dict(), SCHEDULE_RELATIONSHIP_SCHEMA)
        try:
            self.repository.save_relationship(relationship)
        except sqlite3.IntegrityError as exc:
            raise SchedulingInputError("Relationship references are invalid or duplicated.") from exc
        return relationship

    def delete(self, relationship_id: str) -> None:
        self.repository.delete_relationship(relationship_id)
