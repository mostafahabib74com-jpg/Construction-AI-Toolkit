"""WBS draft editing with stable internal identifiers."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from construction_ai_orchestrator.scheduling.graph import find_cycle
from construction_ai_orchestrator.validation import SchemaCatalog

from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.schedule_models import WBSNode
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository

from .planning_contracts import SCHEDULE_WBS_NODE_SCHEMA


class WBSService:
    def __init__(self, repository: SQLiteRepository, catalog: SchemaCatalog) -> None:
        self.repository = repository
        self.catalog = catalog

    def list(self, schedule_id: str) -> list[WBSNode]:
        return self.repository.list_wbs_nodes(schedule_id)

    def save(
        self,
        *,
        schedule_id: str,
        code: str,
        name: str,
        parent_wbs_id: str | None,
        sort_order: int,
        notes: str | None = None,
        wbs_id: str | None = None,
    ) -> WBSNode:
        now = datetime.now(timezone.utc)
        existing = next((item for item in self.list(schedule_id) if item.wbs_id == wbs_id), None)
        node = WBSNode(
            wbs_id=wbs_id or f"WBS-{uuid4().hex[:12].upper()}",
            schedule_id=schedule_id,
            code=code.strip(),
            name=name.strip(),
            parent_wbs_id=parent_wbs_id or None,
            sort_order=int(sort_order),
            notes=notes.strip() if notes and notes.strip() else None,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        nodes = [item for item in self.list(schedule_id) if item.wbs_id != node.wbs_id] + [node]
        ids = {item.wbs_id for item in nodes}
        if node.parent_wbs_id and node.parent_wbs_id not in ids:
            raise SchedulingInputError("The selected parent WBS does not exist.")
        cycle = find_cycle(ids, ((item.parent_wbs_id, item.wbs_id) for item in nodes if item.parent_wbs_id))
        if cycle:
            raise SchedulingInputError(f"The WBS parent selection would create a cycle: {' -> '.join(cycle)}")
        self.catalog.assert_valid(node.to_dict(), SCHEDULE_WBS_NODE_SCHEMA)
        try:
            self.repository.save_wbs_node(node)
        except sqlite3.IntegrityError as exc:
            raise SchedulingInputError("WBS codes must be unique inside the schedule.") from exc
        return node

    def delete(self, wbs_id: str) -> None:
        try:
            self.repository.delete_wbs_node(wbs_id)
        except sqlite3.IntegrityError as exc:
            raise SchedulingInputError("This WBS cannot be deleted while a child or activity references it.") from exc
