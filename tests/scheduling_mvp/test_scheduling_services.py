from __future__ import annotations

from decimal import Decimal

from construction_ai_scheduling.application.activity_service import ActivityService
from construction_ai_scheduling.application.boq_service import BOQService
from construction_ai_scheduling.application.calendar_service import CalendarService
from construction_ai_scheduling.application.relationship_service import RelationshipService
from construction_ai_scheduling.application.schedule_service import ScheduleService
from construction_ai_scheduling.application.schedule_workspace_service import ScheduleWorkspaceService
from construction_ai_scheduling.application.wbs_service import WBSService


def _services(repository, catalog):
    return (
        ScheduleWorkspaceService(repository, catalog),
        WBSService(repository, catalog),
        CalendarService(repository, catalog),
        ActivityService(repository, catalog),
        RelationshipService(repository, catalog),
        ScheduleService(repository, catalog),
    )


def test_boq_conversion_is_explicit_valid_only_and_does_not_assume_productivity(
    scheduling_repository, catalog, saved_project
):
    workspace_service, _, _, activity_service, _, _ = _services(scheduling_repository, catalog)
    workspace = workspace_service.ensure_for_project(saved_project.project_id)
    boq_service = BOQService(scheduling_repository, catalog)
    preview = boq_service.preview(
        "boq.csv",
        "Description,Quantity,Unit\nConcrete,10,m3\nMissing quantity,,m2\n".encode(),
    )
    batch = boq_service.import_boq(
        project_id=saved_project.project_id,
        file_name="boq.csv",
        preview=preview,
        mapping={"item_code": None, "description": "Description", "quantity": "Quantity", "unit": "Unit"},
    )

    result = activity_service.convert_boq_rows(workspace.schedule_id, batch.import_id, [item.row_id for item in batch.rows])

    assert len(result.created) == 1
    assert result.skipped_row_ids == (batch.rows[1].row_id,)
    assert result.created[0].quantity == Decimal("10.0")
    assert result.created[0].productivity_rate is None
    assert result.created[0].crew_count is None
    assert result.created[0].calendar_id is None


def test_split_activity_leaves_quantity_for_user_allocation(scheduling_repository, catalog, saved_project):
    workspace_service, _, _, activity_service, _, _ = _services(scheduling_repository, catalog)
    workspace = workspace_service.ensure_for_project(saved_project.project_id)
    source = activity_service.save(
        schedule_id=workspace.schedule_id,
        activity_id="A1000",
        activity_name="Concrete",
        activity_type="task_dependent",
        quantity="100",
        unit="m3",
        normalized_unit="m3",
        wbs_id=None,
        productivity_rate=None,
        productivity_basis=None,
        crew_count=None,
        calendar_id=None,
        notes=None,
        assumptions=[],
        sort_order=0,
    )

    split = activity_service.create_split_activity(source.activity_pk, activity_id="A1010", activity_name="Zone 2")

    assert split.quantity is None
    assert split.productivity_rate is None
    assert "requires user input" in split.notes


def test_schedule_service_persists_blocked_then_calculated_immutable_runs(
    scheduling_repository, catalog, saved_project
):
    workspace_service, wbs_service, calendar_service, activity_service, relationship_service, schedule_service = _services(
        scheduling_repository, catalog
    )
    workspace = workspace_service.ensure_for_project(saved_project.project_id)

    blocked = schedule_service.calculate(workspace.schedule_id)
    assert blocked.status == "blocked"
    assert {item["code"] for item in blocked.validation_issues} == {"ACTIVITIES_REQUIRED"}

    wbs = wbs_service.save(schedule_id=workspace.schedule_id, code="1", name="Execution", parent_wbs_id=None, sort_order=0)
    calendar = calendar_service.create_from_project(workspace.schedule_id)
    start = activity_service.save(
        schedule_id=workspace.schedule_id,
        activity_id="A1000",
        activity_name="Project start",
        activity_type="start_milestone",
        quantity=None,
        unit=None,
        normalized_unit=None,
        wbs_id=wbs.wbs_id,
        productivity_rate=None,
        productivity_basis=None,
        crew_count=None,
        calendar_id=calendar.calendar_id,
        notes=None,
        assumptions=[],
        sort_order=0,
    )
    task = activity_service.save(
        schedule_id=workspace.schedule_id,
        activity_id="A1010",
        activity_name="Foundation work",
        activity_type="task_dependent",
        quantity="8",
        unit="m3",
        normalized_unit="m3",
        wbs_id=wbs.wbs_id,
        productivity_rate="1",
        productivity_basis="per_hour",
        crew_count=1,
        calendar_id=calendar.calendar_id,
        notes=None,
        assumptions=[],
        sort_order=1,
    )
    relationship_service.save(
        schedule_id=workspace.schedule_id,
        predecessor_activity_pk=start.activity_pk,
        successor_activity_pk=task.activity_pk,
        relationship_type="FS",
        lag_hours="0",
    )

    calculated = schedule_service.calculate(workspace.schedule_id)

    assert calculated.status == "calculated"
    assert len(calculated.results) == 2
    assert calculated.run_id != blocked.run_id
    with scheduling_repository._connect() as connection:
        assert connection.execute("SELECT COUNT(*) FROM schedule_runs").fetchone()[0] == 2
    assert schedule_service.latest_run(workspace.schedule_id) == calculated


def test_relationship_service_blocks_cycles(scheduling_repository, catalog, saved_project):
    workspace_service, _, _, activity_service, relationship_service, _ = _services(scheduling_repository, catalog)
    workspace = workspace_service.ensure_for_project(saved_project.project_id)
    activities = [
        activity_service.save(
            schedule_id=workspace.schedule_id,
            activity_id=f"A10{index}",
            activity_name=f"Activity {index}",
            activity_type="start_milestone",
            quantity=None,
            unit=None,
            normalized_unit=None,
            wbs_id=None,
            productivity_rate=None,
            productivity_basis=None,
            crew_count=None,
            calendar_id=None,
            notes=None,
            assumptions=[],
            sort_order=index,
        )
        for index in range(2)
    ]
    relationship_service.save(
        schedule_id=workspace.schedule_id,
        predecessor_activity_pk=activities[0].activity_pk,
        successor_activity_pk=activities[1].activity_pk,
        relationship_type="FS",
        lag_hours="0",
    )

    import pytest

    with pytest.raises(Exception, match="cycle"):
        relationship_service.save(
            schedule_id=workspace.schedule_id,
            predecessor_activity_pk=activities[1].activity_pk,
            successor_activity_pk=activities[0].activity_pk,
            relationship_type="FS",
            lag_hours="0",
        )
