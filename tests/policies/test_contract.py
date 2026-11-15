from __future__ import annotations

from construction_ai_orchestrator.policies.engine import CONTRACT_REQUIREMENT, AccuracyPolicyEngine


def requirement(**overrides):
    value = {
        "requirement_id": "REQ-001",
        "text": "Submit a performance bond.",
        "basis": "source_fact",
        "mandatory": True,
        "status": "confirmed",
        "evidence_ids": ["EVD-001"],
        "assumption_id": None,
        "owner_role": "Contracts Manager",
        "response_reference": None,
    }
    value.update(overrides)
    return value


def test_sourced_contract_fact_is_allowed(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(CONTRACT_REQUIREMENT, requirement())
    assert report.blockers == ()


def test_contract_fact_without_evidence_is_blocked(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(CONTRACT_REQUIREMENT, requirement(evidence_ids=[]))
    assert report.blockers[0]["code"] == "CONTRACT_EVIDENCE_MISSING"


def test_inference_cannot_be_confirmed_as_contract_fact(catalog):
    report = AccuracyPolicyEngine(catalog).evaluate(
        CONTRACT_REQUIREMENT,
        requirement(basis="inference", evidence_ids=[], assumption_id=None),
    )
    assert {item["code"] for item in report.blockers} == {
        "CONTRACT_ASSUMPTION_LINK_MISSING",
        "INFERRED_CONTRACT_REQUIREMENT_CONFIRMED",
    }
