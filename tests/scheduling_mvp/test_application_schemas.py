from __future__ import annotations

from datetime import datetime, timezone

from construction_ai_scheduling.application.planning_contracts import (
    BOQ_IMPORT_ROW_SCHEMA,
    BOQ_IMPORT_SCHEMA,
    SCHEDULING_PROJECT_SCHEMA,
)


def test_milestone_one_schemas_are_registered(catalog):
    assert {SCHEDULING_PROJECT_SCHEMA, BOQ_IMPORT_SCHEMA, BOQ_IMPORT_ROW_SCHEMA} <= set(catalog.schema_ids)


def test_incomplete_boq_row_is_a_valid_draft_contract(catalog):
    row = {
        "row_id": "BOQ-1",
        "project_id": "PRJ-1",
        "import_id": "IMP-1",
        "source_row_number": 2,
        "item_code": None,
        "description": None,
        "quantity": None,
        "quantity_raw": None,
        "unit": None,
        "validation_status": "incomplete",
        "validation_errors": ["[BOQ_DESCRIPTION_REQUIRED] Description is required."],
        "raw_data": {},
    }
    catalog.assert_valid(row, BOQ_IMPORT_ROW_SCHEMA)


def test_import_contract_requires_row_count(catalog):
    value = {
        "import_id": "IMP-1",
        "project_id": "PRJ-1",
        "source_file_name": "boq.csv",
        "source_type": "csv",
        "source_sheet": None,
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "rows": [],
    }
    issues = catalog.validate(value, BOQ_IMPORT_SCHEMA)
    assert issues[0]["path"] == "$"
