"""Normalized SQLite persistence for projects and draft BOQ imports."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from construction_ai_scheduling.domain.models import BOQImport, BOQRow, Project
from construction_ai_scheduling.domain.schedule_models import (
    ActivityCalculationResult,
    ActivityRelationship,
    CalendarBreak,
    CalendarException,
    ProjectCalendar,
    ScheduleActivity,
    ScheduleRun,
    ScheduleWorkspace,
    WBSNode,
)


class SQLiteRepository:
    def __init__(self, database_path: str | Path, migration_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.migration_path = Path(migration_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            migration_files = sorted(self.migration_path.parent.glob("*.sql"))
            if self.migration_path not in migration_files:
                migration_files.insert(0, self.migration_path)
            for migration_path in migration_files:
                version = migration_path.stem
                migrations_table_exists = connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'schema_migrations'"
                ).fetchone()
                if migrations_table_exists and connection.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = ?", (version,)
                ).fetchone():
                    continue
                connection.executescript(migration_path.read_text(encoding="utf-8"))

    def create_project(self, project: Project) -> None:
        value = project.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO projects (
                    project_id, name, client, contractor, consultant, project_type, location,
                    planned_start_date, required_completion_date, working_days_per_week,
                    working_hours_per_day, working_weekdays_json, workday_start_time,
                    currency, unit_system, time_zone, created_at, updated_at
                ) VALUES (
                    :project_id, :name, :client, :contractor, :consultant, :project_type, :location,
                    :planned_start_date, :required_completion_date, :working_days_per_week,
                    :working_hours_per_day, :working_weekdays_json, :workday_start_time,
                    :currency, :unit_system, :time_zone, :created_at, :updated_at
                )
                """,
                {**value, "working_weekdays_json": json.dumps(value["working_weekdays"])},
            )

    @staticmethod
    def _project_from_row(row: sqlite3.Row) -> Project:
        value = dict(row)
        value["working_weekdays"] = json.loads(value.pop("working_weekdays_json"))
        return Project.from_dict(value)

    def get_project(self, project_id: str) -> Project | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
        return self._project_from_row(row) if row else None

    def list_projects(self) -> list[Project]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM projects ORDER BY created_at DESC, name").fetchall()
        return [self._project_from_row(row) for row in rows]

    def create_boq_import(self, batch: BOQImport) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO boq_imports(import_id, project_id, source_file_name, source_type, source_sheet, imported_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    batch.import_id,
                    batch.project_id,
                    batch.source_file_name,
                    batch.source_type,
                    batch.source_sheet,
                    batch.imported_at.isoformat(),
                ),
            )
            connection.executemany(
                """
                INSERT INTO boq_items(
                    row_id, project_id, import_id, source_row_number, item_code, description,
                    quantity, quantity_raw_json, unit, normalized_unit, validation_status,
                    validation_errors_json, raw_data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row.row_id,
                        row.project_id,
                        row.import_id,
                        row.source_row_number,
                        row.item_code,
                        row.description,
                        row.quantity,
                        json.dumps(row.quantity_raw, ensure_ascii=False),
                        row.unit,
                        row.normalized_unit,
                        row.validation_status,
                        json.dumps(row.validation_errors, ensure_ascii=False),
                        json.dumps(row.raw_data, ensure_ascii=False, sort_keys=True),
                    )
                    for row in batch.rows
                ],
            )

    def list_boq_imports(self, project_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT i.*, COUNT(b.row_id) AS row_count
                FROM boq_imports i
                LEFT JOIN boq_items b ON b.import_id = i.import_id
                WHERE i.project_id = ?
                GROUP BY i.import_id
                ORDER BY i.imported_at DESC
                """,
                (project_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _boq_row_from_row(row: sqlite3.Row) -> BOQRow:
        value = dict(row)
        value["quantity_raw"] = json.loads(value.pop("quantity_raw_json"))
        value["validation_errors"] = json.loads(value.pop("validation_errors_json"))
        value["raw_data"] = json.loads(value.pop("raw_data_json"))
        return BOQRow.from_dict(value)

    def get_boq_rows(self, import_id: str) -> list[BOQRow]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM boq_items WHERE import_id = ? ORDER BY source_row_number, row_id",
                (import_id,),
            ).fetchall()
        return [self._boq_row_from_row(row) for row in rows]

    def update_boq_rows(self, rows: list[BOQRow]) -> None:
        if not rows:
            return
        with self._connect() as connection:
            connection.executemany(
                """
                UPDATE boq_items
                SET item_code = ?, description = ?, quantity = ?, quantity_raw_json = ?,
                    unit = ?, normalized_unit = ?, validation_status = ?, validation_errors_json = ?
                WHERE row_id = ? AND import_id = ? AND project_id = ?
                """,
                [
                    (
                        row.item_code,
                        row.description,
                        row.quantity,
                        json.dumps(row.quantity_raw, ensure_ascii=False),
                        row.unit,
                        row.normalized_unit,
                        row.validation_status,
                        json.dumps(row.validation_errors, ensure_ascii=False),
                        row.row_id,
                        row.import_id,
                        row.project_id,
                    )
                    for row in rows
                ],
            )

    def save_schedule(self, schedule: ScheduleWorkspace) -> None:
        value = schedule.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO schedules(
                    schedule_id, project_id, name, version, status, calculation_mode,
                    rounding_precision, rounding_mode, created_at, updated_at
                ) VALUES (
                    :schedule_id, :project_id, :name, :version, :status, :calculation_mode,
                    :rounding_precision, :rounding_mode, :created_at, :updated_at
                )
                ON CONFLICT(schedule_id) DO UPDATE SET
                    name = excluded.name,
                    version = excluded.version,
                    status = excluded.status,
                    calculation_mode = excluded.calculation_mode,
                    rounding_precision = excluded.rounding_precision,
                    rounding_mode = excluded.rounding_mode,
                    updated_at = excluded.updated_at
                """,
                value,
            )

    def get_schedule(self, schedule_id: str) -> ScheduleWorkspace | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM schedules WHERE schedule_id = ?", (schedule_id,)).fetchone()
        return ScheduleWorkspace.from_dict(dict(row)) if row else None

    def get_schedule_for_project(self, project_id: str) -> ScheduleWorkspace | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM schedules WHERE project_id = ?", (project_id,)).fetchone()
        return ScheduleWorkspace.from_dict(dict(row)) if row else None

    def save_wbs_node(self, node: WBSNode) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO wbs_nodes(
                    wbs_id, schedule_id, code, name, parent_wbs_id, sort_order, notes, created_at, updated_at
                ) VALUES (
                    :wbs_id, :schedule_id, :code, :name, :parent_wbs_id, :sort_order, :notes, :created_at, :updated_at
                )
                ON CONFLICT(wbs_id) DO UPDATE SET
                    code = excluded.code,
                    name = excluded.name,
                    parent_wbs_id = excluded.parent_wbs_id,
                    sort_order = excluded.sort_order,
                    notes = excluded.notes,
                    updated_at = excluded.updated_at
                """,
                node.to_dict(),
            )

    def list_wbs_nodes(self, schedule_id: str) -> list[WBSNode]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM wbs_nodes WHERE schedule_id = ? ORDER BY sort_order, code",
                (schedule_id,),
            ).fetchall()
        return [WBSNode.from_dict(dict(row)) for row in rows]

    def delete_wbs_node(self, wbs_id: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM wbs_nodes WHERE wbs_id = ?", (wbs_id,))

    def save_calendar(self, calendar: ProjectCalendar) -> None:
        value = calendar.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO project_calendars(
                    calendar_id, schedule_id, code, name, time_zone, working_weekdays_json,
                    workday_start_time, working_hours_per_day_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(calendar_id) DO UPDATE SET
                    code = excluded.code,
                    name = excluded.name,
                    time_zone = excluded.time_zone,
                    working_weekdays_json = excluded.working_weekdays_json,
                    workday_start_time = excluded.workday_start_time,
                    working_hours_per_day_text = excluded.working_hours_per_day_text,
                    updated_at = excluded.updated_at
                """,
                (
                    calendar.calendar_id,
                    calendar.schedule_id,
                    calendar.code,
                    calendar.name,
                    calendar.time_zone,
                    json.dumps(value["working_weekdays"]),
                    value["workday_start_time"],
                    value["working_hours_per_day"],
                    value["created_at"],
                    value["updated_at"],
                ),
            )
            connection.execute("DELETE FROM calendar_breaks WHERE calendar_id = ?", (calendar.calendar_id,))
            connection.executemany(
                "INSERT INTO calendar_breaks(break_id, calendar_id, start_time, end_time) VALUES (?, ?, ?, ?)",
                [
                    (item.break_id, calendar.calendar_id, item.start_time.strftime("%H:%M"), item.end_time.strftime("%H:%M"))
                    for item in calendar.breaks
                ],
            )
            connection.execute("DELETE FROM calendar_exceptions WHERE calendar_id = ?", (calendar.calendar_id,))
            connection.executemany(
                """
                INSERT INTO calendar_exceptions(
                    exception_id, calendar_id, exception_date, working, workday_start_time,
                    working_hours_text, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.exception_id,
                        calendar.calendar_id,
                        item.exception_date.isoformat(),
                        int(item.working),
                        item.workday_start_time.strftime("%H:%M") if item.workday_start_time else None,
                        str(item.working_hours) if item.working_hours is not None else None,
                        item.reason,
                    )
                    for item in calendar.exceptions
                ],
            )

    @staticmethod
    def _calendar_from_row(row: sqlite3.Row, breaks: list[sqlite3.Row], exceptions: list[sqlite3.Row]) -> ProjectCalendar:
        value = dict(row)
        value["working_weekdays"] = json.loads(value.pop("working_weekdays_json"))
        value["working_hours_per_day"] = value.pop("working_hours_per_day_text")
        value["breaks"] = [
            {"break_id": item["break_id"], "start_time": item["start_time"], "end_time": item["end_time"]}
            for item in breaks
        ]
        value["exceptions"] = [
            {
                "exception_id": item["exception_id"],
                "date": item["exception_date"],
                "working": bool(item["working"]),
                "workday_start_time": item["workday_start_time"],
                "working_hours": item["working_hours_text"],
                "reason": item["reason"],
            }
            for item in exceptions
        ]
        return ProjectCalendar.from_dict(value)

    def list_calendars(self, schedule_id: str) -> list[ProjectCalendar]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM project_calendars WHERE schedule_id = ? ORDER BY code", (schedule_id,)
            ).fetchall()
            result: list[ProjectCalendar] = []
            for row in rows:
                breaks = connection.execute(
                    "SELECT * FROM calendar_breaks WHERE calendar_id = ? ORDER BY start_time", (row["calendar_id"],)
                ).fetchall()
                exceptions = connection.execute(
                    "SELECT * FROM calendar_exceptions WHERE calendar_id = ? ORDER BY exception_date", (row["calendar_id"],)
                ).fetchall()
                result.append(self._calendar_from_row(row, breaks, exceptions))
        return result

    def get_calendar(self, calendar_id: str) -> ProjectCalendar | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM project_calendars WHERE calendar_id = ?", (calendar_id,)).fetchone()
            if not row:
                return None
            breaks = connection.execute(
                "SELECT * FROM calendar_breaks WHERE calendar_id = ? ORDER BY start_time", (calendar_id,)
            ).fetchall()
            exceptions = connection.execute(
                "SELECT * FROM calendar_exceptions WHERE calendar_id = ? ORDER BY exception_date", (calendar_id,)
            ).fetchall()
        return self._calendar_from_row(row, breaks, exceptions)

    def delete_calendar(self, calendar_id: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM project_calendars WHERE calendar_id = ?", (calendar_id,))

    def save_activity(self, activity: ScheduleActivity) -> None:
        value = activity.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO schedule_activities(
                    activity_pk, schedule_id, activity_id, activity_name, activity_type,
                    source_boq_row_id, boq_item_code, boq_description, source_row_number,
                    quantity_text, unit, normalized_unit, wbs_id, productivity_rate_text,
                    productivity_basis, crew_count, calendar_id, notes, assumptions_json,
                    sort_order, created_at, updated_at
                ) VALUES (
                    :activity_pk, :schedule_id, :activity_id, :activity_name, :activity_type,
                    :source_boq_row_id, :boq_item_code, :boq_description, :source_row_number,
                    :quantity, :unit, :normalized_unit, :wbs_id, :productivity_rate,
                    :productivity_basis, :crew_count, :calendar_id, :notes, :assumptions_json,
                    :sort_order, :created_at, :updated_at
                )
                ON CONFLICT(activity_pk) DO UPDATE SET
                    activity_id = excluded.activity_id,
                    activity_name = excluded.activity_name,
                    activity_type = excluded.activity_type,
                    quantity_text = excluded.quantity_text,
                    unit = excluded.unit,
                    normalized_unit = excluded.normalized_unit,
                    wbs_id = excluded.wbs_id,
                    productivity_rate_text = excluded.productivity_rate_text,
                    productivity_basis = excluded.productivity_basis,
                    crew_count = excluded.crew_count,
                    calendar_id = excluded.calendar_id,
                    notes = excluded.notes,
                    assumptions_json = excluded.assumptions_json,
                    sort_order = excluded.sort_order,
                    updated_at = excluded.updated_at
                """,
                {**value, "assumptions_json": json.dumps(value["assumptions"], ensure_ascii=False)},
            )

    @staticmethod
    def _activity_from_row(row: sqlite3.Row) -> ScheduleActivity:
        value = dict(row)
        value["quantity"] = value.pop("quantity_text")
        value["productivity_rate"] = value.pop("productivity_rate_text")
        value["assumptions"] = json.loads(value.pop("assumptions_json"))
        return ScheduleActivity.from_dict(value)

    def list_activities(self, schedule_id: str) -> list[ScheduleActivity]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM schedule_activities WHERE schedule_id = ? ORDER BY sort_order, activity_id",
                (schedule_id,),
            ).fetchall()
        return [self._activity_from_row(row) for row in rows]

    def get_activity(self, activity_pk: str) -> ScheduleActivity | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM schedule_activities WHERE activity_pk = ?", (activity_pk,)).fetchone()
        return self._activity_from_row(row) if row else None

    def delete_activity(self, activity_pk: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM schedule_activities WHERE activity_pk = ?", (activity_pk,))

    def save_relationship(self, relationship: ActivityRelationship) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO activity_relationships(
                    relationship_id, schedule_id, predecessor_activity_pk, successor_activity_pk,
                    relationship_type, lag_hours_text, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(relationship_id) DO UPDATE SET
                    predecessor_activity_pk = excluded.predecessor_activity_pk,
                    successor_activity_pk = excluded.successor_activity_pk,
                    relationship_type = excluded.relationship_type,
                    lag_hours_text = excluded.lag_hours_text,
                    notes = excluded.notes
                """,
                (
                    relationship.relationship_id,
                    relationship.schedule_id,
                    relationship.predecessor_activity_pk,
                    relationship.successor_activity_pk,
                    relationship.relationship_type,
                    str(relationship.lag_hours),
                    relationship.notes,
                    relationship.created_at.isoformat(),
                ),
            )

    def list_relationships(self, schedule_id: str) -> list[ActivityRelationship]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM activity_relationships WHERE schedule_id = ? ORDER BY created_at, relationship_id",
                (schedule_id,),
            ).fetchall()
        return [ActivityRelationship.from_dict({**dict(row), "lag_hours": row["lag_hours_text"]}) for row in rows]

    def delete_relationship(self, relationship_id: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM activity_relationships WHERE relationship_id = ?", (relationship_id,))

    def save_schedule_run(self, run: ScheduleRun) -> None:
        value = run.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO schedule_runs(
                    run_id, schedule_id, engine_version, status, calculated_at,
                    project_planned_finish, completion_variance_days, validation_issues_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.schedule_id,
                    run.engine_version,
                    run.status,
                    run.calculated_at.isoformat(),
                    run.project_planned_finish.isoformat() if run.project_planned_finish else None,
                    run.completion_variance_days,
                    json.dumps(value["validation_issues"], ensure_ascii=False, sort_keys=True),
                ),
            )
            connection.executemany(
                """
                INSERT INTO schedule_activity_results(
                    run_id, activity_pk, exact_duration_hours_text, exact_duration_days_text,
                    display_duration_days_text, early_start, early_finish, formula,
                    calculation_trace_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run.run_id,
                        item.activity_pk,
                        str(item.exact_duration_hours),
                        str(item.exact_duration_days),
                        str(item.display_duration_days),
                        item.early_start.isoformat(),
                        item.early_finish.isoformat(),
                        item.formula,
                        json.dumps(item.calculation_trace, ensure_ascii=False, sort_keys=True),
                    )
                    for item in run.results
                ],
            )

    def latest_schedule_run(self, schedule_id: str) -> ScheduleRun | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM schedule_runs WHERE schedule_id = ? ORDER BY calculated_at DESC, run_id DESC LIMIT 1",
                (schedule_id,),
            ).fetchone()
            if not row:
                return None
            result_rows = connection.execute(
                "SELECT * FROM schedule_activity_results WHERE run_id = ? ORDER BY activity_pk", (row["run_id"],)
            ).fetchall()
        value = dict(row)
        value["validation_issues"] = json.loads(value.pop("validation_issues_json"))
        value["results"] = [
            {
                "activity_pk": item["activity_pk"],
                "exact_duration_hours": item["exact_duration_hours_text"],
                "exact_duration_days": item["exact_duration_days_text"],
                "display_duration_days": item["display_duration_days_text"],
                "early_start": item["early_start"],
                "early_finish": item["early_finish"],
                "formula": item["formula"],
                "calculation_trace": json.loads(item["calculation_trace_json"]),
            }
            for item in result_rows
        ]
        return ScheduleRun.from_dict(value)
