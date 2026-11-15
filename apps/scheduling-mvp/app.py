"""Streamlit entry point for Phase 8 construction scheduling."""

from __future__ import annotations

import streamlit as st

from construction_ai_orchestrator.validation import SchemaCatalog
from construction_ai_scheduling.application.activity_service import ActivityService
from construction_ai_scheduling.application.boq_service import BOQService
from construction_ai_scheduling.application.calendar_service import CalendarService
from construction_ai_scheduling.application.project_service import ProjectService
from construction_ai_scheduling.application.relationship_service import RelationshipService
from construction_ai_scheduling.application.schedule_service import ScheduleService
from construction_ai_scheduling.application.schedule_workspace_service import ScheduleWorkspaceService
from construction_ai_scheduling.application.wbs_service import WBSService
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository
from construction_ai_scheduling.settings import load_settings
from construction_ai_scheduling.ui.boq_page import render_boq_page
from construction_ai_scheduling.ui.project_page import render_project_page
from construction_ai_scheduling.ui.schedule_page import SchedulingServices, render_schedule_page
from construction_ai_scheduling.ui.estimating_page import render_estimating_page
from construction_ai_scheduling.ui.library_page import render_library_page
from construction_ai_scheduling.application.demo_service import create_demo


@st.cache_resource
def build_services(database_path: str) -> SchedulingServices:
    settings = load_settings()
    repository = SQLiteRepository(database_path, settings.migration_path)
    repository.initialize()
    catalog = SchemaCatalog.from_directory(settings.schema_root)
    return SchedulingServices(
        project=ProjectService(repository, catalog),
        boq=BOQService(repository, catalog),
        workspace=ScheduleWorkspaceService(repository, catalog),
        wbs=WBSService(repository, catalog),
        calendar=CalendarService(repository, catalog),
        activity=ActivityService(repository, catalog),
        relationship=RelationshipService(repository, catalog),
        schedule=ScheduleService(repository, catalog),
    )


def main() -> None:
    st.set_page_config(page_title="Construction AI Toolkit", page_icon="🏗️", layout="wide")
    settings = load_settings()
    services = build_services(str(settings.database_path))

    st.title("Construction AI Toolkit")
    st.caption("Planning, estimating and engineering workflows / التخطيط والتسعير والمهارات الهندسية")

    if st.sidebar.button("Create synthetic demo / تجربة البرنامج"):
        try:
            project = create_demo(services, settings.repo_root)
        except Exception as exc:
            st.error(f"Demo setup failed: {exc}")
        else:
            st.session_state.active_project_id = project.project_id
            st.rerun()

    projects = services.project.list_projects()
    project_ids = [project.project_id for project in projects]
    current = st.session_state.get("active_project_id")
    requested_project = st.query_params.get("project")
    if current not in project_ids and requested_project in project_ids:
        current = requested_project
    project_index = project_ids.index(current) + 1 if current in project_ids else 0
    selected = st.sidebar.selectbox(
        "Active project",
        [None, *project_ids],
        index=project_index,
        format_func=lambda project_id: "No project selected" if project_id is None else next(
            project.name for project in projects if project.project_id == project_id
        ),
    )
    st.session_state.active_project_id = selected
    pages = ["Project setup", "BOQ import and review", "Schedule workspace", "Estimating", "Engineering workflows"]
    requested_view = {"boq": "BOQ import and review", "schedule": "Schedule workspace", "estimate": "Estimating", "workflows": "Engineering workflows"}.get(st.query_params.get("view"), "Project setup")
    page = st.sidebar.radio("Workspace", pages, index=pages.index(requested_view))
    st.sidebar.caption("Saved projects, Gantt, CSV/Excel exports and sourced unit-rate analysis. Use the demo button for a separate synthetic project.")
    if selected and next(project.name for project in projects if project.project_id == selected).startswith("DEMO -"):
        st.warning("SYNTHETIC DEMO / بيانات تجريبية — quantities, productivity and prices are arithmetic examples, not project or market data.")
    if selected and next(project.name for project in projects if project.project_id == selected).startswith("TRIAL -"):
        st.warning("IMPORT TRIAL / تجربة استيراد: BOQ quantities come from the source file. Project dates and parties are trial placeholders; no actual programme or final price is approved.")

    if page == "Project setup":
        render_project_page(services.project, selected)
    elif page == "BOQ import and review":
        render_boq_page(services.boq, services.project, selected)
    elif page == "Schedule workspace":
        render_schedule_page(services, selected)
    elif page == "Estimating":
        render_estimating_page(services, selected)
    else:
        render_library_page(settings.repo_root)


if __name__ == "__main__":
    main()
