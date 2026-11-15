"""Map application scheduling records to the stable canonical schedule contract."""

from __future__ import annotations

from datetime import datetime

from construction_ai_scheduling.domain.models import Project
from construction_ai_scheduling.domain.schedule_models import (
    ActivityCalculationResult,
    ActivityRelationship,
    ProjectCalendar,
    ScheduleActivity,
    ScheduleWorkspace,
    WBSNode,
)


def _wbs_levels(nodes: list[WBSNode]) -> dict[str, int]:
    by_id = {item.wbs_id: item for item in nodes}
    levels: dict[str, int] = {}

    def level(wbs_id: str) -> int:
        if wbs_id in levels:
            return levels[wbs_id]
        parent = by_id[wbs_id].parent_wbs_id
        levels[wbs_id] = 0 if parent is None else level(parent) + 1
        return levels[wbs_id]

    for node in nodes:
        level(node.wbs_id)
    return levels


def to_canonical_schedule(
    *,
    project: Project,
    workspace: ScheduleWorkspace,
    wbs_nodes: list[WBSNode],
    calendars: list[ProjectCalendar],
    activities: list[ScheduleActivity],
    relationships: list[ActivityRelationship],
    results: tuple[ActivityCalculationResult, ...],
) -> dict:
    levels = _wbs_levels(wbs_nodes)
    results_by_id = {item.activity_pk: item for item in results}
    incoming: dict[str, list[ActivityRelationship]] = {item.activity_pk: [] for item in activities}
    activity_ids = {item.activity_pk: item.activity_id for item in activities}
    for item in relationships:
        incoming[item.successor_activity_pk].append(item)
    data_date = datetime.combine(project.planned_start_date, project.workday_start_time).replace(
        tzinfo=results[0].early_start.tzinfo
    )
    return {
        "schedule_id": workspace.schedule_id,
        "project_id": project.project_id,
        "version": workspace.version,
        "data_date": data_date.isoformat(),
        "status": "draft",
        "wbs": [
            {
                "wbs_id": item.wbs_id,
                "name": item.name,
                "parent_wbs_id": item.parent_wbs_id,
                "level": levels[item.wbs_id],
                "description": item.notes,
                "responsible_role": None,
                "status": "draft",
                "evidence_ids": [],
            }
            for item in wbs_nodes
        ],
        "calendars": [
            {
                "calendar_id": item.calendar_id,
                "name": item.name,
                "time_zone": item.time_zone,
                "hours_per_day": float(item.working_hours_per_day),
                "working_days": list(item.working_weekdays),
                "exceptions": [
                    {
                        "date": exception.exception_date.isoformat(),
                        "working": exception.working,
                        "hours": float(exception.working_hours) if exception.working_hours is not None else None,
                        "reason": exception.reason,
                    }
                    for exception in item.exceptions
                ],
            }
            for item in calendars
        ],
        "activities": [
            {
                "activity_id": item.activity_id,
                "wbs_id": item.wbs_id,
                "name": item.activity_name,
                "activity_type": item.activity_type,
                "duration_hours": float(results_by_id[item.activity_pk].exact_duration_hours),
                "calendar_id": item.calendar_id,
                "status": "not_started",
                "planned_start": results_by_id[item.activity_pk].early_start.isoformat(),
                "planned_finish": results_by_id[item.activity_pk].early_finish.isoformat(),
                "relationships": [
                    {
                        "predecessor_activity_id": activity_ids[relation.predecessor_activity_pk],
                        "type": relation.relationship_type,
                        "lag_hours": float(relation.lag_hours),
                    }
                    for relation in incoming[item.activity_pk]
                ],
                "evidence_ids": [],
            }
            for item in activities
        ],
    }
