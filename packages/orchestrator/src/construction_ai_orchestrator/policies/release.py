"""Mandatory-field and approval checks for controlled deliverables."""

from __future__ import annotations

from typing import Any

from .common import policy_issue


def validate_deliverable(value: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    status = value.get("status")
    if status not in {"validated", "approved", "submitted"}:
        return issues
    fields = value.get("field_values") or {}
    missing = set(value.get("missing_fields") or [])
    for field in value.get("mandatory_fields") or []:
        field_value = fields.get(field)
        if field not in fields or field_value is None or (isinstance(field_value, str) and not field_value.strip()):
            missing.add(field)
    if missing:
        issues.append(policy_issue(
            "DELIVERABLE_MANDATORY_FIELDS_MISSING",
            "A controlled deliverable has missing mandatory fields.",
            path="$.missing_fields",
            remediation="Complete every mandatory field before release.",
            details={"missing_fields": sorted(missing)},
        ))
    if value.get("artifact_reference") is None:
        issues.append(policy_issue(
            "DELIVERABLE_ARTIFACT_MISSING",
            "A validated or released deliverable requires an artifact reference.",
            path="$.artifact_reference",
            remediation="Generate, register, and reference the controlled artifact.",
        ))
    if status in {"approved", "submitted"}:
        review = value.get("review") or {}
        if review.get("status") != "approved":
            issues.append(policy_issue(
                "DELIVERABLE_APPROVAL_MISSING",
                "An approved/submitted deliverable requires an approved review record.",
                path="$.review.status",
                remediation="Obtain and record the required professional approval.",
            ))
    return issues
