from __future__ import annotations

from construction_ai_orchestrator.adapters import PlanningAdapter, TenderAdapter

FIXED_TIME = "2026-07-26T10:00:00Z"


def test_tender_source_preserves_control_and_unknown_checksum_algorithm(catalog):
    source = TenderAdapter(catalog).adapt_source_document({
        "source_id": "TND-001",
        "title": "Tender Conditions",
        "revision": "A",
        "issue_date": "2026-07-01",
        "location": "Volume 1",
        "checksum": "vendor-checksum-value",
        "classification": "confidential",
        "extraction_method": "manual_register",
        "confidence": 0.8,
        "controlled_status": "reference_only",
    })
    assert source["controlled_status"] == "reference_only"
    assert source["checksum_algorithm"] == "unspecified"
    assert source["checksum_value"] == "vendor-checksum-value"
    assert source["checksum_sha256"] is None


def test_tender_artifact_approval_mapping(catalog):
    artifact = TenderAdapter(catalog).adapt_artifact_reference(
        {
            "artifact_id": "ART-100",
            "agent_id": "estimation-agent",
            "workflow_id": "boq-development",
            "version": "1.0",
            "approval_status": "approved",
            "artifact_reference": "artifact://ART-100/1.0",
            "approved_by_role": "Estimation Manager",
            "approved_at": FIXED_TIME,
        },
        project_id="P-001",
        run_id="RUN-001",
        created_at=FIXED_TIME,
        artifact_type="boq",
    )
    assert artifact["status"] == "approved"
    assert artifact["review"]["status"] == "approved"
    assert artifact["review"]["reviewed_by"] == ["Estimation Manager"]


def test_planning_schedule_reference_is_not_promoted_to_approved(catalog):
    artifact = PlanningAdapter(catalog).adapt_schedule_reference(
        {
            "project_id": "P-001",
            "schedule_id": "SCH-001",
            "version": "2",
            "data_date": FIXED_TIME,
            "status": "forecast",
            "artifact_reference": "artifact://SCH-001/2",
        },
        workflow_id="progress-update",
        run_id="RUN-002",
        created_at=FIXED_TIME,
    )
    assert artifact["status"] == "generated"
    assert artifact["schema_id"] is None
