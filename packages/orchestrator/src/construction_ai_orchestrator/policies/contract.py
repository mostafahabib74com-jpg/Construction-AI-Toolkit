"""Rules that distinguish sourced contract facts from assumptions."""

from __future__ import annotations

from typing import Any

from .common import policy_issue


def validate_contract_requirement(value: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    basis = value.get("basis")
    evidence = value.get("evidence_ids") or []
    assumption_id = value.get("assumption_id")
    status = value.get("status")
    if basis == "source_fact" and not evidence:
        issues.append(policy_issue(
            "CONTRACT_EVIDENCE_MISSING",
            "A contract fact requires controlled evidence.",
            path="$.evidence_ids",
            remediation="Add a source citation or relabel the statement as an assumption/inference.",
        ))
    if basis in {"assumption", "inference"}:
        if not assumption_id:
            issues.append(policy_issue(
                "CONTRACT_ASSUMPTION_LINK_MISSING",
                "An assumed or inferred requirement requires a linked assumption.",
                path="$.assumption_id",
                remediation="Create and reference a visible assumption record.",
            ))
        if status == "confirmed":
            issues.append(policy_issue(
                "INFERRED_CONTRACT_REQUIREMENT_CONFIRMED",
                "An assumption or inference cannot be presented as a confirmed contract fact.",
                path="$.status",
                remediation="Keep the status proposed/draft until supported by controlled evidence.",
            ))
    return issues
