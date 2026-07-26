"""Streamlit entry point for Phase 8 Milestone 1."""

from __future__ import annotations

import streamlit as st

from construction_ai_orchestrator.validation import SchemaCatalog
from construction_ai_scheduling.application.boq_service import BOQService
from construction_ai_scheduling.application.project_service import ProjectService
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository
from construction_ai_scheduling.settings import load_settings
from construction_ai_scheduling.ui.boq_page import render_boq_page
from construction_ai_scheduling.ui.project_page import render_project_page


@st.cache_resource
def build_services(database_path: str):
    settings = load_settings()
    repository = SQLiteRepository(database_path, settings.migration_path)
    repository.initialize()
    catalog = SchemaCatalog.from_directory(settings.schema_root)
    return ProjectService(repository, catalog), BOQService(repository, catalog)


def main() -> None:
    st.set_page_config(page_title="Construction Scheduling MVP", page_icon="🏗️", layout="wide")
    settings = load_settings()
    project_service, boq_service = build_services(str(settings.database_path))

    st.title("Construction AI Toolkit")
    st.caption("Phase 8 · Construction Project Scheduling MVP · Milestone 1")

    projects = project_service.list_projects()
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
    page = st.sidebar.radio("Milestone 1", ["Project setup", "BOQ import and review"])
    st.sidebar.caption("Schedule calculations, Gantt, and exports are not enabled in this milestone.")

    if page == "Project setup":
        render_project_page(project_service, selected)
    else:
        render_boq_page(boq_service, project_service, selected)


if __name__ == "__main__":
    main()
