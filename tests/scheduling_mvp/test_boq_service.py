from __future__ import annotations

import pytest

from construction_ai_scheduling.domain.errors import BOQImportError


def test_import_stores_valid_and_incomplete_rows(boq_service, saved_project):
    content = b"Code,Description,Quantity,Unit\nA-1,Concrete,10,m3\nA-2,,25,\n"
    preview = boq_service.preview("boq.csv", content)
    batch = boq_service.import_boq(
        project_id=saved_project.project_id,
        file_name="boq.csv",
        preview=preview,
        mapping={
            "item_code": "Code",
            "description": "Description",
            "quantity": "Quantity",
            "unit": "Unit",
        },
    )

    assert [row.validation_status for row in batch.rows] == ["valid", "incomplete"]
    stored = boq_service.get_rows(batch.import_id)
    assert stored == list(batch.rows)
    assert stored[1].description is None
    assert stored[1].unit is None


def test_unmapped_quantity_is_not_fabricated(boq_service, saved_project):
    preview = boq_service.preview("boq.csv", b"Description,Unit\nConcrete,m3\n")
    batch = boq_service.import_boq(
        project_id=saved_project.project_id,
        file_name="boq.csv",
        preview=preview,
        mapping={"item_code": None, "description": "Description", "quantity": None, "unit": "Unit"},
    )
    row = batch.rows[0]
    assert row.quantity is None
    assert row.quantity_raw is None
    assert row.validation_status == "incomplete"


def test_edit_revalidates_and_preserves_source_data(boq_service, saved_project):
    preview = boq_service.preview("boq.csv", b"Description,Quantity,Unit\nConcrete,TBC,m3\n")
    batch = boq_service.import_boq(
        project_id=saved_project.project_id,
        file_name="boq.csv",
        preview=preview,
        mapping={"item_code": None, "description": "Description", "quantity": "Quantity", "unit": "Unit"},
    )
    original = batch.rows[0]
    assert original.validation_status == "invalid"

    updated = boq_service.update_rows(batch.import_id, [{
        "row_id": original.row_id,
        "item_code": "A-1",
        "description": "Concrete",
        "quantity": 15,
        "unit": "m3",
    }])
    assert updated[0].validation_status == "valid"
    assert updated[0].quantity == 15.0
    assert updated[0].raw_data == original.raw_data


def test_source_file_name_is_reduced_to_basename(boq_service, saved_project):
    preview = boq_service.preview("boq.csv", b"Description,Quantity,Unit\nConcrete,1,m3\n")
    batch = boq_service.import_boq(
        project_id=saved_project.project_id,
        file_name="../unsafe/boq.csv",
        preview=preview,
        mapping={"item_code": None, "description": "Description", "quantity": "Quantity", "unit": "Unit"},
    )
    assert batch.source_file_name == "boq.csv"


def test_header_only_boq_is_rejected(boq_service, saved_project):
    preview = boq_service.preview("boq.csv", b"Description,Quantity,Unit\n")
    with pytest.raises(BOQImportError, match="does not contain any data rows"):
        boq_service.import_boq(
            project_id=saved_project.project_id,
            file_name="boq.csv",
            preview=preview,
            mapping={"item_code": None, "description": "Description", "quantity": "Quantity", "unit": "Unit"},
        )
