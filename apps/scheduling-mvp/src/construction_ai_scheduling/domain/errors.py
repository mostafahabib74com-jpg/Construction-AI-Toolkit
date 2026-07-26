"""Typed application errors that can be rendered safely in the user interface."""

from __future__ import annotations

from collections.abc import Sequence

from .models import ValidationIssue


class InputValidationError(ValueError):
    """Raised when user-entered data cannot be accepted."""

    def __init__(self, message: str, issues: Sequence[ValidationIssue]) -> None:
        super().__init__(message)
        self.issues = tuple(issues)


class BOQImportError(ValueError):
    """Raised when an uploaded BOQ file cannot be read safely."""
