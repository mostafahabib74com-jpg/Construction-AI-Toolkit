"""Shared adapter behavior with no silent business defaults."""

from __future__ import annotations

from typing import Any

from ..errors import AdapterValidationError
from ..validation import SchemaCatalog

PROJECT_SCHEMA = "https://construction-ai-toolkit.dev/contracts/v1/core/project.schema.json"
REVIEW_SCHEMA = "https://construction-ai-toolkit.dev/contracts/v1/core/review.schema.json"
SOURCE_SCHEMA = "https://construction-ai-toolkit.dev/contracts/v1/core/source-document.schema.json"

REVIEW_STATUS = {
    "not_started": "not_reviewed",
    "in_review": "in_review",
    "approved": "approved",
    "rejected": "rejected",
    "revision_required": "revision_required",
}


class CommonAdapter:
    agent_id: str

    def __init__(self, catalog: SchemaCatalog) -> None:
        self.catalog = catalog

    def adapt_project(
        self,
        value: dict[str, Any],
        *,
        time_zone: str | None = None,
        unit_system: str | None = None,
    ) -> dict[str, Any]:
        resolved_time_zone = time_zone or value.get("time_zone")
        if not resolved_time_zone:
            raise AdapterValidationError(
                "Project time zone is required and cannot be inferred safely.",
                path="$.project.time_zone",
                remediation="Provide an explicit IANA time zone such as 'Asia/Riyadh'.",
                details={"agent_id": self.agent_id},
            )
        project = {
            "project_id": value.get("project_id"),
            "name": value.get("name"),
            "location": value.get("location"),
            "currency": value.get("currency"),
            "unit_system": unit_system or value.get("unit_system"),
            "time_zone": resolved_time_zone,
            "client": value.get("client"),
            "tender_id": value.get("tender_id"),
        }
        if value.get("language") is not None:
            project["language"] = value["language"]
        self.catalog.assert_valid(project, PROJECT_SCHEMA)
        return project

    def adapt_review(self, value: dict[str, Any]) -> dict[str, Any]:
        legacy_status = value.get("status")
        if legacy_status not in REVIEW_STATUS:
            raise AdapterValidationError(
                f"Unsupported review status: {legacy_status}",
                path="$.review.status",
                remediation="Map the legacy status explicitly before adaptation.",
                details={"agent_id": self.agent_id},
            )
        comments = value.get("comments") or []
        review = {
            "status": REVIEW_STATUS[legacy_status],
            "required_roles": list(value.get("required_roles") or []),
            "reviewed_by": list(value.get("reviewed_by") or []),
            "reviewed_at": value.get("reviewed_at"),
            "notes": "\n".join(str(comment) for comment in comments) or None,
            "authorization_reference": value.get("authorization_reference"),
        }
        self.catalog.assert_valid(review, REVIEW_SCHEMA)
        return review

    def _validate_source(self, source: dict[str, Any]) -> dict[str, Any]:
        self.catalog.assert_valid(source, SOURCE_SCHEMA)
        return source

    @staticmethod
    def _base_source(value: dict[str, Any]) -> dict[str, Any]:
        return {
            "document_id": value.get("source_id"),
            "title": value.get("title"),
            "revision": value.get("revision"),
            "issue_date": None,
            "controlled_status": "unverified",
            "document_number": value.get("document_number"),
            "file_name": None,
            "media_type": None,
            "checksum_sha256": None,
            "checksum_algorithm": None,
            "checksum_value": None,
            "uri": value.get("location"),
            "classification": value.get("classification"),
            "extraction_method": value.get("extraction_method"),
            "confidence": value.get("confidence"),
            "addendum_id": value.get("addendum_id"),
            "supersedes_document_id": value.get("supersedes_source_id"),
        }
