"""Traceable CSV/XLSX exports from immutable runs, never from current drafts."""

from __future__ import annotations

import csv
from io import BytesIO, StringIO
import json
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from construction_ai_scheduling.domain.schedule_models import ScheduleRun


def schedule_rows(run: ScheduleRun) -> list[dict[str, Any]]:
    if run.status != "calculated" or not run.input_snapshot:
        raise ValueError("Calculate a successful run with a saved input snapshot before exporting.")
    snapshot = run.input_snapshot
    activities = {item["activity_pk"]: item for item in snapshot["activities"]}
    wbs = {item["wbs_id"]: item["code"] for item in snapshot["wbs"]}
    calendars = {item["calendar_id"]: item["code"] for item in snapshot["calendars"]}
    rows = []
    for result in run.results:
        activity = activities[result.activity_pk]
        cpm = result.calculation_trace.get("cpm", {})
        rows.append({
            "Activity ID": activity["activity_id"], "Activity name": activity["activity_name"],
            "Type": activity["activity_type"], "WBS": wbs.get(activity["wbs_id"], ""),
            "Calendar": calendars.get(activity["calendar_id"], ""),
            "Quantity": activity["quantity"], "Unit": activity["unit"],
            "Productivity": activity["productivity_rate"], "Productivity basis": activity["productivity_basis"],
            "Crews": activity["crew_count"], "Exact hours": str(result.exact_duration_hours),
            "Duration days": str(result.display_duration_days),
            "Planned start": result.early_start.isoformat(), "Planned finish": result.early_finish.isoformat(),
            "Late start": cpm.get("late_start"), "Late finish": cpm.get("late_finish"),
            "Total float hours": cpm.get("total_float_hours"), "Free float hours": cpm.get("free_float_hours"),
            "Critical": cpm.get("critical"), "Source BOQ row": activity["source_boq_row_id"],
            "Notes": activity["notes"], "Assumptions": "; ".join(activity["assumptions"]),
            "Run ID": run.run_id,
        })
    return rows


def _safe_csv(value):
    # Neutralize spreadsheet formulas while preserving literal Arabic and Unicode.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


def csv_bytes(rows: list[dict]) -> bytes:
    stream = StringIO(newline="")
    if rows:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({key: _safe_csv(value) for key, value in row.items()} for row in rows)
    return stream.getvalue().encode("utf-8-sig")


def workbook_bytes(sheets: dict[str, list[dict]]) -> bytes:
    workbook = Workbook()
    workbook.remove(workbook.active)
    for title, rows in sheets.items():
        sheet = workbook.create_sheet(title)
        sheet.freeze_panes = "A2"
        if not rows:
            sheet.append(["No records"])
            continue
        headers = list(dict.fromkeys(key for row in rows for key in row))
        sheet.append(headers)
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="16324F")
        for row in rows:
            values = [row.get(key) for key in headers]
            for index, value in enumerate(values):
                if isinstance(value, (dict, list, tuple)):
                    values[index] = json.dumps(value, ensure_ascii=False, sort_keys=True)
            sheet.append(values)
            for cell in sheet[sheet.max_row]:
                if isinstance(cell.value, str):
                    cell.data_type = "s"
        sheet.auto_filter.ref = sheet.dimensions
        for column in sheet.columns:
            sheet.column_dimensions[column[0].column_letter].width = min(55, max(14, max(len(str(cell.value or "")) for cell in column) + 2))
    if not workbook.sheetnames:
        workbook.create_sheet("Empty")
    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()


def schedule_workbook(run: ScheduleRun) -> bytes:
    rows = schedule_rows(run)
    snapshot = run.input_snapshot
    activity_codes = {item["activity_pk"]: item["activity_id"] for item in snapshot["activities"]}
    relationships = [{
        "Predecessor": activity_codes[item["predecessor_activity_pk"]],
        "Successor": activity_codes[item["successor_activity_pk"]],
        "Type": item["relationship_type"], "Lag working hours": item["lag_hours"], "Notes": item["notes"],
    } for item in snapshot["relationships"]]
    return workbook_bytes({
        "Schedule": rows,
        "Relationships": relationships,
        "WBS": snapshot["wbs"], "Calendars": snapshot["calendars"],
        "Calculation traces": [{"Activity": activity_codes[item.activity_pk], **item.calculation_trace} for item in run.results],
        "Run metadata": [{"Run ID": run.run_id, "Engine": run.engine_version, "Calculated at": run.calculated_at.isoformat(),
                          "Finish": run.project_planned_finish.isoformat(), "Variance calendar days": run.completion_variance_days,
                          "CPM basis": "Shared calendar; float relative to planned finish, not contractual deadline.",
                          "Primavera": "Review workbook only. Not an XER or a verified native P6 import file."}],
        "Project": [snapshot["project"]],
    })
