from __future__ import annotations

from construction_ai_orchestrator.policies.engine import BOQ_ITEM, QUANTITY, RATE, AccuracyPolicyEngine


def test_confirmed_quantity_requires_basis_and_source(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(QUANTITY, {
        "value": 100,
        "unit": {"code": "m3", "system": "SI"},
        "status": "confirmed",
        "measurement_basis": None,
        "source_ids": [],
        "assumption_id": None,
    })
    assert {item["code"] for item in report.blockers} == {
        "QUANTITY_BASIS_MISSING",
        "QUANTITY_SOURCE_MISSING",
    }


def test_allowance_requires_controlled_assumption(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(QUANTITY, {
        "value": 50,
        "unit": {"code": "m2", "system": "SI"},
        "status": "allowance",
        "measurement_basis": "Preliminary allowance",
        "source_ids": [],
        "assumption_id": None,
    })
    assert [item["code"] for item in report.blockers] == ["ALLOWANCE_ASSUMPTION_MISSING"]


def test_unknown_quantity_cannot_hide_a_number(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(QUANTITY, {
        "value": 1,
        "unit": {"code": "ea", "system": "SI"},
        "status": "unknown",
        "measurement_basis": None,
        "source_ids": [],
        "assumption_id": None,
    })
    assert report.blockers[0]["code"] == "NON_NUMERIC_STATUS_HAS_VALUE"


def test_zero_rate_requires_justification(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(RATE, {
        "rate_id": "RATE-001",
        "description": "Free-issued material",
        "value": {"amount": 0, "currency": "SAR", "base_date": "2026-07-01", "pricing_basis": "Supplier quotation"},
        "unit": {"code": "ea", "system": "SI"},
        "source_status": "quoted",
        "source_reference": "QUOTE-001",
        "zero_cost_justification": None,
        "inclusions": [],
        "exclusions": [],
    })
    assert report.blockers[0]["code"] == "RATE_ZERO_UNJUSTIFIED"


def test_unverified_rate_is_not_release_safe(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(RATE, {
        "rate_id": "RATE-002",
        "description": "Unverified rate",
        "value": {"amount": 10, "currency": "SAR", "base_date": "2026-07-01", "pricing_basis": "Unverified input"},
        "unit": {"code": "ea", "system": "SI"},
        "source_status": "unverified",
        "source_reference": None,
        "zero_cost_justification": None,
        "inclusions": [],
        "exclusions": [],
    })
    assert report.blockers[0]["code"] == "RATE_UNVERIFIED"


def test_priced_boq_requires_rate_and_total(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(BOQ_ITEM, {
        "boq_item_id": "BOQ-001",
        "wbs_id": "WBS-01",
        "cbs_code": None,
        "description": "Concrete",
        "quantity": {
            "value": 10,
            "unit": {"code": "m3", "system": "SI"},
            "status": "confirmed",
            "measurement_basis": "Drawing takeoff",
            "source_ids": ["DRG-001"],
            "assumption_id": None,
        },
        "rate_id": None,
        "total": None,
        "status": "priced",
        "evidence_ids": ["DRG-001"],
    })
    assert {item["code"] for item in report.blockers} == {"BOQ_RATE_MISSING", "BOQ_TOTAL_MISSING"}


def test_boq_cannot_hide_an_unsupported_confirmed_quantity(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(BOQ_ITEM, {
        "boq_item_id": "BOQ-002",
        "wbs_id": None,
        "cbs_code": None,
        "description": "Unsupported quantity",
        "quantity": {
            "value": 25,
            "unit": {"code": "m2", "system": "SI"},
            "status": "confirmed",
            "measurement_basis": None,
            "source_ids": [],
            "assumption_id": None,
        },
        "rate_id": None,
        "total": None,
        "status": "unpriced",
        "evidence_ids": [],
    })
    assert {item["code"] for item in report.blockers} == {
        "QUANTITY_BASIS_MISSING",
        "QUANTITY_SOURCE_MISSING",
    }
    assert all(item["path"].startswith("$.quantity") for item in report.blockers)
