"""Typed, user-safe platform errors."""

from __future__ import annotations

from typing import Any


class PlatformError(Exception):
    code = "PLATFORM_ERROR"
    severity = "error"
    recoverable = False

    def __init__(
        self,
        message: str,
        *,
        path: str | None = None,
        remediation: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.path = path
        self.remediation = remediation
        self.details = details or {}

    def to_issue(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "recoverable": self.recoverable,
            "path": self.path,
            "remediation": self.remediation,
            "details": self.details,
        }


class ConfigurationError(PlatformError):
    code = "CONFIGURATION_ERROR"


class UnknownWorkflowError(PlatformError):
    code = "UNKNOWN_WORKFLOW"
    recoverable = True


class AmbiguousWorkflowError(PlatformError):
    code = "AMBIGUOUS_WORKFLOW"
    recoverable = True


class ContractValidationError(PlatformError):
    code = "CONTRACT_VALIDATION_ERROR"
    recoverable = True


class AdapterValidationError(PlatformError):
    code = "ADAPTER_VALIDATION_ERROR"
    recoverable = True


class ArtifactConflictError(PlatformError):
    code = "ARTIFACT_CONFLICT"


class UnknownArtifactError(PlatformError):
    code = "UNKNOWN_ARTIFACT"
    recoverable = True


class HandlerNotAvailableError(PlatformError):
    code = "HANDLER_NOT_AVAILABLE"
    severity = "blocker"
    recoverable = True
