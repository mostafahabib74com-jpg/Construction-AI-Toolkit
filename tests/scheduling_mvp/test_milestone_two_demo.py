from __future__ import annotations

import json
from decimal import Decimal

from construction_ai_scheduling.application.activity_service import ActivityService
from construction_ai_scheduling.application.calendar_service import CalendarService
from construction_ai_scheduling.application.project_service import ProjectService
from construction_ai_scheduling.application.relationship_service import RelationshipService
from construction_ai_scheduling.application.schedule_service import ScheduleService
from construction_ai_scheduling.application.schedule_workspace_service import ScheduleWorkspaceService
from construction_ai_scheduling.application.wbs_service import WBSService


def test_synthetic_milestone_two_demo_runs_end_to_end(scheduling_repository, catalog, repo_root):
    sample_root = repo_root / "apps/scheduling-mvp/sample_data"
    project_data = json.loads((sample_root / "sample_project.json").read_text(encoding="utf-8"))
    schedule_data = json.loads((sample_root / "milestone_2_demo_schedule.json").read_text(encoding="utf-8"))
    assert project_data["demonstration_data"] is True
    assert schedule_data["demonstration_data"] is True
    assert "not for construction" in schedule_data["notice"].lower()

    project = ProjectService(scheduling_repository, catalog).create_project(project_data["project_input"])
    workspace = ScheduleWorkspaceService(scheduling_repository, catalog).ensure_for_project(project.project_id)
    wbs_service = WBSService(scheduling_repository, catalog)
    calendar_service = CalendarService(scheduling_repository, catalog)
    activity_service = ActivityService(scheduling_repository, catalog)
    relationship_service = RelationshipService(scheduling_repository, catalog)

    wbs_by_code = {}
    for item in schedule_data["wbs"]:
        node = wbs_service.save(
            schedule_id=workspace.schedule_id,
            code=item["code"],
            name=item["name"],
            parent_wbs_id=wbs_by_code.get(item["parent_code"]),
            sort_order=item["sort_order"],
        )
        wbs_by_code[item["code"]] = node.wbs_id

    calendar_input = schedule_data["calendar"]
    calendar = calendar_service.save(schedule_id=workspace.schedule_id, **calendar_input)
    activities_by_code = {}
    for item in schedule_data["activities"]:
        activity = activity_service.save(
            schedule_id=workspace.schedule_id,
            activity_id=item["activity_id"],
            activity_name=item["activity_name"],
            activity_type=item["activity_type"],
            quantity=item["quantity"],
            unit=item["unit"],
            normalized_unit=item["normalized_unit"],
            wbs_id=wbs_by_code[item["wbs_code"]],
            productivity_rate=item["productivity_rate"],
            productivity_basis=item["productivity_basis"],
            crew_count=item["crew_count"],
            calendar_id=calendar.calendar_id,
            notes="Synthetic demonstration activity.",
            assumptions=[],
            sort_order=item["sort_order"],
        )
        activities_by_code[item["activity_id"]] = activity.activity_pk

    for item in schedule_data["relationships"]:
        relationship_service.save(
            schedule_id=workspace.schedule_id,
            predecessor_activity_pk=activities_by_code[item["predecessor"]],
            successor_activity_pk=activities_by_code[item["successor"]],
            relationship_type=item["type"],
            lag_hours=item["lag_hours"],
        )

    run = ScheduleService(scheduling_repository, catalog).calculate(workspace.schedule_id)

    assert run.status == "calculated"
    assert len(run.results) == 5
    assert run.validation_issues == ()
    excavation = next(item for item in run.results if item.activity_pk == activities_by_code["DEMO-A1010"])
    assert excavation.exact_duration_days == Decimal("6")
    assert excavation.exact_duration_hours == Decimal("48")
    assert run.project_planned_finish is not None
    assert run.completion_variance_days < 0
