"""Estimation Agent common-data adapter."""

from __future__ import annotations

from typing import Any

from .common import CommonAdapter

MONEY_SCHEMA = "https://construction-ai-toolkit.dev/contracts/v1/core/money.schema.json"
QUANTITY_SCHEMA = "https://construction-ai-toolkit.dev/contracts/v1/core/quantity.schema.json"


class EstimationAdapter(CommonAdapter):
    agent_id = "estimation-agent"

    def adapt_source_document(self, value: dict[str, Any]) -> dict[str, Any]:
        source = self._base_source(value)
        source["issue_date"] = value.get("date")
        return self._validate_source(source)

    def adapt_money(self, value: dict[str, Any], *, pricing_basis: str) -> dict[str, Any]:
        money = {
            "amount": value.get("amount"),
            "currency": value.get("currency"),
            "base_date": value.get("pricing_date"),
            "pricing_basis": pricing_basis,
        }
        self.catalog.assert_valid(money, MONEY_SCHEMA)
        return money

    def adapt_quantity(
        self,
        value: dict[str, Any],
        *,
        unit_system: str,
        assumption_id: str | None = None,
    ) -> dict[str, Any]:
        basis = value.get("basis")
        status = "allowance" if basis in {"assumed", "allowance", "provisional"} else "confirmed"
        source = value.get("source") or {}
        quantity = {
            "value": value.get("value"),
            "unit": {"code": value.get("unit"), "system": unit_system},
            "status": status,
            "measurement_basis": basis,
            "source_ids": [source["source_id"]] if source.get("source_id") else [],
            "assumption_id": assumption_id,
        }
        self.catalog.assert_valid(quantity, QUANTITY_SCHEMA)
        return quantity
