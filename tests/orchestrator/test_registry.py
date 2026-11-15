from __future__ import annotations

import pytest

from construction_ai_orchestrator.errors import AmbiguousWorkflowError, UnknownWorkflowError


def test_registry_discovers_three_agents_and_all_workflows(registry):
    assert len(registry.agents) == 3
    assert len(registry.workflows) == 44


def test_registry_reports_known_short_id_collisions(registry):
    assert registry.collisions == {
        "commercial-proposal": (
            "estimation-agent/commercial-proposal",
            "tender-manager-agent/commercial-proposal",
        ),
        "rfi-generation": (
            "estimation-agent/rfi-generation",
            "tender-manager-agent/rfi-generation",
        ),
        "technical-proposal": (
            "estimation-agent/technical-proposal",
            "tender-manager-agent/technical-proposal",
        ),
    }


def test_qualified_workflow_resolves_deterministically(registry):
    workflow = registry.resolve("estimation-agent/rfi-generation")
    assert workflow.agent_id == "estimation-agent"
    assert workflow.workflow_id == "rfi-generation"


def test_unqualified_collision_is_rejected(registry):
    with pytest.raises(AmbiguousWorkflowError) as caught:
        registry.resolve("rfi-generation")
    assert caught.value.details["candidates"] == [
        "estimation-agent/rfi-generation",
        "tender-manager-agent/rfi-generation",
    ]


def test_unknown_workflow_is_typed(registry):
    with pytest.raises(UnknownWorkflowError) as caught:
        registry.resolve("not-a-workflow")
    assert caught.value.code == "UNKNOWN_WORKFLOW"


def test_every_workflow_dependency_exists(registry):
    for workflow in registry.workflows:
        assert workflow.contract_path.is_file()
        assert workflow.input_schema_path.is_file()
        assert workflow.output_schema_path.is_file()
        assert workflow.prompt_path.is_file()
