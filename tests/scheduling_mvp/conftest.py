from __future__ import annotations

from datetime import date

import pytest

from construction_ai_scheduling.application.boq_service import BOQService
from construction_ai_scheduling.application.project_service import ProjectService
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository


@pytest.fixture()
def scheduling_repository(tmp_path, repo_root):
    repository = SQLiteRepository(
        tmp_path / "test.db",
        repo_root / "apps/scheduling-mvp/migrations/001_initial.sql",
    )
    repository.initialize()
    return repository


@pytest.fixture()
def project_service(scheduling_repository, catalog):
    return ProjectService(scheduling_repository, catalog)


@pytest.fixture()
def boq_service(scheduling_repository, catalog):
    return BOQService(scheduling_repository, catalog)


@pytest.fixture()
def valid_project_input():
    return {
        "name": "Test Project",
        "client": "Test Client",
        "contractor": "Test Contractor",
        "consultant": "Test Consultant",
        "project_type": "Building",
        "location": "Riyadh, Saudi Arabia",
        "planned_start_date": date(2026, 9, 1),
        "required_completion_date": date(2027, 8, 31),
        "working_days_per_week": 6,
        "working_hours_per_day": 8.0,
        "working_weekdays": ["saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"],
        "workday_start_time": "07:00",
        "currency": "SAR",
        "unit_system": "SI",
        "time_zone": "Asia/Riyadh",
    }


@pytest.fixture()
def saved_project(project_service, valid_project_input):
    return project_service.create_project(valid_project_input)
