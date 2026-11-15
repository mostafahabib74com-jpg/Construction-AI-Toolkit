from dataclasses import replace
from decimal import Decimal
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from construction_ai_scheduling.domain.cpm_engine import enrich_with_cpm
from construction_ai_scheduling.domain.schedule_engine import calculate_forward_pass
from construction_ai_scheduling.domain.schedule_models import ActivityRelationship, ProjectCalendar, ScheduleActivity, ScheduleWorkspace, WBSNode


def inputs(project):
    now = datetime(2026, 9, 1, 7, tzinfo=ZoneInfo("Asia/Riyadh"))
    workspace = ScheduleWorkspace("S", project.project_id, "Test", "1", "draft", "forward_pass", 2, "ROUND_HALF_UP", now, now)
    wbs = WBSNode("W", "S", "1", "Test", None, 0, None, now, now)
    calendar = ProjectCalendar("C", "S", "C", "Shared calendar", "Asia/Riyadh", tuple(["saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"]), time(7), Decimal(8), (), (), now, now)
    def activity(key, hours, order):
        return ScheduleActivity(key, "S", key, key, "task_dependent", None, None, None, None,
            Decimal(hours), "unit", "count", "W", Decimal(1), "per_hour", 1, "C", None, (), order, now, now)
    activities = [activity("A", 8, 0), activity("B", 16, 1), activity("C", 8, 2), activity("D", 8, 3)]
    def relation(key, pred, succ, kind="FS", lag="0"):
        return ActivityRelationship(key, "S", pred, succ, kind, Decimal(lag), None, now)
    relations = [relation("R1", "A", "B"), relation("R2", "A", "C"), relation("R3", "B", "D"), relation("R4", "C", "D")]
    return workspace, [wbs], [calendar], activities, relations


def calculate(project, values):
    workspace, wbs, calendars, activities, relationships = values
    forward = calculate_forward_pass(project=project, workspace=workspace, wbs_nodes=wbs, calendars=calendars, activities=activities, relationships=relationships)
    return enrich_with_cpm(forward.results, activities, calendars, relationships)


def test_parallel_branches_have_known_critical_path_and_float(saved_project):
    results, issues = calculate(saved_project, inputs(saved_project))
    assert not issues
    cpm = {item.activity_pk: item.calculation_trace["cpm"] for item in results}
    assert {key for key, value in cpm.items() if value["critical"]} == {"A", "B", "D"}
    assert Decimal(cpm["C"]["total_float_hours"]) == 8
    assert Decimal(cpm["C"]["free_float_hours"]) == 8
    assert cpm["D"]["late_finish"] == results[-1].early_finish.isoformat()


@pytest.mark.parametrize(("kind", "lag", "expected_a", "expected_b"), [("FS", "0", "0", "0"), ("SS", "0", "0", "0"), ("FF", "0", "8", "0"), ("SF", "0", "8", "0"), ("FS", "-4", "0", "0")])
def test_generalized_precedence_float(saved_project, kind, lag, expected_a, expected_b):
    workspace, wbs, calendars, activities, relationships = inputs(saved_project)
    activities = activities[:2]  # A 8h, B 16h
    relation = replace(relationships[0], relationship_type=kind, lag_hours=Decimal(lag))
    results, _ = calculate(saved_project, (workspace, wbs, calendars, activities, [relation]))
    assert [Decimal(item.calculation_trace["cpm"]["total_float_hours"]) for item in results] == [Decimal(expected_a), Decimal(expected_b)]


def test_multi_calendar_schedule_keeps_dates_without_fabricated_float(saved_project):
    workspace, wbs, calendars, activities, relationships = inputs(saved_project)
    calendars.append(replace(calendars[0], calendar_id="C2", code="C2", working_hours_per_day=Decimal(6)))
    activities[2] = replace(activities[2], calendar_id="C2")
    results, issues = calculate(saved_project, (workspace, wbs, calendars, activities, relationships))
    assert issues[0]["code"] == "CPM_MULTIPLE_CALENDARS"
    assert all("cpm" not in item.calculation_trace for item in results)
