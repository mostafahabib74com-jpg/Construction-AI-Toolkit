"""Generalized precedence CPM in a shared working-time coordinate system.

Multiple activity calendars retain forward dates; their float is deliberately
unavailable instead of mixing incomparable working-hour axes.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal

from construction_ai_orchestrator.scheduling.graph import topological_sort
from .calendar_engine import MAX_SEARCH_DAYS, add_working_hours, next_working_time, working_intervals
from .schedule_models import ActivityCalculationResult, ActivityRelationship, ProjectCalendar, ScheduleActivity


def working_hours_between(start, finish, calendar: ProjectCalendar) -> Decimal:
    if finish < start:
        return -working_hours_between(finish, start, calendar)
    start = start.astimezone(next_working_time(start, calendar).tzinfo)
    finish = finish.astimezone(start.tzinfo)
    days = (finish.date() - start.date()).days
    if days > MAX_SEARCH_DAYS:
        raise ValueError("Schedule exceeds the supported calendar horizon.")
    seconds = Decimal(0)
    for offset in range(days + 1):
        for left, right in working_intervals(calendar, start.date() + timedelta(days=offset)):
            left, right = max(left, start), min(right, finish)
            if right > left:
                delta = right - left
                seconds += Decimal(delta.days * 86400 + delta.seconds) + Decimal(delta.microseconds) / 1000000
    return seconds / 3600


def enrich_with_cpm(
    results: tuple[ActivityCalculationResult, ...],
    activities: list[ScheduleActivity],
    calendars: list[ProjectCalendar],
    relationships: list[ActivityRelationship],
) -> tuple[tuple[ActivityCalculationResult, ...], tuple[dict[str, str], ...]]:
    used_calendars = {activity.calendar_id for activity in activities}
    if len(used_calendars) != 1:
        issue = {"code": "CPM_MULTIPLE_CALENDARS", "severity": "warning", "field": "calendar_id",
                 "message": "Forward dates are available. Float and critical path require a single shared activity calendar in this version."}
        return results, (issue,)
    calendar = next(item for item in calendars if item.calendar_id in used_calendars)
    by_id = {item.activity_pk: item for item in results}
    origin = min(item.early_start for item in results)
    finish = max(item.early_finish for item in results)
    horizon = working_hours_between(origin, finish, calendar)
    early = {key: working_hours_between(origin, value.early_start, calendar) for key, value in by_id.items()}
    outgoing = defaultdict(list)
    edges = []
    for relation in relationships:
        pred_duration = by_id[relation.predecessor_activity_pk].exact_duration_hours
        succ_duration = by_id[relation.successor_activity_pk].exact_duration_hours
        offset = relation.lag_hours
        if relation.relationship_type in {"FS", "FF"}:
            offset += pred_duration
        if relation.relationship_type in {"FF", "SF"}:
            offset -= succ_duration
        outgoing[relation.predecessor_activity_pk].append((relation.successor_activity_pk, offset))
        edges.append((relation.predecessor_activity_pk, relation.successor_activity_pk))
    latest = {}
    for key in reversed(topological_sort(by_id, edges)):
        bounds = [horizon - by_id[key].exact_duration_hours]
        bounds.extend(latest[successor] - offset for successor, offset in outgoing[key])
        latest[key] = min(bounds)
    enriched = []
    tolerance = Decimal("0.000000001")
    for result in results:
        key = result.activity_pk
        total_float = latest[key] - early[key]
        if abs(total_float) < tolerance:
            total_float = Decimal(0)
        gaps = [early[successor] - early[key] - offset for successor, offset in outgoing[key]]
        # Every activity is also constrained to finish by the project finish.
        gaps.append(horizon - early[key] - result.exact_duration_hours)
        free_float = min(gaps)
        if abs(free_float) < tolerance:
            free_float = Decimal(0)
        late_start = add_working_hours(origin, latest[key], calendar)
        if result.exact_duration_hours:
            late_start = next_working_time(late_start, calendar)
        late_finish = add_working_hours(late_start, result.exact_duration_hours, calendar)
        cpm = {
            "basis": "single_calendar_planned_finish",
            "late_start": late_start.isoformat(), "late_finish": late_finish.isoformat(),
            "total_float_hours": str(total_float), "free_float_hours": str(free_float),
            "total_float_days": str(total_float / calendar.working_hours_per_day),
            "critical": total_float <= tolerance,
        }
        enriched.append(replace(result, calculation_trace={**result.calculation_trace, "cpm": cpm}))
    return tuple(enriched), ()
