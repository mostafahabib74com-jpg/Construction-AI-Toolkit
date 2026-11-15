"""Opt-in preparation of hierarchical BOQs, retaining original row evidence."""

from __future__ import annotations

from dataclasses import dataclass, replace
import re

from construction_ai_scheduling.domain.errors import BOQImportError
from construction_ai_scheduling.infrastructure.boq_reader import BOQPreview, _is_blank, _json_value, optional_text


@dataclass(frozen=True)
class PreparedBOQ:
    preview: BOQPreview
    excluded_rows: tuple[dict, ...]
    combined_groups: tuple[tuple[int, ...], ...]


def prepare_boq(preview: BOQPreview, mapping: dict, *, combine_merged_items=False, exclude_structural_rows=False) -> PreparedBOQ:
    """Prepare only after explicit options are selected; never fill missing quantities.

    A composite item requires the same vertical merged range in quantity and
    item-code columns. A shared quantity is used once, with all descriptions.
    """
    required = [mapping.get(field) for field in ("description", "quantity", "unit")]
    if any(column not in preview.frame.columns for column in required):
        raise BOQImportError("Map description, quantity and unit before preparing the BOQ.")
    frame = preview.frame.copy(deep=True)
    desc_col, qty_col, unit_col = required
    code_col = mapping.get("item_code")
    provenance, groups, excluded = {}, [], []
    original_rows = {int(index): {str(key): _json_value(value) for key, value in row.items()} for index, row in frame.iterrows()}
    if combine_merged_items and code_col:
        qty_index = list(frame.columns).index(qty_col) + 1
        code_index = list(frame.columns).index(code_col) + 1
        code_spans = {(first, last) for first, last, left, right in preview.merged_ranges if left == right == code_index and last > first}
        for first, last, left, right in sorted(preview.merged_ranges):
            if left != right or left != qty_index or (first, last) not in code_spans:
                continue
            members = [index for index in range(first, last + 1) if index in frame.index]
            if len(members) < 2 or first not in frame.index or _is_blank(frame.at[first, qty_col]):
                continue
            units = {optional_text(frame.at[index, unit_col]) for index in members if not _is_blank(frame.at[index, unit_col])}
            if len(units) > 1:
                raise BOQImportError(f"Merged quantity rows {first}-{last} have conflicting units; review them manually.")
            descriptions = [optional_text(frame.at[index, desc_col]) for index in members if not _is_blank(frame.at[index, desc_col])]
            frame.at[first, desc_col] = "\n".join(descriptions)
            if _is_blank(frame.at[first, unit_col]) and units:
                frame.at[first, unit_col] = next(iter(units))
            provenance[first] = {"source_rows": members, "merged_quantity_used_once": True,
                                 "original_rows": {str(index): original_rows[index] for index in members}}
            frame = frame.drop(members[1:])
            groups.append(tuple(members))
    context = []
    for index, row in frame.iterrows():
        code = optional_text(row[code_col]) if code_col else None
        desc = optional_text(row[desc_col])
        no_measurement = _is_blank(row[qty_col]) and _is_blank(row[unit_col])
        heading = no_measurement and bool(desc) and (not code or bool(re.fullmatch(r"\d+(?:\.\d+)?", code)))
        total = no_measurement and not desc and bool(code) and bool(re.match(r"^(?:الاجمالي|الإجمالي|ضريبة|total\b|subtotal\b|vat\b)", code, re.IGNORECASE))
        if heading:
            if code:
                context = [dict(row=int(index), code=code, description=desc)]
            else:
                context = [item for item in context if item.get("code")] + [dict(row=int(index), code=None, description=desc)]
        if exclude_structural_rows and (heading or total):
            excluded.append({"source_row": int(index), "role": "heading_or_scope" if heading else "total", "original": original_rows[int(index)]})
            continue
        if context and not heading and not total:
            provenance.setdefault(int(index), {"source_rows": [int(index)]})["scope_context"] = list(context)
    if excluded:
        frame = frame.drop([item["source_row"] for item in excluded])
    frame.attrs["row_provenance"] = provenance
    return PreparedBOQ(replace(preview, frame=frame), tuple(excluded), tuple(groups))
