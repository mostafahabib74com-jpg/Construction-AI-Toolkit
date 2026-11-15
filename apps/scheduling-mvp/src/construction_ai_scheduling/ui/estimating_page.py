"""Persistent estimate draft editor with explicit rates and evidence fields."""

from __future__ import annotations

import json
import pandas as pd
import streamlit as st

from construction_ai_scheduling.domain.estimating import CATEGORIES, calculate_estimate, empty_estimate
from construction_ai_scheduling.application.schedule_exports import csv_bytes, workbook_bytes


def _clean_records(frame):
    return [{key: (None if pd.isna(value) else value) for key, value in row.items()} for row in frame.to_dict("records")]


def render_estimating_page(services, active_project_id):
    st.header("Estimating / تحليل الأسعار")
    project = services.project.get_project(active_project_id) if active_project_id else None
    if not project:
        st.warning("Create or select a saved project before preparing an estimate.")
        return
    repository = services.schedule.repository
    payload = repository.get_estimate_draft(project.project_id) or empty_estimate()
    st.caption(f"{project.name} — {project.currency}. All rates must be in this currency. No market rates are prefilled.")
    with st.expander("Copy validated BOQ quantities into the estimate"):
        batches = services.boq.list_imports(project.project_id)
        if batches:
            import_id = st.selectbox("BOQ import for estimating", [batch["import_id"] for batch in batches])
            st.caption("Appends quantities only. Existing estimate items are retained. Rates and resources remain blank.")
            if st.button("Copy BOQ items without prices"):
                existing = {item["item_id"] for item in payload["items"]}
                added = 0
                for row in services.boq.get_rows(import_id):
                    if row.validation_status != "valid" or row.row_id in existing:
                        continue
                    payload["items"].append({"item_id": row.row_id, "description": row.description, "unit": row.unit,
                                             "quantity": str(row.quantity), "quantity_source": f"{import_id}, row {row.source_row_number}",
                                             "source_evidence": row.raw_data.get("_import_preparation", {}), "resources": []})
                    added += 1
                repository.save_estimate_draft(project.project_id, payload)
                st.success(f"Copied {added} unpriced item(s).")
                st.rerun()
        else:
            st.info("Import a BOQ first, or enter measured items below.")
    st.subheader("1. Quantities and scope")
    fields = ["item_id", "description", "unit", "quantity", "quantity_source"]
    with st.form(f"estimate_items_{project.project_id}"):
        frame = pd.DataFrame([{key: item.get(key) for key in fields} for item in payload["items"]], columns=fields)
        edited = st.data_editor(frame, num_rows="dynamic", hide_index=True, width="stretch", key=f"estimate_item_editor_{project.project_id}")
        if st.form_submit_button("Save estimate items"):
            rows = _clean_records(edited)
            ids = [str(row.get("item_id") or "").strip() for row in rows]
            if any(not value for value in ids) or len(set(ids)) != len(ids):
                st.error("Give every item a unique ID before saving.")
            else:
                previous = {item["item_id"]: item for item in payload["items"]}
                payload["items"] = [{**previous.get(item_id, {"resources": []}), **row, "item_id": item_id} for row, item_id in zip(rows, ids)]
                repository.save_estimate_draft(project.project_id, payload)
                st.rerun()
    if payload["items"]:
        st.subheader("2. Resource cost per BOQ unit")
        ids = [item["item_id"] for item in payload["items"]]
        selected = st.selectbox("Estimate item", ids, format_func=lambda key: next(f"{key} — {item['description']}" for item in payload["items"] if item["item_id"] == key))
        item = next(item for item in payload["items"] if item["item_id"] == selected)
        if item.get("source_evidence"):
            with st.expander("Source scope and merged-row evidence"):
                st.json(item["source_evidence"])
        st.info("Consumption is resource units per one BOQ unit. Labor/equipment: crew cost per period ÷ production per the same period. Record the calculation and quotation in source.")
        resource_fields = ["name", "category", "resource_unit", "consumption", "rate", "waste_percent", "waste_basis", "source", "price_date"]
        with st.form(f"resources_{project.project_id}_{selected}"):
            frame = pd.DataFrame([{key: resource.get(key) for key in resource_fields} for resource in item.get("resources", [])], columns=resource_fields)
            edited = st.data_editor(frame, num_rows="dynamic", hide_index=True, width="stretch",
                                    column_config={"category": st.column_config.SelectboxColumn(options=list(CATEGORIES))},
                                    key=f"resource_editor_{project.project_id}_{selected}")
            if st.form_submit_button("Save item resources"):
                item["resources"] = [{**row, "currency": project.currency} for row in _clean_records(edited)]
                repository.save_estimate_draft(project.project_id, payload)
                st.rerun()
    st.subheader("3. Commercial build-up")
    settings = payload["commercial"]
    with st.form(f"commercial_{project.project_id}"):
        values = dict(settings)
        for column, key in zip(st.columns(3), ["indirects", "contingency", "overhead"]):
            values[key] = column.text_input(key.title() + f" ({project.currency})", value=str(settings[key]))
            values[key + "_basis"] = column.text_input(key.title() + " basis / allocation", value=settings.get(key + "_basis", ""))
        left, middle, right = st.columns(3)
        values["profit_basis"] = left.selectbox("Profit calculation", ["markup", "margin"], index=["markup", "margin"].index(settings["profit_basis"]))
        values["profit_percent"] = left.text_input("Profit %", value=str(settings["profit_percent"]))
        values["tax_percent"] = middle.text_input("Tax % — explicit project basis", value=str(settings["tax_percent"]))
        values["discount"] = right.text_input("Discount amount", value=str(settings["discount"]))
        st.caption("Markup: cost × (1 + %). Gross margin: cost ÷ (1 − %). Tax is never added automatically. Any discount reduces the achieved margin.")
        if st.form_submit_button("Save commercial inputs"):
            payload["commercial"] = values
            repository.save_estimate_draft(project.project_id, payload)
            st.rerun()
    result = calculate_estimate(payload, project.currency)
    if result["issues"]:
        st.warning("Estimate is incomplete. No final selling price is available.")
        total_items, priced_items = len(payload["items"]), len(result["items"])
        for column, label, value in zip(st.columns(3), ["Estimate items", "Priced items", "Items needing rates/evidence"], [total_items, priced_items, total_items - priced_items]):
            column.metric(label, value)
        st.dataframe(pd.DataFrame([{key: item.get(key) for key in ["item_id", "description", "unit", "quantity", "quantity_source"]} for item in payload["items"]]), hide_index=True, width="stretch")
        for issue in result["issues"][:5]:
            st.write("• " + issue)
        if len(result["issues"]) > 5:
            with st.expander(f"Review all {len(result['issues'])} missing inputs / findings"):
                st.dataframe(pd.DataFrame({"Finding": result["issues"]}), hide_index=True, width="stretch")
    else:
        st.success("Calculation complete. Review source evidence before commercial approval.")
        summary = result["summary"]
        for column, key in zip(st.columns(3), ["Direct cost", "Selling price excluding tax", "Total including tax"]):
            column.metric(key, f"{summary[key]} {project.currency}")
        st.dataframe(pd.DataFrame([summary]), hide_index=True)
        st.dataframe(pd.DataFrame(result["items"]), hide_index=True)
        st.download_button("Download estimate CSV", csv_bytes(result["items"]), "estimate.csv", "text/csv")
        st.download_button("Download estimate Excel", workbook_bytes({"Summary": [summary], "BOQ pricing": result["items"], "Resource build-up": result["resources"], "Commercial inputs": [settings]}), "estimate.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Download estimate draft and evidence JSON", json.dumps({"project": project.to_dict(), "inputs": payload, "calculation": result}, ensure_ascii=False, indent=2), "estimate-draft.json", "application/json")
