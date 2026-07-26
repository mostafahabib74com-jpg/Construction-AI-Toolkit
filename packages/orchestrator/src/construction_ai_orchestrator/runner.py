"""Safe workflow execution boundary and cross-agent handoff."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from typing import Any
from uuid import uuid4

from .artifacts import ArtifactStore
from .consolidation import consolidate, utc_now
from .errors import HandlerNotAvailableError, PlatformError
from .models import ExecutionContext, WorkflowDefinition
from .registry import AgentRegistry
from .router import WorkflowRouter
from .validation import SchemaCatalog

REQUEST_SCHEMA_ID = "https://construction-ai-toolkit.dev/contracts/v1/core/workflow-request.schema.json"
RESULT_SCHEMA_ID = "https://construction-ai-toolkit.dev/contracts/v1/core/workflow-result.schema.json"

WorkflowHandler = Callable[[WorkflowDefinition, dict[str, Any], ExecutionContext], Mapping[str, Any]]


def _execution_failure(message: str) -> dict[str, Any]:
    return {
        "code": "WORKFLOW_EXECUTION_FAILED",
        "message": message,
        "severity": "error",
        "recoverable": False,
        "path": None,
        "remediation": "Inspect the registered workflow handler and retry after correction.",
        "details": {},
    }


class Orchestrator:
    def __init__(
        self,
        *,
        registry: AgentRegistry,
        catalog: SchemaCatalog,
        handlers: Mapping[str, WorkflowHandler] | None = None,
        clock: Callable[[], str] = utc_now,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self.registry = registry
        self.catalog = catalog
        self.router = WorkflowRouter(registry)
        self.handlers = dict(handlers or {})
        self.clock = clock
        self.id_factory = id_factory or (lambda: str(uuid4()))

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        store = ArtifactStore(self.catalog)
        request_id = request.get("request_id", "unknown-request") if isinstance(request, dict) else "unknown-request"
        try:
            run = self._execute(request, store)
        except PlatformError as exc:
            return consolidate(
                request_id=str(request_id),
                runs=[],
                artifact_store=store,
                catalog=self.catalog,
                extra_blockers=[exc.to_issue()],
                clock=self.clock,
            )
        return consolidate(
            request_id=str(request_id),
            runs=[run],
            artifact_store=store,
            catalog=self.catalog,
            clock=self.clock,
        )

    def run_sequence(self, requests: Sequence[dict[str, Any]]) -> dict[str, Any]:
        if not requests:
            return self.run({})
        store = ArtifactStore(self.catalog)
        runs: list[dict[str, Any]] = []
        sequence_id = str(requests[0].get("request_id", "unknown-request"))
        extra_blockers: list[dict[str, Any]] = []
        for original in requests:
            try:
                self.catalog.assert_valid(original, REQUEST_SCHEMA_ID)
                request = deepcopy(original)
                existing = request.get("upstream_artifacts", [])
                combined = {(item["artifact_id"], item["version"]) for item in existing}
                combined.update((item["artifact_id"], item["version"]) for item in store.references())
                request["upstream_artifacts"] = [
                    {"artifact_id": artifact_id, "version": version}
                    for artifact_id, version in sorted(combined)
                ]
                run = self._execute(request, store)
            except PlatformError as exc:
                extra_blockers.append(exc.to_issue())
                break
            runs.append(run)
            if run["status"] in {"blocked", "failed"}:
                break
        return consolidate(
            request_id=sequence_id,
            runs=runs,
            artifact_store=store,
            catalog=self.catalog,
            extra_blockers=extra_blockers,
            clock=self.clock,
        )

    def _execute(self, request: dict[str, Any], store: ArtifactStore) -> dict[str, Any]:
        self.catalog.assert_valid(request, REQUEST_SCHEMA_ID)
        workflow = self.router.route(request["selector"])
        run_id = self.id_factory()
        handler = self.handlers.get(workflow.qualified_id)
        if handler is None:
            blocker = HandlerNotAvailableError(
                f"Workflow '{workflow.qualified_id}' is declared but has no executable handler.",
                remediation="Implement and validate a domain handler before requesting generated deliverables.",
                details={"qualified_workflow_id": workflow.qualified_id, "maturity": workflow.status},
            ).to_issue()
            result = {
                "run_id": run_id,
                "request_id": request["request_id"],
                "qualified_workflow_id": workflow.qualified_id,
                "status": "blocked",
                "summary": "The request was routed safely, but domain execution is not available.",
                "artifacts": [],
                "issues": [],
                "blockers": [blocker],
            }
            self.catalog.assert_valid(result, RESULT_SCHEMA_ID)
            return result

        try:
            upstream = tuple(
                store.get(reference["artifact_id"], reference["version"])
                for reference in request.get("upstream_artifacts", [])
            )
            context = ExecutionContext(run_id=run_id, upstream_artifacts=upstream)
            response = dict(handler(workflow, deepcopy(request), context))
            artifacts = list(response.get("artifacts", []))
            result = {
                "run_id": run_id,
                "request_id": request["request_id"],
                "qualified_workflow_id": workflow.qualified_id,
                "status": response.get("status", "complete"),
                "summary": response.get("summary", "Workflow handler completed."),
                "artifacts": artifacts,
                "issues": list(response.get("issues", [])),
                "blockers": list(response.get("blockers", [])),
            }
            self.catalog.assert_valid(result, RESULT_SCHEMA_ID)
            store.add_many([dict(artifact) for artifact in artifacts])
            return result
        except PlatformError:
            raise
        except Exception:
            issue = _execution_failure("The workflow handler failed without producing a valid result.")
            result = {
                "run_id": run_id,
                "request_id": request["request_id"],
                "qualified_workflow_id": workflow.qualified_id,
                "status": "failed",
                "summary": "Workflow execution failed safely.",
                "artifacts": [],
                "issues": [issue],
                "blockers": [],
            }
            self.catalog.assert_valid(result, RESULT_SCHEMA_ID)
            return result
