"""BOQ upload, explicit mapping, and editable draft review."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from construction_ai_scheduling.application.boq_service import BOQService
from construction_ai_scheduling.application.project_service import ProjectService
from construction_ai_scheduling.domain.errors import BOQImportError

MAPPING_LABELS = {
    "item_code": "Item code (optional)",
    "description": "Description",
    "quantity": "Quantity",
    "unit": "Unit",
}


def _mapping_selector(field: str, columns: tuple[str, ...], suggestion: str | None, file_key: str) -> str | None:
    options: list[str | None] = [None, *columns]
    index = options.index(suggestion) if suggestion in options else 0
    return st.selectbox(
        MAPPING_LABELS[field],
        options,
        index=index,
        format_func=lambda value: "— Not mapped —" if value is None else value,
        key=f"mapping_{file_key}_{field}",
    )


def _render_import_form(boq_service: BOQService, project_id: str) -> None:
    st.subheader("Import a BOQ")
    uploaded = st.file_uploader("BOQ file", type=["csv", "xlsx"], help="The source file is read in memory and is not copied into the repository.")
    if uploaded is None:
        return

    content = uploaded.getvalue()
    selected_sheet = None
    try:
        sheets = boq_service.sheet_names(uploaded.name, content)
        if sheets:
            selected_sheet = st.selectbox("Worksheet", sheets)
        preview = boq_service.preview(uploaded.name, content, sheet_name=selected_sheet)
        if preview.source_type == "xlsx":
            option_labels = dict(preview.header_row_options)
            option_numbers = list(option_labels)
            selected_header_row = st.selectbox(
                "Excel header row",
                option_numbers,
                index=option_numbers.index(preview.header_row_number),
                format_func=lambda number: f"Row {number}: {option_labels[number]}",
                help="Rows above the selected header are introductory content and are not imported.",
                key=f"header_row_{uploaded.name}_{selected_sheet or 'xlsx'}_{len(content)}",
            )
            if selected_header_row != preview.header_row_number:
                preview = boq_service.preview(
                    uploaded.name,
                    content,
                    sheet_name=selected_sheet,
                    header_row=selected_header_row,
                )
            st.caption(
                f"Excel row {preview.header_row_number} supplies the column names. "
                "Every nonblank row after it remains available for import."
            )
    except BOQImportError as exc:
        st.error(str(exc))
        return

    st.caption(f"Detected {len(preview.frame)} data row(s). Review the source preview and confirm each mapping.")
    st.dataframe(preview.frame.head(50), use_container_width=True, hide_index=True)

    suggestions = boq_service.suggest_mapping(preview.columns)
    st.markdown("#### Column mapping")
    columns = st.columns(4)
    mapping: dict[str, str | None] = {}
    file_key = f"{uploaded.name}_{selected_sheet or 'csv'}"
    for container, field in zip(columns, MAPPING_LABELS, strict=True):
        with container:
            mapping[field] = _mapping_selector(field, preview.columns, suggestions[field], file_key)

    st.info("Unmapped or blank required values will be stored as incomplete drafts and clearly flagged for review.")
    if st.button("Import draft BOQ", type="primary"):
        try:
            batch = boq_service.import_boq(
                project_id=project_id,
                file_name=uploaded.name,
                preview=preview,
                mapping=mapping,
            )
        except BOQImportError as exc:
            st.error(str(exc))
            return
        st.session_state.active_import_id = batch.import_id
        st.success(f"Imported {len(batch.rows)} BOQ row(s) for review.")
        st.rerun()


def _rows_frame(rows) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "row_id": row.row_id,
            "source_row": row.source_row_number,
            "item_code": row.item_code,
            "description": row.description,
            "quantity": row.quantity,
            "unit": row.unit,
            "normalized_unit": row.normalized_unit,
            "status": row.validation_status,
            "validation_errors": " | ".join(row.validation_errors),
        }
        for row in rows
    ])


def _render_review(boq_service: BOQService, project_id: str) -> None:
    imports = boq_service.list_imports(project_id)
    if not imports:
        st.info("No BOQ has been imported for this project yet.")
        return

    import_ids = [item["import_id"] for item in imports]
    requested = st.session_state.get("active_import_id")
    selected_index = import_ids.index(requested) if requested in import_ids else 0
    selected_id = st.selectbox(
        "Imported BOQ",
        import_ids,
        index=selected_index,
        format_func=lambda import_id: next(
            f"{item['source_file_name']} · {item['row_count']} rows · {item['imported_at']}"
            for item in imports
            if item["import_id"] == import_id
        ),
    )
    st.session_state.active_import_id = selected_id
    rows = boq_service.get_rows(selected_id)
    frame = _rows_frame(rows)
    if frame.empty:
        st.warning("This import contains no BOQ rows.")
        return

    counts = frame["status"].value_counts()
    valid, incomplete, invalid = st.columns(3)
    valid.metric("Valid rows", int(counts.get("valid", 0)))
    incomplete.metric("Incomplete rows", int(counts.get("incomplete", 0)))
    invalid.metric("Invalid rows", int(counts.get("invalid", 0)))

    edited = st.data_editor(
        frame,
        use_container_width=True,
        hide_index=True,
        disabled=["row_id", "source_row", "normalized_unit", "status", "validation_errors"],
        column_config={
            "row_id": None,
            "source_row": st.column_config.NumberColumn("Source row", format="%d"),
            "item_code": st.column_config.TextColumn("Item code"),
            "description": st.column_config.TextColumn("Description", required=True, width="large"),
            "quantity": st.column_config.NumberColumn("Quantity", min_value=0.0, format="%.6f"),
            "unit": st.column_config.TextColumn("Unit", required=True),
            "normalized_unit": st.column_config.TextColumn("Normalized unit"),
            "status": st.column_config.TextColumn("Validation"),
            "validation_errors": st.column_config.TextColumn("Issues", width="large"),
        },
        key=f"boq_editor_{selected_id}",
    )
    if st.button("Validate and save BOQ edits"):
        try:
            updated = boq_service.update_rows(selected_id, edited.to_dict(orient="records"))
        except BOQImportError as exc:
            st.error(str(exc))
            return
        valid_count = sum(row.validation_status == "valid" for row in updated)
        st.success(f"Saved {len(updated)} row(s); {valid_count} currently pass the Milestone 1 BOQ checks.")
        st.rerun()


def render_boq_page(boq_service: BOQService, project_service: ProjectService, active_project_id: str | None) -> None:
    st.header("BOQ import and review")
    if not active_project_id or project_service.get_project(active_project_id) is None:
        st.warning("Create or select a saved project before importing a BOQ.")
        return
    project = project_service.get_project(active_project_id)
    st.caption(f"Active project: {project.name} ({project.project_id})")
    _render_import_form(boq_service, active_project_id)
    st.divider()
    st.subheader("Editable BOQ review")
    _render_review(boq_service, active_project_id)
