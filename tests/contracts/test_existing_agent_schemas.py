from __future__ import annotations

import json
from urllib.parse import urldefrag, urljoin

from jsonschema.validators import validator_for


def _agent_schemas(repo_root):
    return {
        path: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((repo_root / "agents").rglob("*.schema.json"))
    }


def _references(value):
    if isinstance(value, dict):
        if isinstance(value.get("$ref"), str):
            yield value["$ref"]
        for child in value.values():
            yield from _references(child)
    elif isinstance(value, list):
        for child in value:
            yield from _references(child)


def test_all_existing_agent_schemas_are_valid_draft_2020_12(repo_root):
    schemas = _agent_schemas(repo_root)
    assert len(schemas) == 96
    for schema in schemas.values():
        validator_for(schema).check_schema(schema)


def test_existing_agent_schema_ids_are_unique(repo_root):
    schemas = _agent_schemas(repo_root)
    schema_ids = [schema["$id"] for schema in schemas.values()]
    assert len(schema_ids) == len(set(schema_ids))


def test_existing_agent_schema_references_resolve_locally(repo_root):
    schemas = _agent_schemas(repo_root)
    schema_ids = {schema["$id"] for schema in schemas.values()}
    for path, schema in schemas.items():
        for reference in _references(schema):
            if reference.startswith("#"):
                continue
            target, _ = urldefrag(urljoin(schema["$id"], reference))
            assert target in schema_ids, f"Unresolved reference in {path}: {reference}"
