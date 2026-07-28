from __future__ import annotations

import pytest

from construction_ai_scheduling.domain.errors import InputValidationError


def test_create_project_round_trips_through_sqlite(project_service, valid_project_input):
    created = project_service.create_project(valid_project_input)
    stored = project_service.get_project(created.project_id)

    assert stored == created
    assert stored.name == "Test Project"
    assert stored.currency == "SAR"
    assert stored.working_weekdays[0] == "saturday"


def test_project_id_is_system_generated_not_taken_from_input(project_service, valid_project_input):
    valid_project_input["project_id"] = "USER-SUPPLIED"
    created = project_service.create_project(valid_project_input)
    assert created.project_id.startswith("PRJ-")
    assert created.project_id != "USER-SUPPLIED"


def test_missing_project_fields_are_not_fabricated(project_service, valid_project_input):
    valid_project_input["client"] = ""
    valid_project_input["time_zone"] = ""
    with pytest.raises(InputValidationError) as caught:
        project_service.create_project(valid_project_input)
    assert {issue.field for issue in caught.value.issues} >= {"client", "time_zone"}
    assert project_service.list_projects() == []


def test_completion_date_must_not_precede_start(project_service, valid_project_input):
    valid_project_input["required_completion_date"] = valid_project_input["planned_start_date"].replace(year=2025)
    with pytest.raises(InputValidationError) as caught:
        project_service.create_project(valid_project_input)
    assert "DATE_ORDER" in {issue.code for issue in caught.value.issues}


def test_weekday_count_must_match_declared_working_days(project_service, valid_project_input):
    valid_project_input["working_days_per_week"] = 5
    with pytest.raises(InputValidationError) as caught:
        project_service.create_project(valid_project_input)
    assert "WORKDAY_COUNT_MISMATCH" in {issue.code for issue in caught.value.issues}


def test_invalid_time_zone_is_rejected(project_service, valid_project_input):
    valid_project_input["time_zone"] = "Not/AZone"
    with pytest.raises(InputValidationError) as caught:
        project_service.create_project(valid_project_input)
    assert "TIME_ZONE_INVALID" in {issue.code for issue in caught.value.issues}
