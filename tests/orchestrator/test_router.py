from __future__ import annotations

import pytest

from construction_ai_orchestrator.errors import AmbiguousWorkflowError, ContractValidationError
from construction_ai_orchestrator.router import WorkflowRouter


def test_routes_exact_agent_and_workflow(registry):
    workflow = WorkflowRouter(registry).route({"agent_id": "planning-p6-agent", "workflow_id": "wbs-development"})
    assert workflow.qualified_id == "planning-p6-agent/wbs-development"


def test_routes_specific_user_request(registry):
    workflow = WorkflowRouter(registry).route({"user_request": "Perform an RFP analysis"})
    assert workflow.qualified_id == "estimation-agent/rfp-analysis"


def test_ambiguous_text_request_is_rejected(registry):
    with pytest.raises(AmbiguousWorkflowError):
        WorkflowRouter(registry).route({"user_request": "Prepare the commercial proposal"})


def test_empty_selector_is_rejected(registry):
    with pytest.raises(ContractValidationError):
        WorkflowRouter(registry).route({})
