"""Application validation for draft WBS, activities, calendars, and logic."""

from __future__ import annotations

from collections import Counter

from construction_ai_orchestrator.scheduling.graph import find_cycle
from construction_ai_scheduling.domain.calendar_engine import validate_calendar
from construction_ai_scheduling.domain.schedule_models import (
    ActivityRelationship,
    ProjectCalendar,
    ScheduleActivity,
    WBSNode,
)


def issue(code: str, message: str, field: str, *, severity: str = "error", record_id: str | None = None) -> dict[str, str]:
    value = {"code": code, "message": message, "field": field, "severity": severity}
    if record_id:
        value["record_id"] = record_id
    return value


def validate_schedule_inputs(
    *,
    wbs_nodes: list[WBSNode],
    calendars: list[ProjectCalendar],
    activities: list[ScheduleActivity],
    relationships: list[ActivityRelationship],
) -> tuple[dict[str, str], ...]:
    issues: list[dict[str, str]] = []
    wbs_ids = {item.wbs_id for item in wbs_nodes}
    for code, count in Counter(item.code.strip().casefold() for item in wbs_nodes).items():
        if count > 1:
            issues.append(issue("WBS_CODE_DUPLICATE", f"WBS code '{code}' is duplicated.", "wbs.code"))
    for item in wbs_nodes:
        if not item.code.strip():
            issues.append(issue("WBS_CODE_REQUIRED", "WBS code is required.", "wbs.code", record_id=item.wbs_id))
        if not item.name.strip():
            issues.append(issue("WBS_NAME_REQUIRED", "WBS name is required.", "wbs.name", record_id=item.wbs_id))
        if item.parent_wbs_id and item.parent_wbs_id not in wbs_ids:
            issues.append(issue("WBS_PARENT_MISSING", "WBS parent does not exist.", "wbs.parent", record_id=item.wbs_id))
    wbs_cycle = find_cycle(wbs_ids, ((item.parent_wbs_id, item.wbs_id) for item in wbs_nodes if item.parent_wbs_id))
    if wbs_cycle:
        issues.append(issue("WBS_CYCLE", f"WBS hierarchy contains a cycle: {' -> '.join(wbs_cycle)}.", "wbs.parent"))

    calendar_ids = {item.calendar_id for item in calendars}
    for calendar in calendars:
        for calendar_issue in validate_calendar(calendar):
            issues.append({**calendar_issue, "record_id": calendar.calendar_id})
    for code, count in Counter(item.code.strip().casefold() for item in calendars).items():
        if count > 1:
            issues.append(issue("CALENDAR_CODE_DUPLICATE", f"Calendar code '{code}' is duplicated.", "calendar.code"))

    activity_ids = {item.activity_pk for item in activities}
    for value, count in Counter(item.activity_id.strip().casefold() for item in activities).items():
        if count > 1:
            issues.append(issue("ACTIVITY_ID_DUPLICATE", f"Activity ID '{value}' is duplicated.", "activity_id"))
    for item in activities:
        if not item.activity_id.strip():
            issues.append(issue("ACTIVITY_ID_REQUIRED", "Activity ID is required.", "activity_id", record_id=item.activity_pk))
        if not item.activity_name.strip():
            issues.append(issue("ACTIVITY_NAME_REQUIRED", "Activity name is required.", "activity_name", record_id=item.activity_pk))
        if item.wbs_id not in wbs_ids:
            issues.append(issue("ACTIVITY_WBS_REQUIRED", "Assign an existing WBS node.", "wbs_id", record_id=item.activity_pk))
        if item.calendar_id not in calendar_ids:
            issues.append(
                issue("ACTIVITY_CALENDAR_REQUIRED", "Assign an existing project calendar.", "calendar_id", record_id=item.activity_pk)
            )
        if item.activity_type == "task_dependent":
            if item.quantity is None:
                issues.append(issue("QUANTITY_REQUIRED", "Quantity is required; it will not be invented.", "quantity", record_id=item.activity_pk))
            elif item.quantity <= 0:
                issues.append(issue("QUANTITY_NOT_POSITIVE", "Quantity must be positive.", "quantity", record_id=item.activity_pk))
            if item.productivity_rate is None:
                issues.append(
                    issue("PRODUCTIVITY_REQUIRED", "Productivity is required; it will not be assumed.", "productivity_rate", record_id=item.activity_pk)
                )
            elif item.productivity_rate <= 0:
                issues.append(
                    issue("PRODUCTIVITY_NOT_POSITIVE", "Productivity must be positive.", "productivity_rate", record_id=item.activity_pk)
                )
            if item.productivity_basis not in {"per_day", "per_hour"}:
                issues.append(issue("PRODUCTIVITY_BASIS_REQUIRED", "Select a productivity basis.", "productivity_basis", record_id=item.activity_pk))
            if item.crew_count is None:
                issues.append(issue("CREW_COUNT_REQUIRED", "Crew count is required; it will not be assumed.", "crew_count", record_id=item.activity_pk))
            elif item.crew_count <= 0:
                issues.append(issue("CREW_COUNT_NOT_POSITIVE", "Crew count must be positive.", "crew_count", record_id=item.activity_pk))

    edges: list[tuple[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for item in relationships:
        key = (
            item.predecessor_activity_pk,
            item.successor_activity_pk,
            item.relationship_type,
            format(item.lag_hours, "f"),
        )
        if key in seen:
            issues.append(issue("RELATIONSHIP_DUPLICATE", "Duplicate relationship is not allowed.", "relationships", record_id=item.relationship_id))
        seen.add(key)
        if item.predecessor_activity_pk not in activity_ids or item.successor_activity_pk not in activity_ids:
            issues.append(issue("RELATIONSHIP_ENDPOINT_MISSING", "Relationship endpoint does not exist.", "relationships", record_id=item.relationship_id))
            continue
        if item.predecessor_activity_pk == item.successor_activity_pk:
            issues.append(issue("RELATIONSHIP_SELF_REFERENCE", "An activity cannot depend on itself.", "relationships", record_id=item.relationship_id))
        if item.relationship_type not in {"FS", "SS", "FF", "SF"}:
            issues.append(issue("RELATIONSHIP_TYPE_INVALID", "Relationship type must be FS, SS, FF, or SF.", "relationship_type", record_id=item.relationship_id))
        if item.lag_hours < 0:
            issues.append(issue("RELATIONSHIP_NEGATIVE_LAG", "Negative lag requires explicit planner review.", "lag_hours", severity="warning", record_id=item.relationship_id))
        edges.append((item.predecessor_activity_pk, item.successor_activity_pk))
    cycle = find_cycle(activity_ids, edges)
    if cycle:
        issues.append(issue("SCHEDULE_LOGIC_CYCLE", f"Activity logic contains a cycle: {' -> '.join(cycle)}.", "relationships"))
    return tuple(issues)
