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
    st.set_page_config(page_title="Construction Scheduling MVP", page_icon="🏗️", layout="wide")
    settings = load_settings()
    services = build_services(str(settings.database_path))

    st.title("Construction AI Toolkit")
    st.caption("Phase 8 · Construction Project Scheduling MVP · Milestone 2")

    projects = services.project.list_projects()
    project_ids = [project.project_id for project in projects]
    current = st.session_state.get("active_project_id")
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
    page = st.sidebar.radio("Milestone 2", ["Project setup", "BOQ import and review", "Schedule workspace"])
    st.sidebar.caption(
        "Forward scheduling is enabled. Gantt, exports, resource loading, and cost loading are not included."
    )

    if page == "Project setup":
        render_project_page(services.project, selected)
    elif page == "BOQ import and review":
        render_boq_page(services.boq, services.project, selected)
    else:
        render_schedule_page(services, selected)


if __name__ == "__main__":
    main()
