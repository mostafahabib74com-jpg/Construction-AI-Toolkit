from __future__ import annotations

import pytest

from construction_ai_scheduling.domain.units import normalize_unit
from construction_ai_scheduling.domain.validation import boq_validation_status, validate_boq_fields


def test_valid_boq_fields_pass():
    issues = validate_boq_fields(description="Concrete", quantity=10.0, quantity_raw=10, unit="m3")
    assert issues == []
    assert boq_validation_status(issues) == "valid"


def test_missing_boq_values_are_incomplete():
    issues = validate_boq_fields(description=None, quantity=None, quantity_raw=None, unit=None)
    assert {issue.code for issue in issues} == {
        "BOQ_DESCRIPTION_REQUIRED",
        "BOQ_QUANTITY_REQUIRED",
        "BOQ_UNIT_REQUIRED",
    }
    assert boq_validation_status(issues) == "incomplete"


def test_non_numeric_quantity_is_invalid():
    issues = validate_boq_fields(description="Concrete", quantity=None, quantity_raw="unknown", unit="m3")
    assert [issue.code for issue in issues] == ["BOQ_QUANTITY_INVALID"]
    assert boq_validation_status(issues) == "invalid"


def test_negative_quantity_is_invalid():
    issues = validate_boq_fields(description="Concrete", quantity=-1.0, quantity_raw=-1, unit="m3")
    assert [issue.code for issue in issues] == ["BOQ_QUANTITY_NEGATIVE"]
    assert boq_validation_status(issues) == "invalid"


@pytest.mark.parametrize(
    "unit",
    ["م", "م2", "م²", "م3", "م³", "عدد", "كجم", "طن", "مقطوعية", "m", "m2", "m²", "m3", "m³", "kg", "Lump Sum"],
)
def test_arabic_and_english_construction_units_are_valid(unit):
    issues = validate_boq_fields(description="أعمال إنشائية", quantity=1.0, quantity_raw=1, unit=unit)
    assert issues == []


def test_equivalent_area_and_volume_units_share_canonical_values():
    assert {normalize_unit(unit) for unit in ("م2", "م²", "m2", "m²")} == {"m2"}
    assert {normalize_unit(unit) for unit in ("م3", "م³", "m3", "m³")} == {"m3"}
