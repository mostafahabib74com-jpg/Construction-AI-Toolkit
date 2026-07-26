"""Discovery and validation of existing agent/workflow specifications."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from .errors import AmbiguousWorkflowError, ConfigurationError, UnknownWorkflowError
from .models import AgentDefinition, WorkflowDefinition


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(
            f"Unable to load YAML configuration: {path}",
            path=str(path),
            remediation="Correct the file path or YAML syntax.",
        ) from exc
    if not isinstance(value, dict):
        raise ConfigurationError(f"Expected a YAML object in {path}", path=str(path))
    return value


class AgentRegistry:
    """An immutable index of the agents and workflows declared in the repository."""

    def __init__(
        self,
        *,
        repo_root: Path,
        agents: dict[str, AgentDefinition],
        workflows: dict[str, WorkflowDefinition],
    ) -> None:
        self.repo_root = repo_root
        self._agents = dict(agents)
        self._workflows = dict(workflows)
        by_short: dict[str, list[str]] = defaultdict(list)
        for qualified_id, workflow in self._workflows.items():
            by_short[workflow.workflow_id].append(qualified_id)
        self._by_short = {key: tuple(sorted(values)) for key, values in by_short.items()}

    @classmethod
    def from_file(cls, repo_root: str | Path, config_path: str | Path) -> "AgentRegistry":
        root = Path(repo_root).resolve()
        config = Path(config_path)
        if not config.is_absolute():
            config = root / config
        registry_data = _read_yaml(config.resolve())
        entries = registry_data.get("agents")
        if not isinstance(entries, list) or not entries:
            raise ConfigurationError("Agent registry must contain a non-empty 'agents' list.", path=str(config))

        agents: dict[str, AgentDefinition] = {}
        workflows: dict[str, WorkflowDefinition] = {}
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not isinstance(entry.get("manifest"), str):
                raise ConfigurationError("Each registry agent requires string 'id' and 'manifest' fields.", path=str(config))
            declared_id = entry["id"]
            manifest_path = (root / entry["manifest"]).resolve()
            manifest_data = _read_yaml(manifest_path)
            agent_data = manifest_data.get("agent")
            if not isinstance(agent_data, dict):
                raise ConfigurationError("Agent manifest is missing the 'agent' object.", path=str(manifest_path))
            manifest_id = agent_data.get("id")
            if manifest_id != declared_id:
                raise ConfigurationError(
                    f"Registry ID '{declared_id}' does not match manifest ID '{manifest_id}'.",
                    path=str(manifest_path),
                )
            if declared_id in agents:
                raise ConfigurationError(f"Duplicate agent ID: {declared_id}", path=str(config))
            supported = agent_data.get("supported_workflows")
            if not isinstance(supported, list) or not all(isinstance(value, str) for value in supported):
                raise ConfigurationError("Agent manifest requires a string supported_workflows list.", path=str(manifest_path))

            workflow_ids: list[str] = []
            agent_root = manifest_path.parent
            for workflow_id in supported:
                contract_path = (agent_root / "workflows" / workflow_id / "workflow.yaml").resolve()
                workflow_data = _read_yaml(contract_path).get("workflow")
                if not isinstance(workflow_data, dict):
                    raise ConfigurationError("Workflow contract is missing the 'workflow' object.", path=str(contract_path))
                if workflow_data.get("id") != workflow_id:
                    raise ConfigurationError(
                        f"Manifest workflow ID '{workflow_id}' does not match its contract.",
                        path=str(contract_path),
                    )
                input_path = contract_path.parent / "input.schema.json"
                output_path = contract_path.parent / "output.schema.json"
                prompt_ref = workflow_data.get("prompt")
                if not isinstance(prompt_ref, str):
                    raise ConfigurationError("Workflow contract requires a prompt path.", path=str(contract_path))
                prompt_path = (contract_path.parent / prompt_ref).resolve()
                for required_path in (input_path, output_path, prompt_path):
                    if not required_path.is_file():
                        raise ConfigurationError("Workflow dependency does not exist.", path=str(required_path))
                definition = WorkflowDefinition(
                    agent_id=declared_id,
                    workflow_id=workflow_id,
                    title=str(workflow_data.get("title", workflow_id)),
                    objective=str(workflow_data.get("objective", "")),
                    version=str(workflow_data.get("version", "")),
                    status=str(workflow_data.get("status", "unknown")),
                    contract_path=contract_path,
                    input_schema_path=input_path.resolve(),
                    output_schema_path=output_path.resolve(),
                    prompt_path=prompt_path,
                    required_inputs=tuple(workflow_data.get("required_inputs") or ()),
                    deliverables=tuple(workflow_data.get("deliverables") or ()),
                    raw=workflow_data,
                )
                if definition.qualified_id in workflows:
                    raise ConfigurationError(f"Duplicate qualified workflow ID: {definition.qualified_id}")
                workflows[definition.qualified_id] = definition
                workflow_ids.append(workflow_id)

            agents[declared_id] = AgentDefinition(
                agent_id=declared_id,
                name=str(agent_data.get("name", declared_id)),
                version=str(agent_data.get("version", "")),
                status=str(agent_data.get("status", "unknown")),
                manifest_path=manifest_path,
                workflows=tuple(workflow_ids),
                raw=agent_data,
            )

        return cls(repo_root=root, agents=agents, workflows=workflows)

    @property
    def agents(self) -> tuple[AgentDefinition, ...]:
        return tuple(self._agents[key] for key in sorted(self._agents))

    @property
    def workflows(self) -> tuple[WorkflowDefinition, ...]:
        return tuple(self._workflows[key] for key in sorted(self._workflows))

    @property
    def collisions(self) -> dict[str, tuple[str, ...]]:
        return {key: values for key, values in self._by_short.items() if len(values) > 1}

    def resolve(self, workflow_id: str, agent_id: str | None = None) -> WorkflowDefinition:
        if "/" in workflow_id:
            qualified_id = workflow_id
            if agent_id and not qualified_id.startswith(f"{agent_id}/"):
                raise UnknownWorkflowError(
                    "The agent ID conflicts with the qualified workflow ID.",
                    remediation="Use one matching qualified workflow ID.",
                )
            workflow = self._workflows.get(qualified_id)
            if workflow is None:
                raise UnknownWorkflowError(
                    f"Unknown workflow: {qualified_id}",
                    remediation="Inspect the registry and select a declared qualified workflow ID.",
                )
            return workflow

        if agent_id:
            qualified_id = f"{agent_id}/{workflow_id}"
            workflow = self._workflows.get(qualified_id)
            if workflow is None:
                raise UnknownWorkflowError(
                    f"Unknown workflow: {qualified_id}",
                    remediation="Inspect the selected agent's supported workflows.",
                )
            return workflow

        matches = self._by_short.get(workflow_id, ())
        if not matches:
            raise UnknownWorkflowError(
                f"Unknown workflow: {workflow_id}",
                remediation="Provide a declared workflow ID or a user request to route.",
            )
        if len(matches) > 1:
            raise AmbiguousWorkflowError(
                f"Workflow ID '{workflow_id}' exists in more than one agent.",
                remediation="Use a qualified '<agent-id>/<workflow-id>' value.",
                details={"candidates": list(matches)},
            )
        return self._workflows[matches[0]]

    def search(self, user_request: str, agent_id: str | None = None) -> WorkflowDefinition:
        query = user_request.strip().lower()
        if not query:
            raise UnknownWorkflowError("User request is empty.", remediation="Describe the required task.")
        candidates = [workflow for workflow in self.workflows if not agent_id or workflow.agent_id == agent_id]
        if agent_id and agent_id not in self._agents:
            raise UnknownWorkflowError(f"Unknown agent: {agent_id}", remediation="Inspect the agent registry.")

        phrase_matches = [
            workflow
            for workflow in candidates
            if workflow.workflow_id.replace("-", " ") in query
        ]
        if len(phrase_matches) == 1:
            return phrase_matches[0]
        if len(phrase_matches) > 1:
            raise AmbiguousWorkflowError(
                "The user request names a workflow that exists in multiple agents.",
                remediation="Specify the target agent and workflow.",
                details={"candidates": sorted(workflow.qualified_id for workflow in phrase_matches)},
            )

        query_tokens = set(re.findall(r"[a-z0-9]+", query))
        scored: list[tuple[int, str, WorkflowDefinition]] = []
        for workflow in candidates:
            workflow_phrase = workflow.workflow_id.replace("-", " ")
            haystack = f"{workflow_phrase} {workflow.title} {workflow.objective}".lower()
            haystack_tokens = set(re.findall(r"[a-z0-9]+", haystack))
            score = len(query_tokens & haystack_tokens)
            if workflow_phrase in query:
                score += 20
            if workflow.title.lower() in query:
                score += 10
            if score:
                scored.append((score, workflow.qualified_id, workflow))
        if not scored:
            raise UnknownWorkflowError(
                "No workflow matches the user request.",
                remediation="Provide an agent ID and workflow ID, or use more specific task wording.",
            )
        scored.sort(key=lambda item: (-item[0], item[1]))
        best_score = scored[0][0]
        best = [item[2] for item in scored if item[0] == best_score]
        if len(best) > 1:
            raise AmbiguousWorkflowError(
                "The user request matches multiple workflows equally.",
                remediation="Specify the target agent and workflow.",
                details={"candidates": [workflow.qualified_id for workflow in best]},
            )
        return best[0]
