"""Filesystem and application settings for the local scheduling MVP."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    repo_root: Path
    database_path: Path
    schema_root: Path
    migration_path: Path


def load_settings() -> Settings:
    repo_root = Path(__file__).resolve().parents[4]
    configured_database = os.environ.get("CONSTRUCTION_AI_DB_PATH")
    database_path = (
        Path(configured_database).expanduser().resolve()
        if configured_database
        else repo_root / ".local" / "scheduling-mvp.db"
    )
    return Settings(
        repo_root=repo_root,
        database_path=database_path,
        schema_root=repo_root / "packages" / "contracts" / "schemas",
        migration_path=repo_root / "apps" / "scheduling-mvp" / "migrations" / "001_initial.sql",
    )
