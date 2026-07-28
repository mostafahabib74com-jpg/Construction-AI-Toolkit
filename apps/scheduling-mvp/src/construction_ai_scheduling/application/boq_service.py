"""Coordinate BOQ preview, mapping, validation, editing, and persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from construction_ai_orchestrator.validation import SchemaCatalog

from construction_ai_scheduling.domain.errors import BOQImportError
from construction_ai_scheduling.domain.models import BOQImport, BOQRow
from construction_ai_scheduling.domain.units import normalize_unit
from construction_ai_scheduling.domain.validation import boq_validation_status, validate_boq_fields
from construction_ai_scheduling.infrastructure.boq_reader import (
    BOQPreview,
    TabularBOQReader,
    optional_text,
    parse_quantity,
)
from construction_ai_scheduling.infrastructure.sqlite_repository import SQLiteRepository

from .planning_contracts import BOQ_IMPORT_ROW_SCHEMA, BOQ_IMPORT_SCHEMA


def _error_messages(issues: list[Any]) -> tuple[str, ...]:
    return tuple(f"[{issue.code}] {issue.message}" for issue in issues)


class BOQService:
    def __init__(self, repository: SQLiteRepository, catalog: SchemaCatalog, reader: TabularBOQReader | None = None) -> None:
        self.repository = repository
        self.catalog = catalog
        self.reader = reader or TabularBOQReader()

    def preview(
        self,
        file_name: str,
        content: bytes,
        *,
        sheet_name: str | None = None,
        header_row: int | None = None,
    ) -> BOQPreview:
        return self.reader.read(file_name, content, sheet_name=sheet_name, header_row=header_row)

    def sheet_names(self, file_name: str, content: bytes) -> tuple[str, ...]:
        return self.reader.sheet_names(file_name, content)

    @staticmethod
    def suggest_mapping(columns: tuple[str, ...]) -> dict[str, str | None]:
        return TabularBOQReader.suggest_mapping(columns)

    def import_boq(
        self,
        *,
        project_id: str,
        file_name: str,
        preview: BOQPreview,
        mapping: dict[str, str | None],
    ) -> BOQImport:
        if self.repository.get_project(project_id) is None:
            raise BOQImportError("Select a saved project before importing a BOQ.")
        if preview.frame.empty:
            raise BOQImportError("The selected BOQ sheet does not contain any data rows.")
        import_id = f"IMP-{uuid4().hex[:12].upper()}"
        rows: list[BOQRow] = []
        for source in self.reader.extract_rows(preview.frame, mapping):
            issues = validate_boq_fields(
                description=source["description"],
                quantity=source["quantity"],
                quantity_raw=source["quantity_raw"],
                unit=source["unit"],
            )
            row = BOQRow(
                row_id=f"BOQ-{uuid4().hex[:12].upper()}",
                project_id=project_id,
                import_id=import_id,
                source_row_number=source["source_row_number"],
                item_code=source["item_code"],
                description=source["description"],
                quantity=source["quantity"],
                quantity_raw=source["quantity_raw"],
                unit=source["unit"],
                normalized_unit=normalize_unit(source["unit"]),
                validation_status=boq_validation_status(issues),
                validation_errors=_error_messages(issues),
                raw_data=source["raw_data"],
            )
            self.catalog.assert_valid(row.to_dict(), BOQ_IMPORT_ROW_SCHEMA)
            rows.append(row)

        batch = BOQImport(
            import_id=import_id,
            project_id=project_id,
            source_file_name=Path(file_name).name,
            source_type=preview.source_type,
            source_sheet=preview.selected_sheet,
            imported_at=datetime.now(timezone.utc),
            rows=tuple(rows),
        )
        self.catalog.assert_valid(batch.to_dict(), BOQ_IMPORT_SCHEMA)
        self.repository.create_boq_import(batch)
        return batch

    def list_imports(self, project_id: str) -> list[dict[str, Any]]:
        return self.repository.list_boq_imports(project_id)

    def get_rows(self, import_id: str) -> list[BOQRow]:
        return self.repository.get_boq_rows(import_id)

    def update_rows(self, import_id: str, edited: list[dict[str, Any]]) -> list[BOQRow]:
        existing = {row.row_id: row for row in self.repository.get_boq_rows(import_id)}
        if not existing:
            raise BOQImportError("The selected BOQ import does not exist or contains no rows.")
        if len({str(item.get("row_id")) for item in edited}) != len(edited):
            raise BOQImportError("Edited BOQ rows contain duplicate identifiers.")

        updated: list[BOQRow] = []
        for value in edited:
            row_id = str(value.get("row_id") or "")
            if row_id not in existing:
                raise BOQImportError("Edited BOQ data contains a row that is not part of the selected import.")
            original = existing[row_id]
            quantity, quantity_raw = parse_quantity(value.get("quantity"))
            description = optional_text(value.get("description"))
            unit = optional_text(value.get("unit"))
            issues = validate_boq_fields(
                description=description,
                quantity=quantity,
                quantity_raw=quantity_raw,
                unit=unit,
            )
            row = BOQRow(
                row_id=original.row_id,
                project_id=original.project_id,
                import_id=original.import_id,
                source_row_number=original.source_row_number,
                item_code=optional_text(value.get("item_code")),
                description=description,
                quantity=quantity,
                quantity_raw=quantity_raw,
                unit=unit,
                normalized_unit=normalize_unit(unit),
                validation_status=boq_validation_status(issues),
                validation_errors=_error_messages(issues),
                raw_data=original.raw_data,
            )
            self.catalog.assert_valid(row.to_dict(), BOQ_IMPORT_ROW_SCHEMA)
            updated.append(row)
        self.repository.update_boq_rows(updated)
        return updated
