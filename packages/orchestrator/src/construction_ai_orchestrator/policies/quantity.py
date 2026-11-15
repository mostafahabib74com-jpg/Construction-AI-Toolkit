"""Rules that prevent invented or misleading quantities."""

from __future__ import annotations

from typing import Any

from .common import policy_issue


def validate_quantity(value: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    quantity = value.get("value")
    status = value.get("status")
    basis = value.get("measurement_basis")
    sources = value.get("source_ids") or []

    if isinstance(quantity, (int, float)) and quantity < 0:
        issues.append(policy_issue(
            "QUANTITY_NEGATIVE",
            "Quantity cannot be negative.",
            path="$.value",
            remediation="Correct the measurement or represent the adjustment separately.",
        ))
    if status == "confirmed":
        if quantity is None:
            issues.append(policy_issue(
                "QUANTITY_VALUE_MISSING",
                "A confirmed quantity requires a numeric value.",
                path="$.value",
                remediation="Provide a measured/calculated value or mark the quantity unknown.",
            ))
        if not isinstance(basis, str) or not basis.strip():
            issues.append(policy_issue(
                "QUANTITY_BASIS_MISSING",
                "A confirmed quantity requires a measurement basis.",
                path="$.measurement_basis",
                remediation="Record the measurement method or source basis.",
            ))
        if not sources:
            issues.append(policy_issue(
                "QUANTITY_SOURCE_MISSING",
                "A confirmed quantity requires at least one source reference.",
                path="$.source_ids",
                remediation="Add controlled evidence or change the status to allowance/unknown.",
            ))
    elif status == "allowance":
        if quantity is None:
            issues.append(policy_issue(
                "ALLOWANCE_VALUE_MISSING",
                "An allowance requires an explicit value.",
                path="$.value",
                remediation="Provide the approved allowance value or mark it unknown.",
            ))
        if not value.get("assumption_id"):
            issues.append(policy_issue(
                "ALLOWANCE_ASSUMPTION_MISSING",
                "An allowance requires a linked assumption.",
                path="$.assumption_id",
                remediation="Create and reference a controlled assumption.",
            ))
    elif status in {"unknown", "not_applicable"} and quantity is not None:
        issues.append(policy_issue(
            "NON_NUMERIC_STATUS_HAS_VALUE",
            f"A quantity with status '{status}' must not carry a numeric value.",
            path="$.value",
            remediation="Remove the value or choose the correct controlled status.",
        ))
    return issues
