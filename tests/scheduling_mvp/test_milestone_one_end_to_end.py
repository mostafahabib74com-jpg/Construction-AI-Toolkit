from __future__ import annotations

import json


def test_demonstration_project_and_boq_complete_milestone_one_flow(
    repo_root,
    project_service,
    boq_service,
):
    project_sample = json.loads(
        (repo_root / "apps/scheduling-mvp/sample_data/sample_project.json").read_text(encoding="utf-8")
    )
    assert project_sample["demonstration_data"] is True
    project = project_service.create_project(project_sample["project_input"])

    boq_path = repo_root / "apps/scheduling-mvp/sample_data/sample_boq.csv"
    preview = boq_service.preview(boq_path.name, boq_path.read_bytes())
    batch = boq_service.import_boq(
        project_id=project.project_id,
        file_name=boq_path.name,
        preview=preview,
        mapping={
            "item_code": "DEMONSTRATION_ITEM_CODE",
            "description": "DEMONSTRATION_DESCRIPTION",
            "quantity": "DEMONSTRATION_QUANTITY",
            "unit": "DEMONSTRATION_UNIT",
        },
    )

    assert len(batch.rows) == 3
    assert all(row.validation_status == "valid" for row in batch.rows)
    assert project_service.get_project(project.project_id) == project
    assert boq_service.get_rows(batch.import_id) == list(batch.rows)
