from __future__ import annotations

from construction_ai_orchestrator.runner import Orchestrator

FIXED_TIME = "2026-07-26T10:00:00Z"
QUANTITY_SCHEMA = "https://construction-ai-toolkit.dev/contracts/v1/core/quantity.schema.json"


def build_artifact(workflow, request, context, *, source_ids, status="validated"):
    artifact = {
        "artifact_id": "QTY-001",
        "project_id": request["project"]["project_id"],
        "artifact_type": "quantity",
        "schema_id": QUANTITY_SCHEMA,
        "schema_version": "1.0.0",
        "version": "1.0.0",
        "status": status,
        "producer": {"agent_id": workflow.agent_id, "workflow_id": workflow.workflow_id, "run_id": context.run_id},
        "created_at": FIXED_TIME,
        "lineage": [],
        "uri": None,
        "payload": {
            "value": 10,
            "unit": {"code": "m3", "system": "SI"},
            "status": "confirmed",
            "measurement_basis": "Drawing takeoff",
            "source_ids": source_ids,
            "assumption_id": None,
        },
    }
    if status == "approved":
        artifact["review"] = {
            "status": "approved",
            "required_roles": ["Estimation Manager"],
            "reviewed_by": ["Estimation Manager"],
            "reviewed_at": FIXED_TIME,
            "notes": None,
            "authorization_reference": "APR-001",
        }
    return artifact


def make_orchestrator(registry, catalog, handler):
    return Orchestrator(
        registry=registry,
        catalog=catalog,
        handlers={"estimation-agent/boq-development": handler},
        clock=lambda: FIXED_TIME,
        id_factory=lambda: "RUN-POLICY-001",
    )


def test_release_artifact_without_quantity_source_is_blocked(registry, catalog, request_factory):
    def handler(workflow, request, context):
        return {"status": "complete", "summary": "Candidate produced.", "artifacts": [build_artifact(workflow, request, context, source_ids=[])]}

    request = request_factory(agent_id="estimation-agent", workflow_id="boq-development")
    result = make_orchestrator(registry, catalog, handler).run(request)
    assert result["status"] == "blocked"
    assert result["blockers"][0]["code"] == "QUANTITY_SOURCE_MISSING"
    assert result["artifact_manifest"] == []


def test_release_artifact_with_quantity_evidence_is_registered(registry, catalog, request_factory):
    def handler(workflow, request, context):
        return {"status": "complete", "summary": "Candidate produced.", "artifacts": [build_artifact(workflow, request, context, source_ids=["DRG-001"])]}

    request = request_factory(agent_id="estimation-agent", workflow_id="boq-development")
    result = make_orchestrator(registry, catalog, handler).run(request)
    assert result["status"] == "complete"
    assert result["artifact_manifest"][0]["artifact_id"] == "QTY-001"
    assert result["final_deliverables"] == []


def test_only_professionally_approved_artifact_becomes_final_deliverable(registry, catalog, request_factory):
    def handler(workflow, request, context):
        artifact = build_artifact(workflow, request, context, source_ids=["DRG-001"], status="approved")
        return {"status": "complete", "summary": "Approved candidate produced.", "artifacts": [artifact]}

    request = request_factory(agent_id="estimation-agent", workflow_id="boq-development")
    result = make_orchestrator(registry, catalog, handler).run(request)
    assert result["status"] == "complete"
    assert result["final_deliverables"] == [{"artifact_id": "QTY-001", "version": "1.0.0"}]


def test_artifact_cannot_claim_approval_without_review(registry, catalog, request_factory):
    def handler(workflow, request, context):
        artifact = build_artifact(workflow, request, context, source_ids=["DRG-001"], status="approved")
        del artifact["review"]
        return {"status": "complete", "summary": "Unreviewed candidate produced.", "artifacts": [artifact]}

    request = request_factory(agent_id="estimation-agent", workflow_id="boq-development")
    result = make_orchestrator(registry, catalog, handler).run(request)
    assert result["status"] == "blocked"
    assert result["blockers"][0]["code"] == "ARTIFACT_APPROVAL_MISSING"


def test_release_artifact_without_schema_is_blocked(registry, catalog, request_factory):
    def handler(workflow, request, context):
        artifact = build_artifact(workflow, request, context, source_ids=["DRG-001"])
        artifact["schema_id"] = None
        artifact["schema_version"] = None
        return {"status": "complete", "summary": "Candidate produced.", "artifacts": [artifact]}

    request = request_factory(agent_id="estimation-agent", workflow_id="boq-development")
    result = make_orchestrator(registry, catalog, handler).run(request)
    assert result["status"] == "blocked"
    assert {item["code"] for item in result["blockers"]} == {
        "ARTIFACT_SCHEMA_MISSING",
        "ARTIFACT_SCHEMA_VERSION_MISSING",
    }
