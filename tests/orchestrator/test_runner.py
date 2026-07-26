from __future__ import annotations

from construction_ai_orchestrator.runner import Orchestrator

FIXED_TIME = "2026-07-26T10:00:00Z"


def make_artifact(workflow, request, run_id, *, artifact_id="ART-001", lineage=None):
    return {
        "artifact_id": artifact_id,
        "project_id": request["project"]["project_id"],
        "artifact_type": "controlled_test_artifact",
        "schema_id": None,
        "schema_version": None,
        "version": "1.0.0",
        "status": "validated",
        "producer": {
            "agent_id": workflow.agent_id,
            "workflow_id": workflow.workflow_id,
            "run_id": run_id,
        },
        "created_at": FIXED_TIME,
        "lineage": lineage or [],
        "uri": None,
        "payload": {"synthetic": True},
    }


def orchestrator(registry, catalog, handlers=None):
    ids = iter(["RUN-001", "RUN-002", "RUN-003"])
    return Orchestrator(
        registry=registry,
        catalog=catalog,
        handlers=handlers,
        clock=lambda: FIXED_TIME,
        id_factory=lambda: next(ids),
    )


def test_missing_handler_returns_visible_blocker(registry, catalog, request_factory):
    request = request_factory(agent_id="estimation-agent", workflow_id="rfp-analysis")
    result = orchestrator(registry, catalog).run(request)
    assert result["status"] == "blocked"
    assert result["workflow_runs"][0]["qualified_workflow_id"] == "estimation-agent/rfp-analysis"
    assert result["blockers"][0]["code"] == "HANDLER_NOT_AVAILABLE"
    assert result["artifact_manifest"] == []


def test_invalid_request_returns_typed_blocker(registry, catalog):
    result = orchestrator(registry, catalog).run({"request_id": "BAD-001"})
    assert result["status"] == "blocked"
    assert result["blockers"][0]["code"] == "CONTRACT_VALIDATION_ERROR"
    assert "Traceback" not in result["blockers"][0]["message"]


def test_handler_output_is_registered_and_consolidated(registry, catalog, request_factory):
    def handler(workflow, request, context):
        return {
            "status": "complete",
            "summary": "Synthetic handler completed.",
            "artifacts": [make_artifact(workflow, request, context.run_id)],
        }

    key = "estimation-agent/rfp-analysis"
    request = request_factory(agent_id="estimation-agent", workflow_id="rfp-analysis")
    result = orchestrator(registry, catalog, {key: handler}).run(request)
    assert result["status"] == "complete"
    assert result["artifact_manifest"][0]["artifact_id"] == "ART-001"
    assert result["final_deliverables"] == [{"artifact_id": "ART-001", "version": "1.0.0"}]


def test_sequence_passes_artifact_references_between_agents(registry, catalog, request_factory):
    observed = {}

    def tender_handler(workflow, request, context):
        return {
            "status": "complete",
            "summary": "Tender intake complete.",
            "artifacts": [make_artifact(workflow, request, context.run_id, artifact_id="TENDER-SCOPE")],
        }

    def estimation_handler(workflow, request, context):
        observed["upstream"] = request["upstream_artifacts"]
        observed["resolved_upstream"] = context.upstream_artifacts
        return {
            "status": "complete",
            "summary": "Estimation intake complete.",
            "artifacts": [
                make_artifact(
                    workflow,
                    request,
                    context.run_id,
                    artifact_id="ESTIMATE-INPUT",
                    lineage=request["upstream_artifacts"],
                )
            ],
        }

    handlers = {
        "tender-manager-agent/tender-package-ingestion": tender_handler,
        "estimation-agent/rfp-analysis": estimation_handler,
    }
    requests = [
        request_factory(request_id="SEQ-001", agent_id="tender-manager-agent", workflow_id="tender-package-ingestion"),
        request_factory(request_id="SEQ-002", agent_id="estimation-agent", workflow_id="rfp-analysis"),
    ]
    result = orchestrator(registry, catalog, handlers).run_sequence(requests)
    assert result["status"] == "complete"
    assert observed["upstream"] == [{"artifact_id": "TENDER-SCOPE", "version": "1.0.0"}]
    assert observed["resolved_upstream"][0]["artifact_id"] == "TENDER-SCOPE"
    assert observed["resolved_upstream"][0]["payload"] == {"synthetic": True}
    assert [item["artifact_id"] for item in result["artifact_manifest"]] == ["ESTIMATE-INPUT", "TENDER-SCOPE"]


def test_unexpected_handler_error_is_sanitized(registry, catalog, request_factory):
    def handler(workflow, request, context):
        raise RuntimeError("secret implementation detail")

    key = "planning-p6-agent/wbs-development"
    request = request_factory(agent_id="planning-p6-agent", workflow_id="wbs-development")
    result = orchestrator(registry, catalog, {key: handler}).run(request)
    issue = result["issues"][0]
    assert result["status"] == "failed"
    assert issue["code"] == "WORKFLOW_EXECUTION_FAILED"
    assert "secret" not in issue["message"]
