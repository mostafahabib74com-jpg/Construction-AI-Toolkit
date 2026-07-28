from __future__ import annotations

from streamlit.testing.v1 import AppTest

from construction_ai_orchestrator.validation import SchemaCatalog
from construction_ai_scheduling.application.project_service import ProjectService
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository


def test_streamlit_application_loads_project_setup(tmp_path, monkeypatch, repo_root):
    monkeypatch.setenv("CONSTRUCTION_AI_DB_PATH", str(tmp_path / "streamlit.db"))
    app = AppTest.from_file(str(repo_root / "apps/scheduling-mvp/app.py"), default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "Construction AI Toolkit"
    assert app.header[0].value == "Project setup"
    assert app.sidebar.radio[0].value == "Project setup"

    app.sidebar.radio[0].set_value("BOQ import and review").run()
    assert not app.exception
    assert app.header[0].value == "BOQ import and review"
    assert "Create or select a saved project" in app.warning[0].value


def test_streamlit_application_loads_milestone_two_workspace(
    tmp_path, monkeypatch, repo_root, valid_project_input
):
    database_path = tmp_path / "streamlit-schedule.db"
    monkeypatch.setenv("CONSTRUCTION_AI_DB_PATH", str(database_path))
    repository = SQLiteRepository(database_path, repo_root / "apps/scheduling-mvp/migrations/001_initial.sql")
    repository.initialize()
    catalog = SchemaCatalog.from_directory(repo_root / "packages/contracts/schemas")
    project = ProjectService(repository, catalog).create_project(valid_project_input)

    app = AppTest.from_file(str(repo_root / "apps/scheduling-mvp/app.py"), default_timeout=15).run()
    app.sidebar.selectbox[0].set_value(project.project_id)
    app.sidebar.radio[0].set_value("Schedule workspace").run()

    assert not app.exception
    assert app.header[0].value == "Schedule workspace"
    assert [tab.label for tab in app.tabs] == [
        "Overview",
        "WBS",
        "Calendars",
        "Activities",
        "Relationships",
        "Calculate & review",
    ]
    assert "does not calculate float or critical path" in app.info[0].value
