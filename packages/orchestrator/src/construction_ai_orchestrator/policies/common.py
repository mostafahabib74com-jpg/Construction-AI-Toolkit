"""Common policy issue and report types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def policy_issue(
    code: str,
    message: str,
    *,
    path: str,
    remediation: str,
    severity: str = "blocker",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "severity": severity,
        "recoverable": True,
        "path": path,
        "remediation": remediation,
        "details": details or {},
    }


@dataclass(frozen=True, slots=True)
class PolicyReport:
    issues: tuple[dict[str, Any], ...] = ()

    @property
    def blockers(self) -> tuple[dict[str, Any], ...]:
        return tuple(issue for issue in self.issues if issue["severity"] == "blocker")

    @property
    def warnings(self) -> tuple[dict[str, Any], ...]:
        return tuple(issue for issue in self.issues if issue["severity"] == "warning")
