from __future__ import annotations

from copy import deepcopy

from construction_ai_orchestrator.policies.engine import SCHEDULE, AccuracyPolicyEngine


def valid_schedule():
    return {
        "schedule_id": "SCH-001",
        "project_id": "P-001",
        "version": "1.0",
        "data_date": "2026-07-26T08:00:00+03:00",
        "status": "release_candidate",
        "wbs": [
            {"wbs_id": "WBS-ROOT", "name": "Project", "parent_wbs_id": None, "level": 0, "description": None, "responsible_role": None, "status": "validated", "evidence_ids": []},
            {"wbs_id": "WBS-EXEC", "name": "Execution", "parent_wbs_id": "WBS-ROOT", "level": 1, "description": None, "responsible_role": "Construction Manager", "status": "validated", "evidence_ids": []},
        ],
        "calendars": [
            {"calendar_id": "CAL-01", "name": "Six day", "time_zone": "Asia/Riyadh", "hours_per_day": 8, "working_days": ["saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"], "exceptions": []}
        ],
        "activities": [
            {"activity_id": "A-START", "wbs_id": "WBS-EXEC", "name": "Start", "activity_type": "start_milestone", "duration_hours": 0, "calendar_id": "CAL-01", "status": "not_started", "planned_start": "2026-08-01T08:00:00+03:00", "planned_finish": "2026-08-01T08:00:00+03:00", "relationships": [], "evidence_ids": []},
            {"activity_id": "A-WORK", "wbs_id": "WBS-EXEC", "name": "Work", "activity_type": "task_dependent", "duration_hours": 80, "calendar_id": "CAL-01", "status": "not_started", "planned_start": "2026-08-01T08:00:00+03:00", "planned_finish": "2026-08-12T17:00:00+03:00", "relationships": [{"predecessor_activity_id": "A-START", "type": "FS", "lag_hours": 0}], "evidence_ids": []},
            {"activity_id": "A-FINISH", "wbs_id": "WBS-EXEC", "name": "Finish", "activity_type": "finish_milestone", "duration_hours": 0, "calendar_id": "CAL-01", "status": "not_started", "planned_start": "2026-08-12T17:00:00+03:00", "planned_finish": "2026-08-12T17:00:00+03:00", "relationships": [{"predecessor_activity_id": "A-WORK", "type": "FS", "lag_hours": 0}], "evidence_ids": []},
        ],
    }


def test_complete_schedule_logic_passes(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(SCHEDULE, valid_schedule())
    assert report.blockers == ()
    assert report.warnings == ()


def test_schedule_cycle_is_blocked(catalog):
    schedule = valid_schedule()
    schedule["activities"][0]["relationships"] = [{"predecessor_activity_id": "A-FINISH", "type": "FS", "lag_hours": 0}]
    report = AccuracyPolicyEngine(catalog).evaluate(SCHEDULE, schedule)
    assert "SCHEDULE_LOGIC_CYCLE" in {item["code"] for item in report.blockers}


def test_missing_calendar_is_blocked(catalog):
    schedule = valid_schedule()
    schedule["activities"][1]["calendar_id"] = "CAL-MISSING"
    report = AccuracyPolicyEngine(catalog).evaluate(SCHEDULE, schedule)
    assert "ACTIVITY_CALENDAR_MISSING" in {item["code"] for item in report.blockers}


def test_negative_and_excessive_lag_require_review(catalog):
    schedule = valid_schedule()
    schedule["activities"][1]["relationships"][0]["lag_hours"] = -120
    report = AccuracyPolicyEngine(catalog).evaluate(SCHEDULE, schedule)
    assert {item["code"] for item in report.warnings} == {
        "RELATIONSHIP_EXCESSIVE_LAG",
        "RELATIONSHIP_NEGATIVE_LAG",
    }


def test_reversed_activity_dates_are_blocked(catalog):
    schedule = deepcopy(valid_schedule())
    schedule["activities"][1]["planned_finish"] = "2026-07-31T17:00:00+03:00"
    report = AccuracyPolicyEngine(catalog).evaluate(SCHEDULE, schedule)
    assert "ACTIVITY_DATES_REVERSED" in {item["code"] for item in report.blockers}
