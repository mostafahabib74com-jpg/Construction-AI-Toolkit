# Central Orchestrator

The orchestrator is the platform control plane for the three implemented agent specifications. It discovers existing workflow contracts, routes qualified requests, validates canonical envelopes, records immutable artifacts, passes artifact references between runs, and returns a consolidated result.

It does not execute construction-domain work by itself. A workflow without a registered handler returns a visible `HANDLER_NOT_AVAILABLE` blocker.

## Release accuracy safeguards

Artifacts marked `validated`, `conditionally_approved`, or `approved` must identify a local canonical schema and version and provide a schema-valid payload. The orchestrator then applies the relevant quantity, BOQ/rate, contract, schedule, or deliverable policy. Blocking findings prevent the artifact from entering the registry. Only professionally reviewed artifacts with `approved` status appear as final deliverables.

Common-data adapters are available for Estimation, Planning & P6, and Tender Manager sources, projects, reviews, quantities, schedule references, and tender artifact references. They require explicit context where legacy data is incomplete.

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
