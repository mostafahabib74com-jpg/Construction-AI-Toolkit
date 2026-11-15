"""Deterministic workflow selection."""

from __future__ import annotations

from typing import Any

from .errors import ContractValidationError
from .models import WorkflowDefinition
from .registry import AgentRegistry


class WorkflowRouter:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def route(self, selector: dict[str, Any]) -> WorkflowDefinition:
        if not isinstance(selector, dict):
            raise ContractValidationError("Workflow selector must be an object.", path="$.selector")
        agent_id = selector.get("agent_id")
        workflow_id = selector.get("workflow_id")
        user_request = selector.get("user_request")
        if workflow_id:
            return self.registry.resolve(str(workflow_id), str(agent_id) if agent_id else None)
        if user_request:
            return self.registry.search(str(user_request), str(agent_id) if agent_id else None)
        raise ContractValidationError(
            "Workflow selector requires workflow_id or user_request.",
            path="$.selector",
            remediation="Provide a qualified workflow ID or describe the requested task.",
        )
