from __future__ import annotations

from copy import deepcopy

import pytest

from construction_ai_orchestrator.artifacts import ArtifactStore
from construction_ai_orchestrator.errors import ArtifactConflictError


def artifact() -> dict:
    return {
        "artifact_id": "ART-001",
        "project_id": "DEMO-001",
        "artifact_type": "scope_register",
        "schema_id": None,
        "schema_version": None,
        "version": "1.0.0",
        "status": "validated",
        "producer": {
            "agent_id": "tender-manager-agent",
            "workflow_id": "tender-package-ingestion",
            "run_id": "RUN-001",
        },
        "created_at": "2026-07-26T10:00:00Z",
        "lineage": [],
        "uri": None,
        "payload": {"scope": "Synthetic test scope"},
    }


def test_artifacts_are_stored_immutably(catalog):
    store = ArtifactStore(catalog)
    source = artifact()
    stored = store.add(source)
    source["payload"]["scope"] = "mutated"
    stored["payload"]["scope"] = "also mutated"
    assert store.get("ART-001", "1.0.0")["payload"]["scope"] == "Synthetic test scope"


def test_duplicate_identity_and_version_is_rejected(catalog):
    store = ArtifactStore(catalog)
    store.add(artifact())
    with pytest.raises(ArtifactConflictError):
        store.add(artifact())


def test_batch_registration_is_atomic(catalog):
    store = ArtifactStore(catalog)
    first = artifact()
    duplicate = deepcopy(first)
    with pytest.raises(ArtifactConflictError):
        store.add_many([first, duplicate])
    assert store.all() == []
