"""Immutable orchestration definitions loaded from repository specifications."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class WorkflowDefinition:
    agent_id: str
    workflow_id: str
    title: str
    objective: str
    version: str
    status: str
    contract_path: Path
    input_schema_path: Path
    output_schema_path: Path
    prompt_path: Path
    required_inputs: tuple[str, ...]
    deliverables: tuple[str, ...]
    raw: dict[str, Any]

    @property
    def qualified_id(self) -> str:
        return f"{self.agent_id}/{self.workflow_id}"


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    agent_id: str
    name: str
    version: str
    status: str
    manifest_path: Path
    workflows: tuple[str, ...]
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    run_id: str
    upstream_artifacts: tuple[dict[str, Any], ...]
