from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from construction_ai_orchestrator.registry import AgentRegistry
from construction_ai_orchestrator.validation import SchemaCatalog

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def catalog(repo_root: Path) -> SchemaCatalog:
    return SchemaCatalog.from_directory(repo_root / "packages/contracts/schemas")


@pytest.fixture(scope="session")
def registry(repo_root: Path) -> AgentRegistry:
    return AgentRegistry.from_file(repo_root, "packages/orchestrator/config/agent-registry.yaml")


@pytest.fixture()
def project() -> dict:
    return {
        "project_id": "DEMO-001",
        "name": "Critical Integration Test",
        "location": "Riyadh, Saudi Arabia",
        "currency": "SAR",
        "unit_system": "SI",
        "time_zone": "Asia/Riyadh",
        "language": "en",
        "client": None,
        "tender_id": "TND-001",
    }


@pytest.fixture()
def request_factory(project: dict):
    def create(*, request_id: str = "REQ-001", agent_id: str | None = None, workflow_id: str | None = None, user_request: str | None = None) -> dict:
        selector = {
            key: value
            for key, value in {
                "agent_id": agent_id,
                "workflow_id": workflow_id,
                "user_request": user_request,
            }.items()
            if value is not None
        }
        return {
            "request_id": request_id,
            "project": deepcopy(project),
            "selector": selector,
            "inputs": {},
            "upstream_artifacts": [],
            "requested_formats": ["json"],
        }

    return create
