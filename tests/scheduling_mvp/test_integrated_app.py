from dataclasses import replace
from io import BytesIO
import json

from openpyxl import load_workbook
from streamlit.testing.v1 import AppTest

from construction_ai_scheduling.application.demo_service import create_demo
from construction_ai_scheduling.application.schedule_exports import csv_bytes, schedule_rows, schedule_workbook
from construction_ai_scheduling.domain.estimating import calculate_estimate


def services_for(repo_root, database_path):
    # Load the same application composition used by the local UI.
    import importlib.util
    spec = importlib.util.spec_from_file_location("integrated_app", repo_root / "apps/scheduling-mvp/app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_services(str(database_path))


def test_demo_produces_reproducible_schedule_estimate_and_arabic_workbook(tmp_path, repo_root):
    services = services_for(repo_root, tmp_path / "demo.db")
    project = create_demo(services, repo_root)
    workspace = services.workspace.ensure_for_project(project.project_id)
    run = services.schedule.latest_run(workspace.schedule_id)
    assert run.status == "calculated"
    assert services.schedule.is_current(run)
    assert len(schedule_rows(run)) == 5
    workbook = load_workbook(BytesIO(schedule_workbook(run)))
    assert {"Schedule", "Relationships", "Calendars", "Run metadata"} <= set(workbook.sheetnames)
    payload = services.schedule.repository.get_estimate_draft(project.project_id)
    result = calculate_estimate(payload, project.currency)
    assert result["summary"]["Direct cost"] == "1000.00"
    assert result["summary"]["Total including tax"] == "1250.00"
    assert "بند تجريبي" in payload["items"][0]["description"]


def test_saved_run_survives_edits_and_deleted_activity(tmp_path, repo_root):
    services = services_for(repo_root, tmp_path / "history.db")
    project = create_demo(services, repo_root)
    workspace = services.workspace.ensure_for_project(project.project_id)
    original = services.schedule.latest_run(workspace.schedule_id)
    original_csv = csv_bytes(schedule_rows(original))
    activity = services.activity.list(workspace.schedule_id)[0]
    services.schedule.repository.save_activity(replace(activity, activity_name="Changed after calculation"))
    assert not services.schedule.is_current(original)
    for relationship in services.relationship.list(workspace.schedule_id):
        services.relationship.delete(relationship.relationship_id)
    services.activity.delete(activity.activity_pk)
    saved = services.schedule.latest_run(workspace.schedule_id)
    assert saved == original
    assert csv_bytes(schedule_rows(saved)) == original_csv


def test_exports_neutralize_spreadsheet_formulas_without_losing_arabic():
    from construction_ai_scheduling.application.schedule_exports import workbook_bytes
    rows = [{"Name": '=HYPERLINK("bad")', "Description": "خرسانة"}]
    csv = csv_bytes(rows).decode("utf-8-sig")
    assert "'=HYPERLINK" in csv
    assert "خرسانة" in csv
    workbook = load_workbook(BytesIO(workbook_bytes({"Items": rows})))
    assert workbook["Items"]["A2"].data_type == "s"
    assert workbook["Items"]["B2"].value == "خرسانة"


def test_integrated_ui_demo_gantt_estimate_and_workflow_browser(tmp_path, monkeypatch, repo_root):
    monkeypatch.setenv("CONSTRUCTION_AI_DB_PATH", str(tmp_path / "ui.db"))
    app = AppTest.from_file(str(repo_root / "apps/scheduling-mvp/app.py"), default_timeout=25).run()
    app.sidebar.button[0].click().run()
    assert not app.exception
    app.sidebar.radio[0].set_value("Schedule workspace").run()
    assert not app.exception
    assert any("Gantt" in item.value for item in app.subheader)
    assert len(app.get("download_button")) == 3
    app.sidebar.radio[0].set_value("Estimating").run()
    assert not app.exception
    assert any("1250.00" in item.value for item in app.metric)
    app.sidebar.radio[0].set_value("Engineering workflows").run()
    assert not app.exception
    assert app.metric[0].value == "5"
