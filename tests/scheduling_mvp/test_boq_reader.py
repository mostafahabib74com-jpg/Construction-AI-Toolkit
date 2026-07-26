from __future__ import annotations

from io import BytesIO

import openpyxl
import pytest

from construction_ai_scheduling.domain.errors import BOQImportError
from construction_ai_scheduling.infrastructure.boq_reader import TabularBOQReader


def test_csv_reader_suggests_unambiguous_columns():
    content = b"Item No,Description,Qty,UOM\nA-1,Concrete,10,m3\n"
    preview = TabularBOQReader().read("boq.csv", content)
    mapping = TabularBOQReader.suggest_mapping(preview.columns)

    assert mapping == {
        "item_code": "Item No",
        "description": "Description",
        "quantity": "Qty",
        "unit": "UOM",
    }
    rows = TabularBOQReader.extract_rows(preview.frame, mapping)
    assert rows[0]["quantity"] == 10.0
    assert rows[0]["source_row_number"] == 2


def test_reader_does_not_guess_ambiguous_description_column():
    content = b"Description,Item Description,Qty,UOM\nA,B,10,m3\n"
    preview = TabularBOQReader().read("boq.csv", content)
    assert TabularBOQReader.suggest_mapping(preview.columns)["description"] is None


def test_reader_preserves_invalid_quantity_for_review():
    content = b"Description,Qty,UOM\nConcrete,TBC,m3\n"
    preview = TabularBOQReader().read("boq.csv", content)
    rows = TabularBOQReader.extract_rows(preview.frame, {
        "item_code": None,
        "description": "Description",
        "quantity": "Qty",
        "unit": "UOM",
    })
    assert rows[0]["quantity"] is None
    assert rows[0]["quantity_raw"] == "TBC"


def test_xlsx_reader_selects_requested_worksheet():
    workbook = openpyxl.Workbook()
    first = workbook.active
    first.title = "Cover"
    first.append(["Notes"])
    first.append(["Demonstration only"])
    boq = workbook.create_sheet("BOQ")
    boq.append(["Description", "Quantity", "Unit"])
    boq.append(["Concrete", 12, "m3"])
    stream = BytesIO()
    workbook.save(stream)

    preview = TabularBOQReader().read("boq.xlsx", stream.getvalue(), sheet_name="BOQ")
    assert preview.sheet_names == ("Cover", "BOQ")
    assert preview.selected_sheet == "BOQ"
    assert preview.frame.iloc[0]["Quantity"] == 12


def test_reader_rejects_unsupported_or_empty_files():
    reader = TabularBOQReader()
    with pytest.raises(BOQImportError, match="CSV or XLSX"):
        reader.read("boq.xls", b"data")
    with pytest.raises(BOQImportError, match="empty"):
        reader.read("boq.csv", b"")
