"""Normalized SQLite persistence for projects and draft BOQ imports."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from construction_ai_scheduling.domain.models import BOQImport, BOQRow, Project


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
        migration = self.migration_path.read_text(encoding="utf-8")
        with self._connect() as connection:
            connection.executescript(migration)

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
                    quantity, quantity_raw_json, unit, validation_status,
                    validation_errors_json, raw_data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    unit = ?, validation_status = ?, validation_errors_json = ?
                WHERE row_id = ? AND import_id = ? AND project_id = ?
                """,
                [
                    (
                        row.item_code,
                        row.description,
                        row.quantity,
                        json.dumps(row.quantity_raw, ensure_ascii=False),
                        row.unit,
                        row.validation_status,
                        json.dumps(row.validation_errors, ensure_ascii=False),
                        row.row_id,
                        row.import_id,
                        row.project_id,
                    )
                    for row in rows
                ],
            )
