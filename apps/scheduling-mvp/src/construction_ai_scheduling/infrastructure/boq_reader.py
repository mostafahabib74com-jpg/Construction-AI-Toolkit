"""Read CSV/XLSX BOQs without inventing values or semantic mappings."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

from construction_ai_scheduling.domain.errors import BOQImportError

FIELD_ALIASES = {
    "item_code": {"item", "itemcode", "itemid", "itemno", "itemnumber", "boqitem", "boqno", "code", "no"},
    "description": {"description", "itemdescription", "workdescription", "scope", "scopeofwork"},
    "quantity": {"quantity", "qty", "boqquantity"},
    "unit": {"unit", "uom", "unitofmeasure", "measurementunit"},
}


@dataclass(frozen=True, slots=True)
class BOQPreview:
    frame: pd.DataFrame
    columns: tuple[str, ...]
    sheet_names: tuple[str, ...]
    source_type: str
    selected_sheet: str | None


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    try:
        if bool(pd.isna(value)):
            return True
    except (TypeError, ValueError):
        pass
    return isinstance(value, str) and not value.strip()


def _json_value(value: Any) -> Any:
    if _is_blank(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def optional_text(value: Any) -> str | None:
    if _is_blank(value):
        return None
    return str(value).strip()


def parse_quantity(value: Any) -> tuple[float | None, str | float | int | None]:
    raw = _json_value(value)
    if raw is None:
        return None, None
    if isinstance(raw, bool):
        return None, str(raw)
    if isinstance(raw, (int, float)):
        numeric = float(raw)
        return (numeric, raw) if math.isfinite(numeric) else (None, raw)
    candidate = str(raw).strip()
    try:
        numeric = float(candidate)
    except ValueError:
        return None, candidate
    return (numeric, candidate) if math.isfinite(numeric) else (None, candidate)


class TabularBOQReader:
    allowed_extensions = {".csv": "csv", ".xlsx": "xlsx"}

    @staticmethod
    def source_type(file_name: str) -> str:
        extension = Path(file_name).suffix.lower()
        try:
            return TabularBOQReader.allowed_extensions[extension]
        except KeyError as exc:
            raise BOQImportError("BOQ file must be CSV or XLSX.") from exc

    def sheet_names(self, file_name: str, content: bytes) -> tuple[str, ...]:
        if not content:
            raise BOQImportError("The uploaded BOQ file is empty.")
        if self.source_type(file_name) == "csv":
            return ()
        try:
            with pd.ExcelFile(BytesIO(content), engine="openpyxl") as workbook:
                return tuple(workbook.sheet_names)
        except Exception as exc:
            raise BOQImportError("The XLSX workbook could not be read.") from exc

    def read(self, file_name: str, content: bytes, *, sheet_name: str | None = None) -> BOQPreview:
        if not content:
            raise BOQImportError("The uploaded BOQ file is empty.")
        source_type = self.source_type(file_name)
        try:
            if source_type == "csv":
                frame = pd.read_csv(BytesIO(content), dtype=object)
                sheet_names: tuple[str, ...] = ()
                selected_sheet = None
            else:
                names = self.sheet_names(file_name, content)
                if not names:
                    raise BOQImportError("The XLSX workbook does not contain a worksheet.")
                selected_sheet = sheet_name or names[0]
                if selected_sheet not in names:
                    raise BOQImportError(f"Worksheet '{selected_sheet}' does not exist in the workbook.")
                frame = pd.read_excel(BytesIO(content), sheet_name=selected_sheet, dtype=object, engine="openpyxl")
                sheet_names = names
        except BOQImportError:
            raise
        except Exception as exc:
            raise BOQImportError(f"The {source_type.upper()} file could not be read as a tabular BOQ.") from exc

        frame.columns = [str(column).strip() for column in frame.columns]
        frame = frame.loc[frame.apply(lambda row: any(not _is_blank(value) for value in row), axis=1)].reset_index(drop=True)
        if not len(frame.columns):
            raise BOQImportError("The BOQ file does not contain any columns.")
        return BOQPreview(
            frame=frame,
            columns=tuple(frame.columns),
            sheet_names=sheet_names,
            source_type=source_type,
            selected_sheet=selected_sheet,
        )

    @staticmethod
    def suggest_mapping(columns: tuple[str, ...]) -> dict[str, str | None]:
        suggestions: dict[str, str | None] = {}
        for field, aliases in FIELD_ALIASES.items():
            matches = [column for column in columns if re.sub(r"[^a-z0-9]", "", column.lower()) in aliases]
            suggestions[field] = matches[0] if len(matches) == 1 else None
        return suggestions

    @staticmethod
    def extract_rows(frame: pd.DataFrame, mapping: dict[str, str | None]) -> list[dict[str, Any]]:
        unknown = {column for column in mapping.values() if column is not None and column not in frame.columns}
        if unknown:
            raise BOQImportError(f"Mapped BOQ columns do not exist: {', '.join(sorted(unknown))}.")
        extracted: list[dict[str, Any]] = []
        for index, record in frame.iterrows():
            raw_data = {str(column): _json_value(record[column]) for column in frame.columns}

            def mapped(field: str) -> Any:
                column = mapping.get(field)
                return record[column] if column else None

            quantity, quantity_raw = parse_quantity(mapped("quantity"))
            extracted.append({
                "source_row_number": int(index) + 2,
                "item_code": optional_text(mapped("item_code")),
                "description": optional_text(mapped("description")),
                "quantity": quantity,
                "quantity_raw": quantity_raw,
                "unit": optional_text(mapped("unit")),
                "raw_data": raw_data,
            })
        return extracted
