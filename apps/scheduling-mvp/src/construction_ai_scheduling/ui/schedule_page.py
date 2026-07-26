"""Milestone 2 Streamlit workspace for deterministic forward scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Any

import pandas as pd
import streamlit as st

from construction_ai_scheduling.application.activity_service import ActivityService
from construction_ai_scheduling.application.boq_service import BOQService
from construction_ai_scheduling.application.calendar_service import CalendarService
from construction_ai_scheduling.application.project_service import ProjectService
from construction_ai_scheduling.application.relationship_service import RelationshipService
from construction_ai_scheduling.application.schedule_service import ScheduleService
from construction_ai_scheduling.application.schedule_workspace_service import ScheduleWorkspaceService
from construction_ai_scheduling.application.wbs_service import WBSService
from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.schedule_validation import validate_schedule_inputs


WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
ACTIVITY_TYPES = ["task_dependent", "start_milestone", "finish_milestone"]
RELATIONSHIP_TYPES = ["FS", "SS", "FF", "SF"]


@dataclass(frozen=True, slots=True)
class SchedulingServices:
    project: ProjectService
    boq: BOQService
    workspace: ScheduleWorkspaceService
    wbs: WBSService
    calendar: CalendarService
    activity: ActivityService
    relationship: RelationshipService
    schedule: ScheduleService


def _text_or_none(value: Any) -> str | None:
    if value is None or (not isinstance(value, (list, tuple, dict)) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def _show_error(exc: Exception) -> None:
    st.error(str(exc))
    if isinstance(exc, SchedulingInputError):
        for item in exc.issues:
            message = item.message if hasattr(item, "message") else item.get("message", str(item))
            st.warning(message)


def _overview(services: SchedulingServices, project, workspace) -> None:
    counts = [
        len(services.wbs.list(workspace.schedule_id)),
        len(services.calendar.list(workspace.schedule_id)),
        len(services.activity.list(workspace.schedule_id)),
        len(services.relationship.list(workspace.schedule_id)),
    ]
    latest = services.schedule.latest_run(workspace.schedule_id)
    for column, label, value in zip(
        st.columns(5),
        ["WBS nodes", "Calendars", "Activities", "Relationships", "Latest run"],
        [*counts, latest.status.title() if latest else "Not run"],
        strict=True,
    ):
        column.metric(label, value)
    st.caption(
        f"{workspace.schedule_id} · {workspace.version} · forward pass only · "
        f"project dates {project.planned_start_date} to {project.required_completion_date}"
    )
    with st.form("calculation_settings"):
        left, right = st.columns(2)
        precision = left.number_input("Displayed duration decimal places", 0, 6, workspace.rounding_precision, 1)
        modes = ["ROUND_HALF_UP", "ROUND_HALF_EVEN", "ROUND_UP", "ROUND_DOWN"]
        rounding = right.selectbox("Displayed duration rounding", modes, index=modes.index(workspace.rounding_mode))
        submitted = st.form_submit_button("Save calculation display settings")
    if submitted:
        try:
            services.workspace.update_calculation_settings(
                workspace.schedule_id, rounding_precision=int(precision), rounding_mode=rounding
            )
        except Exception as exc:
            _show_error(exc)
        else:
            st.success("Display settings saved. Exact internal durations remain unrounded.")
            st.rerun()
    st.info("This milestone calculates early planned dates only. It does not calculate float or critical path.")


def _wbs_tab(services: SchedulingServices, workspace) -> None:
    nodes = services.wbs.list(workspace.schedule_id)
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Code": item.code,
                    "Name": item.name,
                    "Parent": next((node.code for node in nodes if node.wbs_id == item.parent_wbs_id), ""),
                    "Order": item.sort_order,
                    "Notes": item.notes,
                }
                for item in nodes
            ],
            columns=["Code", "Name", "Parent", "Order", "Notes"],
        ),
        width="stretch",
        hide_index=True,
    )
    selected_id = st.selectbox(
        "WBS record to edit",
        [None, *[item.wbs_id for item in nodes]],
        format_func=lambda value: "Create a new WBS node" if value is None else next(
            f"{item.code} · {item.name}" for item in nodes if item.wbs_id == value
        ),
    )
    selected = next((item for item in nodes if item.wbs_id == selected_id), None)
    with st.form("wbs_editor"):
        left, right = st.columns(2)
        code = left.text_input("WBS code *", value=selected.code if selected else "")
        name = right.text_input("WBS name *", value=selected.name if selected else "")
        parent_options = [None, *[item.wbs_id for item in nodes if item.wbs_id != selected_id]]
        parent_index = parent_options.index(selected.parent_wbs_id) if selected and selected.parent_wbs_id in parent_options else 0
        parent = left.selectbox(
            "Parent WBS",
            parent_options,
            index=parent_index,
            format_func=lambda value: "— Root node —" if value is None else next(
                f"{item.code} · {item.name}" for item in nodes if item.wbs_id == value
            ),
        )
        order = right.number_input("Sort order", 0, value=selected.sort_order if selected else len(nodes), step=1)
        notes = st.text_area("Notes", value=(selected.notes or "") if selected else "")
        submitted = st.form_submit_button("Update WBS node" if selected else "Add WBS node", type="primary")
    if submitted:
        try:
            services.wbs.save(
                schedule_id=workspace.schedule_id,
                code=code,
                name=name,
                parent_wbs_id=parent,
                sort_order=int(order),
                notes=notes,
                wbs_id=selected_id,
            )
        except Exception as exc:
            _show_error(exc)
        else:
            st.success("WBS node saved.")
            st.rerun()
    if selected and st.button("Delete selected WBS"):
        try:
            services.wbs.delete(selected.wbs_id)
        except Exception as exc:
            _show_error(exc)
        else:
            st.success("WBS node deleted.")
            st.rerun()


def _calendar_table(calendars) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Code": item.code,
                "Name": item.name,
                "Time zone": item.time_zone,
                "Weekdays": ", ".join(item.working_weekdays),
                "Start": item.workday_start_time.strftime("%H:%M"),
                "Net hours/day": str(item.working_hours_per_day),
                "Breaks": len(item.breaks),
                "Exceptions": len(item.exceptions),
            }
            for item in calendars
        ],
        columns=["Code", "Name", "Time zone", "Weekdays", "Start", "Net hours/day", "Breaks", "Exceptions"],
    )


def _calendar_tab(services: SchedulingServices, workspace) -> None:
    calendars = services.calendar.list(workspace.schedule_id)
    if not calendars and st.button("Create calendar from confirmed project setup", type="primary"):
        try:
            services.calendar.create_from_project(workspace.schedule_id)
        except Exception as exc:
            _show_error(exc)
        else:
            st.success("Project setup calendar created. Review it before assigning activities.")
            st.rerun()
    st.dataframe(_calendar_table(calendars), width="stretch", hide_index=True)
    calendar_id = st.selectbox(
        "Calendar to edit",
        [None, *[item.calendar_id for item in calendars]],
        format_func=lambda value: "Create a new calendar" if value is None else next(
            f"{item.code} · {item.name}" for item in calendars if item.calendar_id == value
        ),
    )
    selected = next((item for item in calendars if item.calendar_id == calendar_id), None)
    default_breaks = [item.to_dict() for item in selected.breaks] if selected else []
    default_exceptions = [item.to_dict() for item in selected.exceptions] if selected else []
    with st.form("calendar_editor"):
        first, second = st.columns(2)
        code = first.text_input("Calendar code *", value=selected.code if selected else "")
        name = second.text_input("Calendar name *", value=selected.name if selected else "")
        zone = first.text_input("IANA time zone *", value=selected.time_zone if selected else "")
        start = second.time_input("Workday start *", value=selected.workday_start_time if selected else time(7))
        weekdays = st.multiselect("Working weekdays *", WEEKDAYS, default=list(selected.working_weekdays) if selected else [])
        hours = st.text_input("Net productive hours per working day *", value=str(selected.working_hours_per_day) if selected else "")
        st.caption("Breaks extend elapsed clock time; they do not reduce the net productive hours above.")
        breaks = st.data_editor(
            pd.DataFrame(default_breaks, columns=["break_id", "start_time", "end_time"]),
            num_rows="dynamic",
            hide_index=True,
            disabled=["break_id"],
            column_config={"break_id": None, "start_time": "Break start (HH:MM)", "end_time": "Break end (HH:MM)"},
            key=f"breaks_{calendar_id or 'new'}",
        )
        st.caption("Exceptions override the weekly calendar. Optional start/hours inherit the normal shift.")
        exceptions = st.data_editor(
            pd.DataFrame(
                default_exceptions,
                columns=["exception_id", "date", "working", "workday_start_time", "working_hours", "reason"],
            ),
            num_rows="dynamic",
            hide_index=True,
            disabled=["exception_id"],
            column_config={
                "exception_id": None,
                "date": st.column_config.DateColumn("Date", required=True),
                "working": st.column_config.CheckboxColumn("Working?"),
                "workday_start_time": "Override start (HH:MM)",
                "working_hours": "Override net hours",
                "reason": "Reason",
            },
            key=f"exceptions_{calendar_id or 'new'}",
        )
        submitted = st.form_submit_button("Update calendar" if selected else "Add calendar", type="primary")
    if submitted:
        try:
            break_values = [
                {
                    "break_id": _text_or_none(item.get("break_id")),
                    "start_time": _text_or_none(item.get("start_time")),
                    "end_time": _text_or_none(item.get("end_time")),
                }
                for item in breaks.to_dict(orient="records")
                if _text_or_none(item.get("start_time")) or _text_or_none(item.get("end_time"))
            ]
            exception_values = [
                {
                    "exception_id": _text_or_none(item.get("exception_id")),
                    "date": item.get("date"),
                    "working": bool(item.get("working")),
                    "workday_start_time": _text_or_none(item.get("workday_start_time")),
                    "working_hours": _text_or_none(item.get("working_hours")),
                    "reason": _text_or_none(item.get("reason")),
                }
                for item in exceptions.to_dict(orient="records")
                if item.get("date") is not None and not pd.isna(item.get("date"))
            ]
            services.calendar.save(
                schedule_id=workspace.schedule_id,
                code=code,
                name=name,
                time_zone=zone,
                working_weekdays=weekdays,
                workday_start_time=start,
                working_hours_per_day=hours,
                breaks=break_values,
                exceptions=exception_values,
                calendar_id=calendar_id,
            )
        except Exception as exc:
            _show_error(exc)
        else:
            st.success("Calendar saved.")
            st.rerun()
    if selected and st.button("Delete selected calendar"):
        try:
            services.calendar.delete(selected.calendar_id)
        except Exception as exc:
            _show_error(exc)
        else:
            st.success("Calendar deleted.")
            st.rerun()


def _boq_conversion(services: SchedulingServices, project, workspace) -> None:
    imports = services.boq.list_imports(project.project_id)
    if not imports:
        st.info("Import and validate a BOQ before converting BOQ rows into draft activities.")
        return
    import_id = st.selectbox(
        "BOQ import source",
        [item["import_id"] for item in imports],
        format_func=lambda value: next(item["source_file_name"] for item in imports if item["import_id"] == value),
    )
    rows = services.boq.get_rows(import_id)
    converted = {item.source_boq_row_id for item in services.activity.list(workspace.schedule_id)}
    eligible = [item for item in rows if item.validation_status == "valid" and item.row_id not in converted]
    selected = st.multiselect(
        "Validated BOQ rows to convert",
        [item.row_id for item in eligible],
        format_func=lambda value: next(
            f"{item.item_code or '—'} · {item.description} · {item.quantity:g} {item.unit}"
            for item in eligible
            if item.row_id == value
        ),
    )
    st.caption("Conversion copies confirmed BOQ quantities only. It does not assign WBS, productivity, crews, or calendars.")
    if st.button("Convert selected BOQ rows", disabled=not selected):
        try:
            result = services.activity.convert_boq_rows(workspace.schedule_id, import_id, selected)
        except Exception as exc:
            _show_error(exc)
        else:
            st.success(f"Created {len(result.created)} draft activity row(s).")
            st.rerun()


def _activity_frame(activities) -> pd.DataFrame:
    columns = [
        "activity_pk", "activity_id", "activity_name", "activity_type", "boq_item", "quantity", "unit",
        "wbs_id", "productivity_rate", "productivity_basis", "crew_count", "calendar_id", "notes", "sort_order",
    ]
    return pd.DataFrame(
        [
            {
                "activity_pk": item.activity_pk,
                "activity_id": item.activity_id,
                "activity_name": item.activity_name,
                "activity_type": item.activity_type,
                "boq_item": item.boq_item_code,
                "quantity": str(item.quantity) if item.quantity is not None else None,
                "unit": item.unit,
                "wbs_id": item.wbs_id,
                "productivity_rate": str(item.productivity_rate) if item.productivity_rate is not None else None,
                "productivity_basis": item.productivity_basis,
                "crew_count": item.crew_count,
                "calendar_id": item.calendar_id,
                "notes": item.notes,
                "sort_order": item.sort_order,
            }
            for item in activities
        ],
        columns=columns,
    )


def _activity_tab(services: SchedulingServices, project, workspace) -> None:
    _boq_conversion(services, project, workspace)
    st.divider()
    activities = services.activity.list(workspace.schedule_id)
    wbs_nodes = services.wbs.list(workspace.schedule_id)
    calendars = services.calendar.list(workspace.schedule_id)
    frame = _activity_frame(activities)
    edited = st.data_editor(
        frame,
        width="stretch",
        hide_index=True,
        disabled=["activity_pk", "boq_item"],
        column_config={
            "activity_pk": None,
            "activity_id": st.column_config.TextColumn("Activity ID", required=True),
            "activity_name": st.column_config.TextColumn("Activity name", required=True, width="large"),
            "activity_type": st.column_config.SelectboxColumn("Type", options=ACTIVITY_TYPES, required=True),
            "boq_item": "BOQ item",
            "quantity": "Quantity",
            "unit": "Unit",
            "wbs_id": st.column_config.SelectboxColumn("WBS", options=[item.wbs_id for item in wbs_nodes]),
            "productivity_rate": "Productivity rate",
            "productivity_basis": st.column_config.SelectboxColumn("Basis", options=["per_day", "per_hour"]),
            "crew_count": st.column_config.NumberColumn("Crews", min_value=1, step=1),
            "calendar_id": st.column_config.SelectboxColumn("Calendar", options=[item.calendar_id for item in calendars]),
            "notes": "Notes",
            "sort_order": st.column_config.NumberColumn("Order", min_value=0, step=1),
        },
        key=f"activity_editor_{workspace.schedule_id}",
    )
    if st.button("Validate and save activity edits", type="primary", disabled=frame.empty):
        try:
            existing = {item.activity_pk: item for item in activities}
            for value in edited.to_dict(orient="records"):
                original = existing[value["activity_pk"]]
                services.activity.save(
                    schedule_id=workspace.schedule_id,
                    activity_pk=original.activity_pk,
                    activity_id=_text_or_none(value.get("activity_id")),
                    activity_name=_text_or_none(value.get("activity_name")),
                    activity_type=_text_or_none(value.get("activity_type")),
                    quantity=_text_or_none(value.get("quantity")),
                    unit=_text_or_none(value.get("unit")),
                    normalized_unit=original.normalized_unit,
                    wbs_id=_text_or_none(value.get("wbs_id")),
                    productivity_rate=_text_or_none(value.get("productivity_rate")),
                    productivity_basis=_text_or_none(value.get("productivity_basis")),
                    crew_count=value.get("crew_count"),
                    calendar_id=_text_or_none(value.get("calendar_id")),
                    notes=_text_or_none(value.get("notes")),
                    assumptions=list(original.assumptions),
                    sort_order=int(value.get("sort_order") or 0),
                )
        except Exception as exc:
            _show_error(exc)
        else:
            st.success(f"Saved {len(edited)} activity row(s).")
            st.rerun()
    with st.expander("Add a manual activity"):
        with st.form("manual_activity"):
            activity_id = st.text_input("Activity ID *")
            activity_name = st.text_input("Activity name *")
            activity_type = st.selectbox("Activity type *", ACTIVITY_TYPES)
            submitted = st.form_submit_button("Add manual draft activity")
        if submitted:
            try:
                services.activity.save(
                    schedule_id=workspace.schedule_id,
                    activity_id=activity_id,
                    activity_name=activity_name,
                    activity_type=activity_type,
                    quantity=None,
                    unit=None,
                    normalized_unit=None,
                    wbs_id=None,
                    productivity_rate=None,
                    productivity_basis=None,
                    crew_count=None,
                    calendar_id=None,
                    notes=None,
                    assumptions=[],
                    sort_order=len(activities),
                )
            except Exception as exc:
                _show_error(exc)
            else:
                st.success("Manual draft activity added. Complete its inputs in the table.")
                st.rerun()
    linked = [item for item in activities if item.source_boq_row_id]
    if linked:
        with st.expander("Split a BOQ-linked activity"):
            source_pk = st.selectbox(
                "Source activity", [item.activity_pk for item in linked],
                format_func=lambda value: next(f"{item.activity_id} · {item.activity_name}" for item in linked if item.activity_pk == value),
            )
            new_id = st.text_input("New split activity ID")
            new_name = st.text_input("New split activity name")
            st.caption("The new split quantity and productivity remain blank until you allocate them explicitly.")
            if st.button("Create split draft"):
                try:
                    services.activity.create_split_activity(source_pk, activity_id=new_id, activity_name=new_name)
                except Exception as exc:
                    _show_error(exc)
                else:
                    st.success("Split draft created with no fabricated quantity.")
                    st.rerun()
    if activities:
        delete_pk = st.selectbox(
            "Activity to delete", [item.activity_pk for item in activities],
            format_func=lambda value: next(f"{item.activity_id} · {item.activity_name}" for item in activities if item.activity_pk == value),
        )
        if st.button("Delete selected activity"):
            try:
                services.activity.delete(delete_pk)
            except Exception as exc:
                _show_error(exc)
            else:
                st.success("Activity deleted.")
                st.rerun()


def _relationship_tab(services: SchedulingServices, workspace) -> None:
    activities = services.activity.list(workspace.schedule_id)
    relationships = services.relationship.list(workspace.schedule_id)
    names = {item.activity_pk: f"{item.activity_id} · {item.activity_name}" for item in activities}
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Relationship": item.relationship_id,
                    "Predecessor": names.get(item.predecessor_activity_pk, item.predecessor_activity_pk),
                    "Successor": names.get(item.successor_activity_pk, item.successor_activity_pk),
                    "Type": item.relationship_type,
                    "Lag hours": str(item.lag_hours),
                    "Notes": item.notes,
                }
                for item in relationships
            ],
            columns=["Relationship", "Predecessor", "Successor", "Type", "Lag hours", "Notes"],
        ),
        width="stretch",
        hide_index=True,
    )
    if len(activities) < 2:
        st.info("Create at least two activities before adding a relationship.")
        return
    with st.form("relationship_editor"):
        predecessor = st.selectbox("Predecessor *", list(names), format_func=names.get)
        successor = st.selectbox("Successor *", list(names), index=1, format_func=names.get)
        relation_type = st.selectbox("Relationship type *", RELATIONSHIP_TYPES)
        lag = st.text_input("Lag in successor working hours *", value="0")
        notes = st.text_input("Notes")
        submitted = st.form_submit_button("Add relationship", type="primary")
    if submitted:
        try:
            relationship = services.relationship.save(
                schedule_id=workspace.schedule_id,
                predecessor_activity_pk=predecessor,
                successor_activity_pk=successor,
                relationship_type=relation_type,
                lag_hours=lag,
                notes=notes,
            )
        except Exception as exc:
            _show_error(exc)
        else:
            if relationship.lag_hours < 0:
                st.warning("Negative lag was saved and remains flagged for planner review.")
            else:
                st.success("Relationship saved.")
            st.rerun()
    if relationships:
        delete_id = st.selectbox("Relationship to delete", [item.relationship_id for item in relationships])
        if st.button("Delete relationship"):
            services.relationship.delete(delete_id)
            st.success("Relationship deleted.")
            st.rerun()


def _calculation_tab(services: SchedulingServices, workspace) -> None:
    wbs_nodes = services.wbs.list(workspace.schedule_id)
    calendars = services.calendar.list(workspace.schedule_id)
    activities = services.activity.list(workspace.schedule_id)
    relationships = services.relationship.list(workspace.schedule_id)
    issues = validate_schedule_inputs(
        wbs_nodes=wbs_nodes,
        calendars=calendars,
        activities=activities,
        relationships=relationships,
    )
    if not activities:
        issues += ({"code": "ACTIVITIES_REQUIRED", "message": "At least one activity is required.", "field": "activities", "severity": "error"},)
    if issues:
        st.subheader("Validation findings")
        st.dataframe(pd.DataFrame(issues), width="stretch", hide_index=True)
    blockers = [item for item in issues if item["severity"] == "error"]
    if blockers:
        st.error(f"Calculation is blocked by {len(blockers)} required correction(s).")
    else:
        st.success("No blocking draft-input errors were found. Warnings remain visible in the saved run.")
    if st.button("Calculate forward schedule", type="primary", disabled=bool(blockers)):
        try:
            run = services.schedule.calculate(workspace.schedule_id)
        except Exception as exc:
            _show_error(exc)
        else:
            st.success(f"Schedule run {run.run_id} completed with status: {run.status}.")
            st.rerun()

    run = services.schedule.latest_run(workspace.schedule_id)
    if run is None:
        st.info("No schedule calculation has been saved yet.")
        return
    st.divider()
    st.subheader("Latest immutable calculation run")
    first, second, third = st.columns(3)
    first.metric("Run status", run.status.title())
    second.metric("Planned finish", run.project_planned_finish.date().isoformat() if run.project_planned_finish else "—")
    variance = run.completion_variance_days
    third.metric("Completion variance", f"{variance:+d} calendar days" if variance is not None else "—")
    st.caption(f"{run.run_id} · engine {run.engine_version} · {run.calculated_at.isoformat()}")
    if run.validation_issues:
        st.dataframe(pd.DataFrame(run.validation_issues), width="stretch", hide_index=True)
    activities_by_id = {item.activity_pk: item for item in activities}
    wbs_by_id = {item.wbs_id: item.code for item in wbs_nodes}
    calendar_by_id = {item.calendar_id: item.code for item in calendars}
    result_rows = []
    for result in run.results:
        activity = activities_by_id.get(result.activity_pk)
        if not activity:
            continue
        result_rows.append(
            {
                "Activity ID": activity.activity_id,
                "Activity name": activity.activity_name,
                "WBS": wbs_by_id.get(activity.wbs_id, ""),
                "Calendar": calendar_by_id.get(activity.calendar_id, ""),
                "Exact hours": str(result.exact_duration_hours),
                "Duration days": str(result.display_duration_days),
                "Planned start": result.early_start.isoformat(sep=" ", timespec="minutes"),
                "Planned finish": result.early_finish.isoformat(sep=" ", timespec="minutes"),
            }
        )
    st.dataframe(pd.DataFrame(result_rows), width="stretch", hide_index=True)
    st.caption("Dates are derived outputs. Edit inputs or logic, then calculate a new immutable run.")


def render_schedule_page(services: SchedulingServices, active_project_id: str | None) -> None:
    st.header("Schedule workspace")
    project = services.project.get_project(active_project_id) if active_project_id else None
    if project is None:
        st.warning("Create or select a saved project before opening the schedule workspace.")
        return
    try:
        workspace = services.workspace.ensure_for_project(project.project_id)
    except Exception as exc:
        _show_error(exc)
        return
    st.caption(f"Active project: {project.name} ({project.project_id})")
    overview, wbs, calendars, activities, relationships, calculate = st.tabs(
        ["Overview", "WBS", "Calendars", "Activities", "Relationships", "Calculate & review"]
    )
    with overview:
        _overview(services, project, workspace)
    with wbs:
        _wbs_tab(services, workspace)
    with calendars:
        _calendar_tab(services, workspace)
    with activities:
        _activity_tab(services, project, workspace)
    with relationships:
        _relationship_tab(services, workspace)
    with calculate:
        _calculation_tab(services, workspace)
