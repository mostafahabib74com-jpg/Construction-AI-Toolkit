from __future__ import annotations

import json

from construction_ai_orchestrator.cli import main


def test_cli_inspect_reports_current_registry(repo_root, capsys):
    exit_code = main(["inspect", "--repo-root", str(repo_root)])
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert len(output["agents"]) == 3
    assert output["workflow_count"] == 44


def test_cli_route_returns_qualified_workflow(repo_root, capsys):
    exit_code = main([
        "route",
        "--repo-root",
        str(repo_root),
        "--agent",
        "planning-p6-agent",
        "--workflow",
        "wbs-development",
    ])
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["qualified_workflow_id"] == "planning-p6-agent/wbs-development"


def test_cli_ambiguous_route_returns_safe_error(repo_root, capsys):
    exit_code = main([
        "route",
        "--repo-root",
        str(repo_root),
        "--workflow",
        "commercial-proposal",
    ])
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["error"]["code"] == "AMBIGUOUS_WORKFLOW"
