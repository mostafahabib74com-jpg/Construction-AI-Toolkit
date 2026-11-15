"""Command-line entrypoint for registry inspection and safe routing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .errors import PlatformError
from .registry import AgentRegistry
from .router import WorkflowRouter
from .runner import Orchestrator
from .validation import SchemaCatalog

REGISTRY_PATH = Path("packages/orchestrator/config/agent-registry.yaml")
SCHEMA_PATH = Path("packages/contracts/schemas")


def _components(repo_root: Path) -> tuple[AgentRegistry, SchemaCatalog]:
    registry = AgentRegistry.from_file(repo_root, REGISTRY_PATH)
    catalog = SchemaCatalog.from_directory(repo_root / SCHEMA_PATH)
    return registry, catalog


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="construction-ai")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect", help="Show registered agents and workflows.")
    inspect_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    route_parser = subparsers.add_parser("route", help="Resolve a request to one workflow.")
    route_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    route_parser.add_argument("--request")
    route_parser.add_argument("--agent")
    route_parser.add_argument("--workflow")
    run_parser = subparsers.add_parser("run", help="Validate and route a canonical request JSON file.")
    run_parser.add_argument("request_file", type=Path)
    run_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        registry, catalog = _components(args.repo_root.resolve())
        catalog.check_all_schemas()
        if args.command == "inspect":
            output = {
                "agents": [{"agent_id": item.agent_id, "name": item.name, "status": item.status} for item in registry.agents],
                "workflow_count": len(registry.workflows),
                "colliding_short_ids": registry.collisions,
            }
        elif args.command == "route":
            selector = {key: value for key, value in {"agent_id": args.agent, "workflow_id": args.workflow, "user_request": args.request}.items() if value}
            workflow = WorkflowRouter(registry).route(selector)
            output = {
                "qualified_workflow_id": workflow.qualified_id,
                "title": workflow.title,
                "status": workflow.status,
                "contract": str(workflow.contract_path.relative_to(args.repo_root.resolve())),
            }
        else:
            request = json.loads(args.request_file.read_text(encoding="utf-8"))
            output = Orchestrator(registry=registry, catalog=catalog).run(request)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, PlatformError) as exc:
        issue = exc.to_issue() if isinstance(exc, PlatformError) else {
            "code": "INPUT_FILE_ERROR",
            "message": "Unable to read the request file.",
            "severity": "error",
            "recoverable": True,
            "path": None,
            "remediation": "Provide a readable JSON request file.",
            "details": {},
        }
        print(json.dumps({"error": issue}, indent=2, sort_keys=True))
        return 2
