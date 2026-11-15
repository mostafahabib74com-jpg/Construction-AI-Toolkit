# High-priority milestone 1 change inventory

## Files created

### Reports

- `docs/phase-7/HIGH-PRIORITY-MILESTONE-1.md`
- `docs/phase-7/HIGH-PRIORITY-TEST-RESULTS.md`
- `docs/phase-7/HIGH-PRIORITY-CHANGE-INVENTORY.md`

### Canonical schemas

- `packages/contracts/schemas/domain/calendar.schema.json`
- `packages/contracts/schemas/domain/contract-requirement.schema.json`
- `packages/contracts/schemas/domain/schedule.schema.json`

### Legacy-to-canonical adapters

- `packages/orchestrator/src/construction_ai_orchestrator/adapters/__init__.py`
- `packages/orchestrator/src/construction_ai_orchestrator/adapters/common.py`
- `packages/orchestrator/src/construction_ai_orchestrator/adapters/estimation.py`
- `packages/orchestrator/src/construction_ai_orchestrator/adapters/planning.py`
- `packages/orchestrator/src/construction_ai_orchestrator/adapters/tender.py`

### Accuracy policies

- `packages/orchestrator/src/construction_ai_orchestrator/policies/__init__.py`
- `packages/orchestrator/src/construction_ai_orchestrator/policies/common.py`
- `packages/orchestrator/src/construction_ai_orchestrator/policies/contract.py`
- `packages/orchestrator/src/construction_ai_orchestrator/policies/engine.py`
- `packages/orchestrator/src/construction_ai_orchestrator/policies/pricing.py`
- `packages/orchestrator/src/construction_ai_orchestrator/policies/quantity.py`
- `packages/orchestrator/src/construction_ai_orchestrator/policies/release.py`
- `packages/orchestrator/src/construction_ai_orchestrator/policies/schedule.py`

### Tests

- `tests/adapters/test_common_adapters.py`
- `tests/adapters/test_repository_examples.py`
- `tests/adapters/test_tender_and_planning_adapters.py`
- `tests/orchestrator/test_policy_integration.py`
- `tests/policies/test_contract.py`
- `tests/policies/test_quantity_and_pricing.py`
- `tests/policies/test_release.py`
- `tests/policies/test_schedule.py`

## Files modified

- `docs/phase-7/README.md`
- `packages/contracts/README.md`
- `packages/contracts/schemas/catalog.json`
- `packages/contracts/schemas/core/artifact.schema.json`
- `packages/contracts/schemas/core/review.schema.json`
- `packages/contracts/schemas/core/source-document.schema.json`
- `packages/contracts/schemas/domain/deliverable.schema.json`
- `packages/contracts/schemas/domain/rate.schema.json`
- `packages/orchestrator/README.md`
- `packages/orchestrator/src/construction_ai_orchestrator/__init__.py`
- `packages/orchestrator/src/construction_ai_orchestrator/consolidation.py`
- `packages/orchestrator/src/construction_ai_orchestrator/errors.py`
- `packages/orchestrator/src/construction_ai_orchestrator/runner.py`
- `tests/contracts/test_schema_catalog.py`
- `tests/orchestrator/test_runner.py`

## Files moved or renamed

None.

## Files deleted

None.

No file under `agents/` or `AI-Prompts/` was changed.
