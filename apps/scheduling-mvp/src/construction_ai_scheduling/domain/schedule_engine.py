"""Forward-pass planned-date calculation without CPM or float calculations."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from construction_ai_orchestrator.scheduling.graph import topological_sort
from construction_ai_scheduling.domain.calendar_engine import add_working_hours, next_working_time, subtract_working_hours
from construction_ai_scheduling.domain.duration_engine import DurationCalculation, calculate_duration
from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.models import Project
from construction_ai_scheduling.domain.schedule_models import (
    ActivityCalculationResult,
    ActivityRelationship,
    ProjectCalendar,
    ScheduleActivity,
    ScheduleWorkspace,
    WBSNode,
)
from construction_ai_scheduling.domain.schedule_validation import validate_schedule_inputs


ENGINE_VERSION = "2.0.0-forward-pass"


@dataclass(frozen=True, slots=True)
class ForwardPassResult:
    results: tuple[ActivityCalculationResult, ...]
    project_planned_finish: datetime
    completion_variance_days: int
    validation_issues: tuple[dict[str, str], ...]


def _constraint_start(
    relationship: ActivityRelationship,
    predecessor: ActivityCalculationResult,
    successor_duration: DurationCalculation,
    successor_calendar: ProjectCalendar,
) -> datetime:
    if relationship.relationship_type in {"FS", "FF"}:
        reference = predecessor.early_finish
    else:
        reference = predecessor.early_start
    constrained_event = add_working_hours(reference, relationship.lag_hours, successor_calendar)
    if relationship.relationship_type in {"FS", "SS"}:
        return next_working_time(constrained_event, successor_calendar)
    return subtract_working_hours(constrained_event, successor_duration.exact_duration_hours, successor_calendar)


def calculate_forward_pass(
    *,
    project: Project,
    workspace: ScheduleWorkspace,
    wbs_nodes: list[WBSNode],
    calendars: list[ProjectCalendar],
    activities: list[ScheduleActivity],
    relationships: list[ActivityRelationship],
) -> ForwardPassResult:
    issues = validate_schedule_inputs(
        wbs_nodes=wbs_nodes,
        calendars=calendars,
        activities=activities,
        relationships=relationships,
    )
    blockers = tuple(item for item in issues if item["severity"] == "error")
    if not activities:
        blockers += ({"code": "ACTIVITIES_REQUIRED", "message": "At least one activity is required.", "field": "activities", "severity": "error"},)
    if blockers:
        raise SchedulingInputError("Schedule cannot be calculated until blocking inputs are corrected.", issues)

    calendar_by_id = {item.calendar_id: item for item in calendars}
    activity_by_pk = {item.activity_pk: item for item in activities}
    incoming: dict[str, list[ActivityRelationship]] = defaultdict(list)
    edges: list[tuple[str, str]] = []
    for item in relationships:
        incoming[item.successor_activity_pk].append(item)
        edges.append((item.predecessor_activity_pk, item.successor_activity_pk))
    ordered = topological_sort(activity_by_pk, edges)
    calculations: dict[str, ActivityCalculationResult] = {}
    project_origin = datetime.combine(
        project.planned_start_date,
        project.workday_start_time,
        ZoneInfo(project.time_zone),
    )
    for activity_pk in ordered:
        activity = activity_by_pk[activity_pk]
        calendar = calendar_by_id[activity.calendar_id]
        duration = calculate_duration(
            activity_type=activity.activity_type,
            quantity=activity.quantity,
            productivity_rate=activity.productivity_rate,
            productivity_basis=activity.productivity_basis,
            crew_count=activity.crew_count,
            working_hours_per_day=calendar.working_hours_per_day,
            rounding_precision=workspace.rounding_precision,
            rounding_mode=workspace.rounding_mode,
        )
        candidates = [next_working_time(project_origin, calendar)]
        for relationship in incoming.get(activity_pk, []):
            candidates.append(_constraint_start(relationship, calculations[relationship.predecessor_activity_pk], duration, calendar))
        early_start = max(candidates)
        if duration.exact_duration_hours > 0:
            early_start = next_working_time(early_start, calendar)
            early_finish = add_working_hours(early_start, duration.exact_duration_hours, calendar)
        else:
            early_finish = early_start
        calculations[activity_pk] = ActivityCalculationResult(
            activity_pk=activity_pk,
            exact_duration_hours=duration.exact_duration_hours,
            exact_duration_days=duration.exact_duration_days,
            display_duration_days=duration.display_duration_days,
            early_start=early_start,
            early_finish=early_finish,
            formula=duration.formula,
            calculation_trace={
                **duration.calculation_trace,
                "calendar_id": calendar.calendar_id,
                "relationship_constraints": [item.relationship_id for item in incoming.get(activity_pk, [])],
            },
        )
    results = tuple(calculations[item.activity_pk] for item in sorted(activities, key=lambda value: (value.sort_order, value.activity_id)))
    project_finish = max(item.early_finish for item in results)
    variance = (project_finish.date() - project.required_completion_date).days
    return ForwardPassResult(results, project_finish, variance, issues)
