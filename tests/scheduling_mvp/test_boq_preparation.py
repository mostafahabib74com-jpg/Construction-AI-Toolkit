from io import BytesIO
import pytest
from openpyxl import Workbook

from construction_ai_scheduling.application.boq_preparation import prepare_boq
from construction_ai_scheduling.infrastructure.boq_reader import TabularBOQReader
from construction_ai_scheduling.domain.errors import BOQImportError
from construction_ai_scheduling.domain.units import normalize_unit


def preview(*, conflicting_units=False):
    book = Workbook()
    sheet = book.active
    sheet.append(["Item", "Description", "Unit", "Quantity"])
    sheet.append([1.1, "Equipment package", None, None])
    sheet.append([None, "Supply and install, including testing", None, None])
    sheet.append(["1.1.1", "Electric pump", "set", 1])
    sheet.append([None, "Diesel pump", "m" if conflicting_units else "set", None])
    sheet.append([None, "Jockey pump", "set", None])
    sheet.merge_cells("A4:A6")
    sheet.merge_cells("D4:D6")
    sheet.append(["1.1.2", "Unconfirmed measurable item", "m", None])
    sheet.append(["TOTAL", None, None, None])
    stream = BytesIO()
    book.save(stream)
    return TabularBOQReader().read("synthetic.xlsx", stream.getvalue())


MAPPING = {"item_code": "Item", "description": "Description", "unit": "Unit", "quantity": "Quantity"}


def test_arabic_work_description_header_is_detected_without_assuming_price_columns():
    result = TabularBOQReader.suggest_mapping(("رقم البند", "وصف العمل", "الوحدة", "الكمية", "السعر الإفرادي"))
    assert result == {"item_code": "رقم البند", "description": "وصف العمل", "quantity": "الكمية", "unit": "الوحدة"}


def test_preparation_is_opt_in_and_original_preview_is_unchanged():
    source = preview()
    prepared = prepare_boq(source, MAPPING)
    assert prepared.preview.frame.equals(source.frame)
    assert len(source.frame) == 7
    assert not prepared.combined_groups
    assert not prepared.excluded_rows


def test_merged_shared_quantity_is_used_once_and_scope_evidence_is_retained():
    source = preview()
    prepared = prepare_boq(source, MAPPING, combine_merged_items=True, exclude_structural_rows=True)
    extracted = TabularBOQReader.extract_rows(prepared.preview.frame, MAPPING)
    assert len(extracted) == 2
    assert prepared.combined_groups == ((4, 5, 6),)
    assert [row["source_row"] for row in prepared.excluded_rows] == [2, 3, 8]
    group = extracted[0]
    assert group["quantity"] == 1
    assert group["description"] == "Electric pump\nDiesel pump\nJockey pump"
    assert group["raw_data"]["_import_preparation"]["source_rows"] == [4, 5, 6]
    assert group["raw_data"]["_import_preparation"]["scope_context"][-1]["description"] == "Supply and install, including testing"
    assert extracted[1]["quantity"] is None  # no fabricated quantity for an unrelated incomplete item
    assert source.frame.loc[4, "Description"] == "Electric pump"


def test_conflicting_units_block_composite_group():
    with pytest.raises(BOQImportError, match="conflicting units"):
        prepare_boq(preview(conflicting_units=True), MAPPING, combine_merged_items=True)


@pytest.mark.parametrize(("source", "canonical"), [("م ط", "m"), ("م.ط", "m"), ("مجموعة", "set"), ("قاطوعة", "ls")])
def test_common_arabic_unit_labels_keep_a_canonical_measurement(source, canonical):
    assert normalize_unit(source) == canonical
