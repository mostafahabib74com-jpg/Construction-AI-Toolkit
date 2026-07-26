# Central Orchestrator

The orchestrator is the platform control plane for the three implemented agent specifications. It discovers existing workflow contracts, routes qualified requests, validates canonical envelopes, records immutable artifacts, passes artifact references between runs, and returns a consolidated result.

It does not execute construction-domain work by itself. A workflow without a registered handler returns a visible `HANDLER_NOT_AVAILABLE` blocker.

## Install and test

```powershell
python -m pip install -e "packages/orchestrator[test]"
python -m pytest
```

## Inspect and route

```powershell
construction-ai inspect --repo-root .
construction-ai route --repo-root . --request "Analyze this RFP package"
construction-ai route --repo-root . --agent planning-p6-agent --workflow wbs-development
```

Workflow runtime keys use `<agent-id>/<workflow-id>`. An unqualified ID that exists in multiple agents is rejected as ambiguous.
