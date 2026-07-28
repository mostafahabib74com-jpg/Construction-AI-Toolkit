"""Immutable artifact registration for cross-agent handoff."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .errors import ArtifactConflictError, UnknownArtifactError
from .validation import SchemaCatalog

ARTIFACT_SCHEMA_ID = "https://construction-ai-toolkit.dev/contracts/v1/core/artifact.schema.json"


class ArtifactStore:
    def __init__(self, catalog: SchemaCatalog) -> None:
        self._catalog = catalog
        self._artifacts: dict[tuple[str, str], dict[str, Any]] = {}

    def add(self, artifact: dict[str, Any]) -> dict[str, Any]:
        return self.add_many([artifact])[0]

    def add_many(self, artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        pending: dict[tuple[str, str], dict[str, Any]] = {}
        for artifact in artifacts:
            self._catalog.assert_valid(artifact, ARTIFACT_SCHEMA_ID)
            key = (artifact["artifact_id"], artifact["version"])
            if key in self._artifacts or key in pending:
                raise ArtifactConflictError(
                    f"Artifact {key[0]} version {key[1]} is already registered.",
                    remediation="Create a new artifact version; registered versions are immutable.",
                    details={"artifact_id": key[0], "version": key[1]},
                )
            pending[key] = deepcopy(artifact)
        self._artifacts.update(pending)
        return [deepcopy(pending[key]) for key in pending]

    def get(self, artifact_id: str, version: str) -> dict[str, Any]:
        key = (artifact_id, version)
        if key not in self._artifacts:
            raise UnknownArtifactError(
                f"Artifact {artifact_id} version {version} is not registered.",
                remediation="Use an artifact reference returned by the orchestrator.",
            )
        return deepcopy(self._artifacts[key])

    def all(self) -> list[dict[str, Any]]:
        return [deepcopy(self._artifacts[key]) for key in sorted(self._artifacts)]

    def references(self) -> list[dict[str, str]]:
        return [
            {"artifact_id": artifact_id, "version": version}
            for artifact_id, version in sorted(self._artifacts)
        ]
