"""Project creation and saved-project summary view."""

from __future__ import annotations

import streamlit as st

from construction_ai_scheduling.application.project_service import ProjectService
from construction_ai_scheduling.domain.errors import InputValidationError

WEEKDAY_OPTIONS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def _render_project_summary(project) -> None:
    st.subheader("Active project")
    first, second, third = st.columns(3)
    first.metric("Project", project.name)
    second.metric("Client", project.client)
    third.metric("Currency", project.currency)
    st.caption(
        f"{project.project_id} · {project.location} · "
        f"{project.planned_start_date.isoformat()} to {project.required_completion_date.isoformat()}"
    )


def render_project_page(project_service: ProjectService, active_project_id: str | None) -> None:
    st.header("Project setup")
    st.write("Create a controlled local project record before importing a BOQ. No example values are prefilled.")

    if active_project_id:
        project = project_service.get_project(active_project_id)
        if project:
            _render_project_summary(project)
            st.divider()

    with st.form("create_project_form", clear_on_submit=False):
        st.subheader("Create a new project")
        left, right = st.columns(2)
        with left:
            name = st.text_input("Project name *")
            client = st.text_input("Client *")
            contractor = st.text_input("Contractor *")
            consultant = st.text_input("Consultant *")
            project_type = st.text_input("Project type *")
            location = st.text_input("Location *")
            currency = st.text_input("Currency *", max_chars=3, help="Three-letter code, for example SAR or USD.")
            unit_system = st.selectbox(
                "Unit system *",
                ["SI", "imperial", "mixed"],
                index=None,
                placeholder="Select a unit system",
            )
        with right:
            planned_start_date = st.date_input("Planned start date *", value=None)
            required_completion_date = st.date_input("Required completion date *", value=None)
            working_days_per_week = st.number_input(
                "Working days per week *",
                min_value=1,
                max_value=7,
                value=None,
                step=1,
            )
            working_hours_per_day = st.number_input(
                "Working hours per day *",
                min_value=0.25,
                max_value=24.0,
                value=None,
                step=0.25,
            )
            working_weekdays = st.multiselect(
                "Actual working weekdays *",
                WEEKDAY_OPTIONS,
                help="The number selected must match working days per week.",
            )
            workday_start_time = st.text_input("Workday start time *", placeholder="HH:MM", max_chars=5)
            time_zone = st.text_input("IANA time zone *", placeholder="Example: Asia/Riyadh")

        submitted = st.form_submit_button("Create project", type="primary")

    if not submitted:
        return
    try:
        project = project_service.create_project({
            "name": name,
            "client": client,
            "contractor": contractor,
            "consultant": consultant,
            "project_type": project_type,
            "location": location,
            "planned_start_date": planned_start_date,
            "required_completion_date": required_completion_date,
            "working_days_per_week": working_days_per_week,
            "working_hours_per_day": working_hours_per_day,
            "working_weekdays": working_weekdays,
            "workday_start_time": workday_start_time,
            "currency": currency,
            "unit_system": unit_system,
            "time_zone": time_zone,
        })
    except InputValidationError as exc:
        st.error("Project was not saved. Correct the fields below.")
        for issue in exc.issues:
            st.warning(f"{issue.field}: {issue.message}")
        return

    st.session_state.active_project_id = project.project_id
    st.success(f"Project '{project.name}' was saved locally.")
    st.rerun()
