from __future__ import annotations


def test_initial_migration_is_idempotent(scheduling_repository):
    scheduling_repository.initialize()
    with scheduling_repository._connect() as connection:
        versions = connection.execute("SELECT version FROM schema_migrations").fetchall()
    assert [row["version"] for row in versions] == ["001_initial"]


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
