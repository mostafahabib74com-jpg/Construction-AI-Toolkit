"""Offline JSON Schema catalog and instance validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import FormatChecker
from jsonschema.validators import validator_for
from referencing import Registry, Resource

from .errors import ConfigurationError, ContractValidationError


def _json_path(parts: list[Any]) -> str:
    value = "$"
    for part in parts:
        value += f"[{part}]" if isinstance(part, int) else f".{part}"
    return value


class SchemaCatalog:
    """Loads all canonical schemas from an explicit local-only catalog."""

    def __init__(self, *, root: Path, schemas: dict[str, dict[str, Any]], registry: Registry) -> None:
        self.root = root
        self._schemas = dict(schemas)
        self._registry = registry
        self._format_checker = FormatChecker()

    @classmethod
    def from_directory(cls, root: str | Path) -> "SchemaCatalog":
        schema_root = Path(root).resolve()
        catalog_path = schema_root / "catalog.json"
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ConfigurationError("Unable to load the schema catalog.", path=str(catalog_path)) from exc
        paths = catalog.get("schemas")
        if not isinstance(paths, list) or not paths:
            raise ConfigurationError("Schema catalog requires a non-empty 'schemas' list.", path=str(catalog_path))

        schemas: dict[str, dict[str, Any]] = {}
        resources: list[tuple[str, Resource[Any]]] = []
        for relative in paths:
            if not isinstance(relative, str):
                raise ConfigurationError("Schema catalog entries must be strings.", path=str(catalog_path))
            path = (schema_root / relative).resolve()
            if schema_root not in path.parents:
                raise ConfigurationError("Schema catalog path escapes its root.", path=str(path))
            try:
                schema = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ConfigurationError("Unable to load a canonical schema.", path=str(path)) from exc
            schema_id = schema.get("$id")
            if not isinstance(schema_id, str) or not schema_id:
                raise ConfigurationError("Canonical schema requires a non-empty $id.", path=str(path))
            if schema_id in schemas:
                raise ConfigurationError(f"Duplicate canonical schema ID: {schema_id}", path=str(path))
            schemas[schema_id] = schema
            resources.append((schema_id, Resource.from_contents(schema)))

        return cls(root=schema_root, schemas=schemas, registry=Registry().with_resources(resources))

    @property
    def schema_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._schemas))

    def check_all_schemas(self) -> None:
        for schema_id, schema in self._schemas.items():
            validator = validator_for(schema)
            try:
                validator.check_schema(schema)
            except Exception as exc:
                raise ConfigurationError("Canonical schema failed meta-schema validation.", path=schema_id) from exc

    def validate(self, instance: Any, schema_id: str) -> list[dict[str, Any]]:
        schema = self._schemas.get(schema_id)
        if schema is None:
            raise ConfigurationError(f"Unknown canonical schema ID: {schema_id}")
        validator_class = validator_for(schema)
        validator = validator_class(schema, registry=self._registry, format_checker=self._format_checker)
        errors = sorted(validator.iter_errors(instance), key=lambda error: [str(part) for part in error.absolute_path])
        return [
            {
                "path": _json_path(list(error.absolute_path)),
                "message": error.message,
                "validator": error.validator,
            }
            for error in errors
        ]

    def assert_valid(self, instance: Any, schema_id: str) -> None:
        issues = self.validate(instance, schema_id)
        if issues:
            first = issues[0]
            raise ContractValidationError(
                f"Contract validation failed with {len(issues)} issue(s): {first['message']}",
                path=first["path"],
                remediation="Correct the payload to match the canonical contract.",
                details={"schema_id": schema_id, "issues": issues},
            )
