"""Read CSV/XLSX BOQs without inventing values or semantic mappings."""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

from construction_ai_scheduling.domain.errors import BOQImportError

HEADER_SCAN_LIMIT = 100
RAW_FIELD_ALIASES = {
    "item_code": {
        "item", "itemcode", "itemid", "itemno", "itemnumber", "boqitem", "boqno", "code", "no",
        "رقم", "رقم البند", "كود", "كود البند", "البند",
    },
    "description": {
        "description", "itemdescription", "workdescription", "scope", "scopeofwork",
        "الوصف", "وصف", "وصف البند", "البيان", "بيان الأعمال", "بيان الاعمال", "الأعمال", "الاعمال",
    },
    "quantity": {"quantity", "qty", "boqquantity", "الكمية", "كمية"},
    "unit": {"unit", "uom", "unitofmeasure", "measurementunit", "الوحدة", "وحدة", "وحدة القياس"},
}


def _header_key(value: Any) -> str:
    if value is None:
        return ""
    decomposed = unicodedata.normalize("NFKD", str(value).casefold())
    without_marks = "".join(character for character in decomposed if unicodedata.category(character) != "Mn")
    return "".join(character for character in without_marks if character.isalnum())


FIELD_ALIASES = {
    field: {_header_key(alias) for alias in aliases}
    for field, aliases in RAW_FIELD_ALIASES.items()
}


@dataclass(frozen=True, slots=True)
class BOQPreview:
    frame: pd.DataFrame
    columns: tuple[str, ...]
    sheet_names: tuple[str, ...]
    source_type: str
    selected_sheet: str | None
    header_row_number: int
    header_row_options: tuple[tuple[int, str], ...]


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


def _header_score(record: pd.Series) -> int:
    keys = {_header_key(value) for value in record if not _is_blank(value)}
    keys.discard("")
    return sum(bool(keys & aliases) for aliases in FIELD_ALIASES.values())


def _header_options(frame: pd.DataFrame) -> tuple[tuple[int, str], ...]:
    options: list[tuple[int, str]] = []
    for index, record in frame.head(HEADER_SCAN_LIMIT).iterrows():
        values = [str(value).strip() for value in record if not _is_blank(value)]
        if not values:
            continue
        summary = " | ".join(values[:4])
        if len(summary) > 120:
            summary = summary[:117] + "..."
        options.append((int(index) + 1, summary))
    return tuple(options)


def _detect_header_row(frame: pd.DataFrame, options: tuple[tuple[int, str], ...]) -> int:
    scored = [
        (int(index) + 1, _header_score(record))
        for index, record in frame.head(HEADER_SCAN_LIMIT).iterrows()
        if any(not _is_blank(value) for value in record)
    ]
    if not scored:
        raise BOQImportError("The BOQ file does not contain a nonblank header row.")
    row_number, score = max(scored, key=lambda item: (item[1], -item[0]))
    return row_number if score >= 2 else options[0][0]


def _column_names(record: pd.Series) -> list[str]:
    names: list[str] = []
    counts: dict[str, int] = {}
    for position, value in enumerate(record, start=1):
        base = optional_text(value) or f"Column {position}"
        counts[base] = counts.get(base, 0) + 1
        names.append(base if counts[base] == 1 else f"{base} ({counts[base]})")
    return names


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

    def read(
        self,
        file_name: str,
        content: bytes,
        *,
        sheet_name: str | None = None,
        header_row: int | None = None,
    ) -> BOQPreview:
        if not content:
            raise BOQImportError("The uploaded BOQ file is empty.")
        source_type = self.source_type(file_name)
        try:
            if source_type == "csv":
                raw_frame = pd.read_csv(BytesIO(content), dtype=object, header=None)
                sheet_names: tuple[str, ...] = ()
                selected_sheet = None
            else:
                names = self.sheet_names(file_name, content)
                if not names:
                    raise BOQImportError("The XLSX workbook does not contain a worksheet.")
                selected_sheet = sheet_name or names[0]
                if selected_sheet not in names:
                    raise BOQImportError(f"Worksheet '{selected_sheet}' does not exist in the workbook.")
                raw_frame = pd.read_excel(
                    BytesIO(content),
                    sheet_name=selected_sheet,
                    dtype=object,
                    engine="openpyxl",
                    header=None,
                )
                sheet_names = names
        except BOQImportError:
            raise
        except Exception as exc:
            raise BOQImportError(f"The {source_type.upper()} file could not be read as a tabular BOQ.") from exc

        if raw_frame.empty or not len(raw_frame.columns):
            raise BOQImportError("The BOQ file does not contain any columns.")
        options = _header_options(raw_frame)
        selected_header_row = header_row or _detect_header_row(raw_frame, options)
        if selected_header_row < 1 or selected_header_row > len(raw_frame):
            raise BOQImportError(
                f"Header row must be between 1 and {len(raw_frame)} for the selected worksheet."
            )
        header_record = raw_frame.iloc[selected_header_row - 1]
        if all(_is_blank(value) for value in header_record):
            raise BOQImportError(f"Selected header row {selected_header_row} is blank.")

        frame = raw_frame.iloc[selected_header_row:].copy()
        frame.columns = _column_names(header_record)
        frame.index = range(selected_header_row + 1, len(raw_frame) + 1)
        frame = frame.loc[frame.apply(lambda row: any(not _is_blank(value) for value in row), axis=1)]
        return BOQPreview(
            frame=frame,
            columns=tuple(frame.columns),
            sheet_names=sheet_names,
            source_type=source_type,
            selected_sheet=selected_sheet,
            header_row_number=selected_header_row,
            header_row_options=options,
        )

    @staticmethod
    def suggest_mapping(columns: tuple[str, ...]) -> dict[str, str | None]:
        suggestions: dict[str, str | None] = {}
        for field, aliases in FIELD_ALIASES.items():
            matches = [column for column in columns if _header_key(column) in aliases]
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
                "source_row_number": int(index),
                "item_code": optional_text(mapped("item_code")),
                "description": optional_text(mapped("description")),
                "quantity": quantity,
                "quantity_raw": quantity_raw,
                "unit": optional_text(mapped("unit")),
                "raw_data": raw_data,
            })
        return extracted
