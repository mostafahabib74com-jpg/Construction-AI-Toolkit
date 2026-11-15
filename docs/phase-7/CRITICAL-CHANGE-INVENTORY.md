# Critical implementation change inventory

## Scope

This inventory covers the critical Phase 7 control-plane implementation. Existing agent content was preserved.

## Files created

### Repository support

- `.gitignore`

### Classification and reporting

- `docs/phase-7/FINDING-CLASSIFICATION.md`
- `docs/phase-7/CORRECTIVE-ACTION-PLAN.md`
- `docs/phase-7/CRITICAL-TEST-RESULTS.md`
- `docs/phase-7/CRITICAL-CHANGE-INVENTORY.md`

### Shared contracts

- `packages/contracts/README.md`
- `packages/contracts/schemas/catalog.json`
- `packages/contracts/schemas/core/artifact.schema.json`
- `packages/contracts/schemas/core/consolidated-result.schema.json`
- `packages/contracts/schemas/core/error.schema.json`
- `packages/contracts/schemas/core/evidence.schema.json`
- `packages/contracts/schemas/core/money.schema.json`
- `packages/contracts/schemas/core/project.schema.json`
- `packages/contracts/schemas/core/quantity.schema.json`
- `packages/contracts/schemas/core/review.schema.json`
- `packages/contracts/schemas/core/source-document.schema.json`
- `packages/contracts/schemas/core/unit.schema.json`
- `packages/contracts/schemas/core/workflow-request.schema.json`
- `packages/contracts/schemas/core/workflow-result.schema.json`
- `packages/contracts/schemas/domain/activity.schema.json`
- `packages/contracts/schemas/domain/assumption.schema.json`
- `packages/contracts/schemas/domain/boq-item.schema.json`
- `packages/contracts/schemas/domain/deliverable.schema.json`
- `packages/contracts/schemas/domain/exclusion.schema.json`
- `packages/contracts/schemas/domain/rate.schema.json`
- `packages/contracts/schemas/domain/resource.schema.json`
- `packages/contracts/schemas/domain/rfi.schema.json`
- `packages/contracts/schemas/domain/risk.schema.json`
- `packages/contracts/schemas/domain/tender-clarification.schema.json`
- `packages/contracts/schemas/domain/wbs.schema.json`

### Central orchestrator

- `packages/orchestrator/README.md`
- `packages/orchestrator/config/agent-registry.yaml`
- `packages/orchestrator/pyproject.toml`
- `packages/orchestrator/requirements.lock`
- `packages/orchestrator/src/construction_ai_orchestrator/__init__.py`
- `packages/orchestrator/src/construction_ai_orchestrator/__main__.py`
- `packages/orchestrator/src/construction_ai_orchestrator/artifacts.py`
- `packages/orchestrator/src/construction_ai_orchestrator/cli.py`
- `packages/orchestrator/src/construction_ai_orchestrator/consolidation.py`
- `packages/orchestrator/src/construction_ai_orchestrator/errors.py`
- `packages/orchestrator/src/construction_ai_orchestrator/models.py`
- `packages/orchestrator/src/construction_ai_orchestrator/registry.py`
- `packages/orchestrator/src/construction_ai_orchestrator/router.py`
- `packages/orchestrator/src/construction_ai_orchestrator/runner.py`
- `packages/orchestrator/src/construction_ai_orchestrator/validation.py`

### Automated tests

- `tests/conftest.py`
- `tests/contracts/test_existing_agent_schemas.py`
- `tests/contracts/test_schema_catalog.py`
- `tests/orchestrator/test_artifacts.py`
- `tests/orchestrator/test_cli.py`
- `tests/orchestrator/test_registry.py`
- `tests/orchestrator/test_router.py`
- `tests/orchestrator/test_runner.py`

## Files modified

- `docs/phase-7/README.md`

## Files moved or renamed

None.

## Files deleted

None.

Generated Python and pytest cache directories were removed from the working tree and are excluded by `.gitignore`; they were never tracked repository content.
