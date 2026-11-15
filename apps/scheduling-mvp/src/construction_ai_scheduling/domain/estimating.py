"""Exact, evidence-backed unit-rate and estimate calculations; no market defaults."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


CATEGORIES = ("material", "labor", "equipment", "subcontract", "other")


def number(value, field: str, *, positive: bool = False) -> Decimal:
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field}: a value is required.")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field}: enter a decimal number.") from exc
    if not result.is_finite() or result < 0 or (positive and result == 0):
        raise ValueError(f"{field}: enter a finite {'positive' if positive else 'nonnegative'} number.")
    return result


def money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def resource_cost(resource: dict, currency: str) -> Decimal:
    for field in ("name", "resource_unit", "source", "price_date"):
        if not str(resource.get(field) or "").strip():
            raise ValueError(f"Resource {field} is required.")
    try:
        date.fromisoformat(str(resource["price_date"]))
    except ValueError as exc:
        raise ValueError("Price date must use YYYY-MM-DD.") from exc
    if resource.get("currency") != currency:
        raise ValueError("Resource currency must match project currency; normalize quotations explicitly first.")
    if resource.get("category") not in CATEGORIES:
        raise ValueError("Resource category is invalid.")
    consumption = number(resource.get("consumption"), "Consumption per BOQ unit", positive=True)
    rate = number(resource.get("rate"), "Resource rate")
    waste = number(resource.get("waste_percent"), "Waste percentage")
    if waste and resource["category"] != "material":
        raise ValueError("Waste allowance applies to materials only; record other burdens as separate resources.")
    if waste and not str(resource.get("waste_basis") or "").strip():
        raise ValueError("A material waste allowance requires its basis.")
    return consumption * rate * (1 + waste / 100)


def calculate_estimate(payload: dict, currency: str) -> dict:
    issues, rows, traces = [], [], []
    seen = set()
    direct = Decimal(0)
    if not payload.get("items"):
        issues.append("At least one estimate item is required.")
    for item in payload.get("items", []):
        item_id = str(item.get("item_id") or "").strip()
        try:
            if not item_id or item_id in seen:
                raise ValueError("Item IDs must be present and unique.")
            seen.add(item_id)
            for field in ("description", "unit", "quantity_source"):
                if not str(item.get(field) or "").strip():
                    raise ValueError(f"{field} is required.")
            quantity = number(item.get("quantity"), "Item quantity", positive=True)
            if not item.get("resources"):
                raise ValueError("Resource build-up is missing; no unit rate has been assumed.")
            unit_cost = Decimal(0)
            item_traces = []
            for resource in item["resources"]:
                amount = resource_cost(resource, currency)
                unit_cost += amount
                item_traces.append({"Item ID": item_id, **resource, "Cost per BOQ unit": str(amount),
                                    "Formula": "consumption * rate * (1 + waste_percent / 100)"})
            amount = quantity * unit_cost
            direct += amount
            traces.extend(item_traces)
            rows.append({"Item ID": item_id, "Description": item["description"], "Unit": item["unit"],
                         "Quantity": str(quantity), "Direct unit cost": str(unit_cost), "Amount": money(amount),
                         "Quantity source": item["quantity_source"]})
        except (ValueError, TypeError) as exc:
            issues.append(f"{item_id or 'Unnamed item'}: {exc}")
    summary = None
    settings = payload.get("commercial", {})
    try:
        additions = {key: number(settings.get(key), key) for key in ("indirects", "contingency", "overhead")}
        for key, value in additions.items():
            if value and not str(settings.get(key + "_basis") or "").strip():
                raise ValueError(f"{key}: record an allocation/risk basis to avoid duplicate allowances.")
        profit_percent = number(settings.get("profit_percent"), "Profit percentage")
        tax_percent = number(settings.get("tax_percent"), "Tax percentage")
        discount = number(settings.get("discount"), "Discount")
        base = direct + sum(additions.values())
        if settings.get("profit_basis") == "markup":
            before_discount = base * (1 + profit_percent / 100)
        elif settings.get("profit_basis") == "margin" and profit_percent < 100:
            before_discount = base / (1 - profit_percent / 100)
        else:
            raise ValueError("Select markup or a gross margin below 100%.")
        if discount > before_discount:
            raise ValueError("Discount exceeds the selling price.")
        net = before_discount - discount
        tax = net * tax_percent / 100
        summary = {"Currency": currency, "Direct cost": money(direct),
                   **{key.title(): money(value) for key, value in additions.items()},
                   "Cost base": money(base), "Profit basis": settings["profit_basis"],
                   "Profit percentage": str(profit_percent), "Profit before discount": money(before_discount - base),
                   "Discount": money(discount), "Selling price excluding tax": money(net),
                   "Tax percentage": str(tax_percent), "Tax amount": money(tax), "Total including tax": money(net + tax)}
    except (ValueError, TypeError) as exc:
        issues.append(str(exc))
    return {"status": "blocked" if issues else "calculated", "issues": issues, "items": rows,
            "resources": traces, "summary": None if issues else summary,
            "notice": "User-supplied inputs only. Evidence references require human review; this is not an approval of quotations or quantities."}


def empty_estimate() -> dict:
    return {"items": [], "commercial": {"indirects": "0", "contingency": "0", "overhead": "0",
            "indirects_basis": "", "contingency_basis": "", "overhead_basis": "",
            "profit_basis": "markup", "profit_percent": "0", "tax_percent": "0", "discount": "0"}}
