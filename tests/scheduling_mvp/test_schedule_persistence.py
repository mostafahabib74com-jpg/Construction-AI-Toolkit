from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal

import pytest

from construction_ai_scheduling.domain.schedule_models import (
    ActivityCalculationResult,
    ActivityRelationship,
    CalendarBreak,
    CalendarException,
    ProjectCalendar,
    ScheduleActivity,
    ScheduleRun,
    ScheduleWorkspace,
    WBSNode,
)


NOW = datetime(2026, 9, 1, 7, 0, tzinfo=timezone.utc)


def _workspace(project_id: str) -> ScheduleWorkspace:
    return ScheduleWorkspace(
        schedule_id="SCH-001",
        project_id=project_id,
        name="Baseline schedule",
        version="DRAFT-1",
        status="draft",
        calculation_mode="forward_pass",
        rounding_precision=2,
        rounding_mode="ROUND_HALF_UP",
        created_at=NOW,
        updated_at=NOW,
    )


def test_schedule_models_preserve_exact_decimal_text():
    activity = ScheduleActivity(
        activity_pk="ACT-PK-1",
        schedule_id="SCH-001",
        activity_id="A1000",
        activity_name="صب الخرسانة",
        activity_type="task_dependent",
        source_boq_row_id=None,
        boq_item_code="C-01",
        boq_description="صب خرسانة الأساسات",
        source_row_number=10,
        quantity=Decimal("120.500"),
        unit="م³",
        normalized_unit="m3",
        wbs_id=None,
        productivity_rate=Decimal("12.50"),
        productivity_basis="per_day",
        crew_count=2,
        calendar_id=None,
        notes=None,
        assumptions=(),
        sort_order=0,
        created_at=NOW,
        updated_at=NOW,
    )

    restored = ScheduleActivity.from_dict(activity.to_dict())

    assert restored.quantity == Decimal("120.500")
    assert restored.productivity_rate == Decimal("12.50")
    assert restored.unit == "م³"


def test_schedule_repository_round_trip(scheduling_repository, saved_project):
    workspace = _workspace(saved_project.project_id)
    scheduling_repository.save_schedule(workspace)
    wbs = WBSNode("WBS-1", workspace.schedule_id, "1", "Preliminaries", None, 0, None, NOW, NOW)
    scheduling_repository.save_wbs_node(wbs)
    calendar = ProjectCalendar(
        calendar_id="CAL-1",
        schedule_id=workspace.schedule_id,
        code="6D-8H",
        name="Six day calendar",
        time_zone="Asia/Riyadh",
        working_weekdays=("saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"),
        workday_start_time=time(7, 0),
        working_hours_per_day=Decimal("8.0"),
        breaks=(CalendarBreak("BRK-1", time(12, 0), time(13, 0)),),
        exceptions=(CalendarException("EX-1", date(2026, 9, 23), False, None, None, "Holiday"),),
        created_at=NOW,
        updated_at=NOW,
    )
    scheduling_repository.save_calendar(calendar)
    activity = ScheduleActivity(
        activity_pk="ACT-PK-1",
        schedule_id=workspace.schedule_id,
        activity_id="A1000",
        activity_name="Foundation concrete",
        activity_type="task_dependent",
        source_boq_row_id=None,
        boq_item_code="C-01",
        boq_description="Foundation concrete",
        source_row_number=10,
        quantity=Decimal("120.500"),
        unit="م³",
        normalized_unit="m3",
        wbs_id=wbs.wbs_id,
        productivity_rate=Decimal("12.50"),
        productivity_basis="per_day",
        crew_count=2,
        calendar_id=calendar.calendar_id,
        notes=None,
        assumptions=(),
        sort_order=0,
        created_at=NOW,
        updated_at=NOW,
    )
    successor = ScheduleActivity.from_dict(
        {**activity.to_dict(), "activity_pk": "ACT-PK-2", "activity_id": "A1010", "activity_name": "Curing"}
    )
    scheduling_repository.save_activity(activity)
    scheduling_repository.save_activity(successor)
    relationship = ActivityRelationship(
        "REL-1", workspace.schedule_id, activity.activity_pk, successor.activity_pk, "FS", Decimal("-4.25"), None, NOW
    )
    scheduling_repository.save_relationship(relationship)
    result = ActivityCalculationResult(
        activity.activity_pk,
        Decimal("38.56"),
        Decimal("4.82"),
        Decimal("4.82"),
        NOW,
        datetime(2026, 9, 5, 13, 33, 36, tzinfo=timezone.utc),
        "quantity / (productivity * crews)",
        {"quantity": "120.500"},
    )
    run = ScheduleRun(
        "RUN-1",
        workspace.schedule_id,
        "2.0.0",
        "calculated",
        NOW,
        result.early_finish,
        -360,
        (),
        (result,),
    )
    scheduling_repository.save_schedule_run(run)

    assert scheduling_repository.get_schedule(workspace.schedule_id) == workspace
    assert scheduling_repository.list_wbs_nodes(workspace.schedule_id) == [wbs]
    assert scheduling_repository.get_calendar(calendar.calendar_id) == calendar
    assert scheduling_repository.list_activities(workspace.schedule_id) == [activity, successor]
    assert scheduling_repository.list_relationships(workspace.schedule_id) == [relationship]
    assert scheduling_repository.latest_schedule_run(workspace.schedule_id) == run


def test_referenced_wbs_and_calendar_are_guarded(scheduling_repository, saved_project):
    workspace = _workspace(saved_project.project_id)
    scheduling_repository.save_schedule(workspace)
    wbs = WBSNode("WBS-1", workspace.schedule_id, "1", "Root", None, 0, None, NOW, NOW)
    scheduling_repository.save_wbs_node(wbs)
    calendar = ProjectCalendar(
        "CAL-1", workspace.schedule_id, "5D", "Calendar", "Asia/Riyadh", ("sunday",), time(8),
        Decimal("8"), (), (), NOW, NOW
    )
    scheduling_repository.save_calendar(calendar)
    activity = ScheduleActivity(
        "ACT-1", workspace.schedule_id, "A1000", "Task", "task_dependent", None, None, None, None,
        Decimal("1"), "m", "m", wbs.wbs_id, Decimal("1"), "per_day", 1, calendar.calendar_id,
        None, (), 0, NOW, NOW
    )
    scheduling_repository.save_activity(activity)

    with pytest.raises(Exception):
        scheduling_repository.delete_wbs_node(wbs.wbs_id)
    with pytest.raises(Exception):
        scheduling_repository.delete_calendar(calendar.calendar_id)
