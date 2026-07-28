from __future__ import annotations

import sqlite3

from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository


def test_initial_migration_is_idempotent(scheduling_repository):
    scheduling_repository.initialize()
    with scheduling_repository._connect() as connection:
        versions = connection.execute("SELECT version FROM schema_migrations").fetchall()
    assert [row["version"] for row in versions] == [
        "001_initial",
        "002_boq_normalized_unit",
        "003_scheduling_engine",
    ]


def test_existing_milestone_one_database_receives_normalized_unit_column(tmp_path, repo_root):
    database_path = tmp_path / "legacy.db"
    migration_path = repo_root / "apps/scheduling-mvp/migrations/001_initial.sql"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(migration_path.read_text(encoding="utf-8"))

    repository = SQLiteRepository(database_path, migration_path)
    repository.initialize()

    with repository._connect() as connection:
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(boq_items)").fetchall()}
        versions = {row["version"] for row in connection.execute("SELECT version FROM schema_migrations").fetchall()}
    assert "normalized_unit" in columns
    assert "002_boq_normalized_unit" in versions
    assert "003_scheduling_engine" in versions


def test_import_summary_is_scoped_to_project(boq_service, project_service, saved_project, valid_project_input):
    second_input = dict(valid_project_input)
    second_input["name"] = "Second Project"
    second = project_service.create_project(second_input)
    preview = boq_service.preview("boq.csv", b"Description,Quantity,Unit\nConcrete,1,m3\n")
    batch = boq_service.import_boq(
        project_id=saved_project.project_id,
        file_name="boq.csv",
        preview=preview,
        mapping={"item_code": None, "description": "Description", "quantity": "Quantity", "unit": "Unit"},
    )

    assert boq_service.list_imports(second.project_id) == []
    assert boq_service.list_imports(saved_project.project_id)[0]["import_id"] == batch.import_id
