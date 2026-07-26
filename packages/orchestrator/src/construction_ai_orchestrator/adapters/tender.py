"""Tender Manager Agent common-data adapter."""

from __future__ import annotations

import re
from typing import Any

from .common import CommonAdapter

ARTIFACT_SCHEMA = "https://construction-ai-toolkit.dev/contracts/v1/core/artifact.schema.json"

ARTIFACT_STATUS = {
    "draft": "draft",
    "in_review": "in_review",
    "approved": "approved",
    "conditionally_approved": "conditionally_approved",
    "rejected": "rejected",
    "superseded": "superseded",
}

REVIEW_STATUS = {
    "draft": "not_reviewed",
    "in_review": "in_review",
    "approved": "approved",
    "conditionally_approved": "conditionally_approved",
    "rejected": "rejected",
    "superseded": "revision_required",
}


class TenderAdapter(CommonAdapter):
    agent_id = "tender-manager-agent"

    def adapt_source_document(self, value: dict[str, Any]) -> dict[str, Any]:
        source = self._base_source(value)
        source["issue_date"] = value.get("issue_date")
        source["controlled_status"] = value.get("controlled_status")
        checksum = value.get("checksum")
        if checksum:
            source["checksum_value"] = checksum
            if re.fullmatch(r"[a-fA-F0-9]{64}", checksum):
                source["checksum_algorithm"] = "sha256"
                source["checksum_sha256"] = checksum
            else:
                source["checksum_algorithm"] = "unspecified"
        return self._validate_source(source)

    def adapt_tender_project(
        self,
        value: dict[str, Any],
        *,
        project_id: str,
        location: str,
        unit_system: str,
    ) -> dict[str, Any]:
        return self.adapt_project(
            {
                "project_id": project_id,
                "name": value.get("name"),
                "location": location,
                "currency": value.get("currency"),
                "unit_system": unit_system,
                "time_zone": value.get("time_zone"),
                "language": value.get("language"),
                "client": value.get("client"),
                "tender_id": value.get("tender_id"),
            }
        )

    def adapt_artifact_reference(
        self,
        value: dict[str, Any],
        *,
        project_id: str,
        run_id: str,
        created_at: str,
        artifact_type: str,
    ) -> dict[str, Any]:
        artifact = {
            "artifact_id": value.get("artifact_id"),
            "project_id": project_id,
            "artifact_type": artifact_type,
            "schema_id": None,
            "schema_version": None,
            "version": value.get("version"),
            "status": ARTIFACT_STATUS.get(value.get("approval_status"), value.get("approval_status")),
            "producer": {
                "agent_id": value.get("agent_id"),
                "workflow_id": value.get("workflow_id"),
                "run_id": run_id,
            },
            "created_at": created_at,
            "lineage": [],
            "uri": value.get("artifact_reference"),
        }
        if value.get("approved_by_role") or value.get("approved_at"):
            artifact["review"] = {
                "status": REVIEW_STATUS[value.get("approval_status")],
                "required_roles": [value["approved_by_role"]] if value.get("approved_by_role") else [],
                "reviewed_by": [value["approved_by_role"]] if value.get("approved_by_role") else [],
                "reviewed_at": value.get("approved_at"),
                "notes": None,
                "authorization_reference": None,
            }
        self.catalog.assert_valid(artifact, ARTIFACT_SCHEMA)
        return artifact
