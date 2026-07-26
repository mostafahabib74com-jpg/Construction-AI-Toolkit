from __future__ import annotations

import pytest

from construction_ai_orchestrator.errors import ContractValidationError

PROJECT_SCHEMA = "https://construction-ai-toolkit.dev/contracts/v1/core/project.schema.json"


def test_catalog_loads_all_declared_schemas(catalog):
    assert len(catalog.schema_ids) == 29
    assert len(set(catalog.schema_ids)) == 29


def test_all_schemas_pass_meta_schema_validation(catalog):
    catalog.check_all_schemas()


def test_valid_project_passes(catalog, project):
    catalog.assert_valid(project, PROJECT_SCHEMA)


def test_invalid_currency_returns_precise_issue(catalog, project):
    project["currency"] = "Saudi Riyal"
    issues = catalog.validate(project, PROJECT_SCHEMA)
    assert issues
    assert issues[0]["path"] == "$.currency"


def test_assert_valid_raises_typed_error(catalog, project):
    del project["project_id"]
    with pytest.raises(ContractValidationError) as caught:
        catalog.assert_valid(project, PROJECT_SCHEMA)
    assert caught.value.code == "CONTRACT_VALIDATION_ERROR"
    assert caught.value.details["issues"]
