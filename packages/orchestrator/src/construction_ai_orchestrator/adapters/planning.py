"""Planning & Primavera P6 Agent common-data adapter."""

from __future__ import annotations

from typing import Any

from .common import CommonAdapter

ARTIFACT_SCHEMA = "https://construction-ai-toolkit.dev/contracts/v1/core/artifact.schema.json"

SCHEDULE_STATUS = {
    "draft": "draft",
    "submitted": "in_review",
    "approved": "approved",
    "update": "generated",
    "forecast": "generated",
    "recovery": "generated",
    "scenario": "generated",
    "impacted": "generated",
    "superseded": "superseded",
}


class PlanningAdapter(CommonAdapter):
    agent_id = "planning-p6-agent"

    def adapt_source_document(self, value: dict[str, Any]) -> dict[str, Any]:
        return self._validate_source(self._base_source(value))

    def adapt_schedule_reference(
        self,
        value: dict[str, Any],
        *,
        workflow_id: str,
        run_id: str,
        created_at: str,
    ) -> dict[str, Any]:
        artifact = {
            "artifact_id": value.get("schedule_id"),
            "project_id": value.get("project_id"),
            "artifact_type": "schedule",
            "schema_id": None,
            "schema_version": None,
            "version": value.get("version"),
            "status": SCHEDULE_STATUS.get(value.get("status"), value.get("status")),
            "producer": {"agent_id": self.agent_id, "workflow_id": workflow_id, "run_id": run_id},
            "created_at": created_at,
            "lineage": [],
            "uri": value.get("artifact_reference"),
        }
        self.catalog.assert_valid(artifact, ARTIFACT_SCHEMA)
        return artifact
