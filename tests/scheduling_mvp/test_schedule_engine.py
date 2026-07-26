from __future__ import annotations

from dataclasses import replace
from datetime import datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.schedule_engine import calculate_forward_pass
from construction_ai_scheduling.domain.schedule_models import (
    ActivityRelationship,
    ProjectCalendar,
    ScheduleActivity,
    ScheduleWorkspace,
    WBSNode,
)


ZONE = ZoneInfo("Asia/Riyadh")
NOW = datetime(2026, 9, 1, 7, tzinfo=ZONE)


def _inputs(project):
    workspace = ScheduleWorkspace(
        "SCH-1", project.project_id, "Draft", "D1", "draft", "forward_pass", 2, "ROUND_HALF_UP", NOW, NOW
    )
    wbs = WBSNode("WBS-1", "SCH-1", "1", "Execution", None, 0, None, NOW, NOW)
    calendar = ProjectCalendar(
        "CAL-1",
        "SCH-1",
        "6D-8H",
        "Six day",
        "Asia/Riyadh",
        ("saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"),
        time(7),
        Decimal("8"),
        (),
        (),
        NOW,
        NOW,
    )
    predecessor = ScheduleActivity(
        "ACT-1", "SCH-1", "A1000", "Predecessor", "task_dependent", None, None, None, None,
        Decimal("8"), "unit", "count", wbs.wbs_id, Decimal("1"), "per_hour", 1, calendar.calendar_id,
        None, (), 0, NOW, NOW
    )
    successor = ScheduleActivity(
        "ACT-2", "SCH-1", "A1010", "Successor", "task_dependent", None, None, None, None,
        Decimal("4"), "unit", "count", wbs.wbs_id, Decimal("1"), "per_hour", 1, calendar.calendar_id,
        None, (), 1, NOW, NOW
    )
    return workspace, [wbs], [calendar], [predecessor, successor]


@pytest.mark.parametrize(
    ("relationship_type", "lag", "expected_start", "expected_finish"),
    [
        ("FS", "0", datetime(2026, 9, 2, 7, tzinfo=ZONE), datetime(2026, 9, 2, 11, tzinfo=ZONE)),
        ("SS", "2", datetime(2026, 9, 1, 9, tzinfo=ZONE), datetime(2026, 9, 1, 13, tzinfo=ZONE)),
        ("FF", "0", datetime(2026, 9, 1, 11, tzinfo=ZONE), datetime(2026, 9, 1, 15, tzinfo=ZONE)),
        ("SF", "4", datetime(2026, 9, 1, 7, tzinfo=ZONE), datetime(2026, 9, 1, 11, tzinfo=ZONE)),
    ],
)
def test_forward_pass_supports_all_relationship_types(
    saved_project, relationship_type, lag, expected_start, expected_finish
):
    workspace, wbs, calendars, activities = _inputs(saved_project)
    relationship = ActivityRelationship(
        "REL-1", "SCH-1", "ACT-1", "ACT-2", relationship_type, Decimal(lag), None, NOW
    )

    result = calculate_forward_pass(
        project=saved_project,
        workspace=workspace,
        wbs_nodes=wbs,
        calendars=calendars,
        activities=activities,
        relationships=[relationship],
    )

    successor = next(item for item in result.results if item.activity_pk == "ACT-2")
    assert successor.early_start == expected_start
    assert successor.early_finish == expected_finish
    assert result.completion_variance_days == (result.project_planned_finish.date() - saved_project.required_completion_date).days


def test_negative_lag_uses_successor_calendar(saved_project):
    workspace, wbs, calendars, activities = _inputs(saved_project)
    relationship = ActivityRelationship("REL-1", "SCH-1", "ACT-1", "ACT-2", "FS", Decimal("-2"), None, NOW)

    result = calculate_forward_pass(
        project=saved_project,
        workspace=workspace,
        wbs_nodes=wbs,
        calendars=calendars,
        activities=activities,
        relationships=[relationship],
    )

    successor = next(item for item in result.results if item.activity_pk == "ACT-2")
    assert successor.early_start == datetime(2026, 9, 1, 13, tzinfo=ZONE)
    assert {item["code"] for item in result.validation_issues} == {"RELATIONSHIP_NEGATIVE_LAG"}


def test_cycle_and_missing_inputs_block_calculation(saved_project):
    workspace, wbs, calendars, activities = _inputs(saved_project)
    activities[1] = replace(activities[1], productivity_rate=None)
    relationships = [
        ActivityRelationship("R1", "SCH-1", "ACT-1", "ACT-2", "FS", Decimal("0"), None, NOW),
        ActivityRelationship("R2", "SCH-1", "ACT-2", "ACT-1", "FS", Decimal("0"), None, NOW),
    ]

    with pytest.raises(SchedulingInputError) as caught:
        calculate_forward_pass(
            project=saved_project,
            workspace=workspace,
            wbs_nodes=wbs,
            calendars=calendars,
            activities=activities,
            relationships=relationships,
        )

    assert {item["code"] for item in caught.value.issues} >= {"PRODUCTIVITY_REQUIRED", "SCHEDULE_LOGIC_CYCLE"}


def test_milestone_needs_no_quantity_or_productivity(saved_project):
    workspace, wbs, calendars, activities = _inputs(saved_project)
    milestone = replace(
        activities[0],
        activity_type="start_milestone",
        quantity=None,
        productivity_rate=None,
        productivity_basis=None,
        crew_count=None,
    )

    result = calculate_forward_pass(
        project=saved_project,
        workspace=workspace,
        wbs_nodes=wbs,
        calendars=calendars,
        activities=[milestone],
        relationships=[],
    )

    assert result.results[0].early_start == result.results[0].early_finish == datetime(2026, 9, 1, 7, tzinfo=ZONE)
