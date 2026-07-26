from __future__ import annotations

import pytest

from construction_ai_orchestrator.adapters import EstimationAdapter, PlanningAdapter, TenderAdapter
from construction_ai_orchestrator.errors import AdapterValidationError


@pytest.mark.parametrize("adapter_type", [EstimationAdapter, PlanningAdapter, TenderAdapter])
def test_project_adapter_requires_explicit_time_zone(catalog, adapter_type):
    adapter = adapter_type(catalog)
    legacy = {
        "project_id": "P-001",
        "name": "Test Project",
        "location": "Riyadh",
        "currency": "SAR",
        "unit_system": "SI",
    }
    with pytest.raises(AdapterValidationError):
        adapter.adapt_project(legacy)
    canonical = adapter.adapt_project(legacy, time_zone="Asia/Riyadh")
    assert canonical["time_zone"] == "Asia/Riyadh"


def test_estimation_source_mapping_is_visible_and_controlled(catalog):
    source = EstimationAdapter(catalog).adapt_source_document({
        "source_id": "DOC-001",
        "title": "RFP",
        "revision": "01",
        "date": "2026-01-15",
        "location": "Section 1",
        "extraction_method": "native",
        "confidence": 1.0,
    })
    assert source["document_id"] == "DOC-001"
    assert source["issue_date"] == "2026-01-15"
    assert source["controlled_status"] == "unverified"
    assert source["uri"] == "Section 1"


def test_planning_source_does_not_invent_issue_date(catalog):
    source = PlanningAdapter(catalog).adapt_source_document({
        "source_id": "PLAN-001",
        "title": "Baseline",
        "revision": "0",
        "location": "Schedule file",
        "extraction_method": "structured_import",
        "confidence": 0.9,
    })
    assert source["issue_date"] is None
    assert source["controlled_status"] == "unverified"


def test_review_status_is_mapped_without_approval_inference(catalog):
    review = EstimationAdapter(catalog).adapt_review({
        "required_roles": ["Estimation Manager"],
        "status": "revision_required",
        "comments": ["Correct rate source."],
    })
    assert review["status"] == "revision_required"
    assert review["reviewed_by"] == []
    assert review["notes"] == "Correct rate source."


def test_estimation_quantity_requires_explicit_unit_system(catalog):
    adapter = EstimationAdapter(catalog)
    quantity = adapter.adapt_quantity(
        {
            "value": 10,
            "unit": "m3",
            "basis": "measured",
            "source": {"source_id": "DOC-001"},
        },
        unit_system="SI",
    )
    assert quantity["unit"] == {"code": "m3", "system": "SI"}
    assert quantity["source_ids"] == ["DOC-001"]
