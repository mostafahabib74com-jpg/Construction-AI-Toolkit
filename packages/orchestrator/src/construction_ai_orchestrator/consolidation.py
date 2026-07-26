"""Creation of canonical final orchestration results."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from .artifacts import ArtifactStore
from .validation import SchemaCatalog

CONSOLIDATED_SCHEMA_ID = "https://construction-ai-toolkit.dev/contracts/v1/core/consolidated-result.schema.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def consolidate(
    *,
    request_id: str,
    runs: list[dict[str, Any]],
    artifact_store: ArtifactStore,
    catalog: SchemaCatalog,
    extra_issues: list[dict[str, Any]] | None = None,
    extra_blockers: list[dict[str, Any]] | None = None,
    clock: Callable[[], str] = utc_now,
) -> dict[str, Any]:
    issues = [issue for run in runs for issue in run["issues"]] + list(extra_issues or [])
    blockers = [issue for run in runs for issue in run["blockers"]] + list(extra_blockers or [])
    statuses = {run["status"] for run in runs}
    if "failed" in statuses:
        status = "failed"
    elif blockers or "blocked" in statuses:
        status = "blocked" if not ("complete" in statuses) else "partial"
    elif "requires_review" in statuses:
        status = "requires_review"
    elif runs and statuses == {"complete"}:
        status = "complete"
    else:
        status = "failed"

    artifacts = artifact_store.all()
    final_deliverables = [
        {"artifact_id": artifact["artifact_id"], "version": artifact["version"]}
        for artifact in artifacts
        if artifact["status"] in {"validated", "approved"}
    ]
    result = {
        "request_id": request_id,
        "status": status,
        "workflow_runs": runs,
        "artifact_manifest": artifacts,
        "issues": issues,
        "blockers": blockers,
        "final_deliverables": final_deliverables,
        "created_at": clock(),
    }
    catalog.assert_valid(result, CONSOLIDATED_SCHEMA_ID)
    return result
