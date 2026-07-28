"""Rules that prevent unsupported or misleading rates and BOQ prices."""

from __future__ import annotations

from typing import Any

from .common import policy_issue
from .quantity import validate_quantity


def validate_rate(value: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    amount = value.get("value", {}).get("amount")
    source_status = value.get("source_status")
    source_reference = value.get("source_reference")
    if isinstance(amount, (int, float)) and amount < 0:
        issues.append(policy_issue(
            "RATE_NEGATIVE",
            "A rate cannot be negative.",
            path="$.value.amount",
            remediation="Correct the rate or represent credits separately with an approved basis.",
        ))
    if amount == 0 and not value.get("zero_cost_justification"):
        issues.append(policy_issue(
            "RATE_ZERO_UNJUSTIFIED",
            "A zero rate requires an explicit zero-cost justification.",
            path="$.zero_cost_justification",
            remediation="State why the item is included elsewhere, free-issued, or genuinely zero cost.",
        ))
    if source_status in {"quoted", "historical"} and not source_reference:
        issues.append(policy_issue(
            "RATE_SOURCE_MISSING",
            f"A {source_status} rate requires a source reference.",
            path="$.source_reference",
            remediation="Link the quotation or historical rate source.",
        ))
    if source_status == "unverified":
        issues.append(policy_issue(
            "RATE_UNVERIFIED",
            "An unverified rate cannot be released as validated pricing.",
            path="$.source_status",
            remediation="Verify the rate or retain the artifact in draft status.",
        ))
    return issues


def validate_boq_item(value: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for issue in validate_quantity(value["quantity"]):
        nested = dict(issue)
        nested["path"] = issue["path"].replace("$", "$.quantity", 1)
        issues.append(nested)
    status = value.get("status")
    if status in {"priced", "validated", "approved"}:
        if not value.get("rate_id"):
            issues.append(policy_issue(
                "BOQ_RATE_MISSING",
                "A priced BOQ item requires a rate reference.",
                path="$.rate_id",
                remediation="Link an approved rate or mark the item unpriced.",
            ))
        if value.get("total") is None:
            issues.append(policy_issue(
                "BOQ_TOTAL_MISSING",
                "A priced BOQ item requires a calculated total.",
                path="$.total",
                remediation="Calculate the total deterministically from quantity and rate.",
            ))
    if status == "unpriced" and value.get("total") is not None:
        issues.append(policy_issue(
            "UNPRICED_BOQ_HAS_TOTAL",
            "An unpriced BOQ item must not carry a commercial total.",
            path="$.total",
            remediation="Remove the total or complete and validate the rate build-up.",
        ))
    total = value.get("total")
    if isinstance(total, dict) and total.get("amount", 0) < 0:
        issues.append(policy_issue(
            "BOQ_TOTAL_NEGATIVE",
            "A BOQ item total cannot be negative.",
            path="$.total.amount",
            remediation="Correct the calculation or represent credits separately.",
        ))
    return issues
