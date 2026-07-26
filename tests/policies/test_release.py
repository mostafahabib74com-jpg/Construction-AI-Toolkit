from __future__ import annotations

from construction_ai_orchestrator.policies.engine import DELIVERABLE, AccuracyPolicyEngine


def deliverable(**overrides):
    value = {
        "deliverable_id": "DEL-001",
        "name": "Commercial Proposal",
        "deliverable_type": "commercial_proposal",
        "status": "approved",
        "mandatory_fields": ["tender_sum", "currency"],
        "missing_fields": [],
        "field_values": {"tender_sum": 1000, "currency": "SAR"},
        "artifact_reference": {"artifact_id": "ART-001", "version": "1.0"},
        "due_at": "2026-08-01T12:00:00+03:00",
        "review": {
            "status": "approved",
            "required_roles": ["Commercial Manager"],
            "reviewed_by": ["Commercial Manager"],
            "reviewed_at": "2026-07-30T12:00:00+03:00",
            "notes": None,
            "authorization_reference": "APR-001",
        },
    }
    value.update(overrides)
    return value


def test_complete_approved_deliverable_passes(catalog):
    assert AccuracyPolicyEngine(catalog).evaluate(DELIVERABLE, deliverable()).blockers == ()


def test_missing_mandatory_value_blocks_release(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(
        DELIVERABLE,
        deliverable(field_values={"currency": "SAR"}),
    )
    assert report.blockers[0]["code"] == "DELIVERABLE_MANDATORY_FIELDS_MISSING"
    assert report.blockers[0]["details"]["missing_fields"] == ["tender_sum"]


def test_unapproved_document_cannot_be_submitted(catalog):
    invalid_review = deliverable()["review"] | {"status": "in_review"}
    report = AccuracyPolicyEngine(catalog).evaluate(
        DELIVERABLE,
        deliverable(status="submitted", review=invalid_review),
    )
    assert report.blockers[0]["code"] == "DELIVERABLE_APPROVAL_MISSING"
