from copy import deepcopy
from decimal import Decimal
import pytest

from construction_ai_scheduling.domain.estimating import calculate_estimate, empty_estimate, resource_cost


def estimate():
    value = empty_estimate()
    value["items"] = [{"item_id": "X1", "description": "خرسانة تجريبية", "unit": "m3", "quantity": "10",
                       "quantity_source": "Synthetic test measurement", "resources": [
        {"name": "Synthetic resource", "category": "material", "resource_unit": "m3", "consumption": "1",
         "rate": "100", "waste_percent": "0", "source": "Synthetic arithmetic only", "price_date": "2026-01-01", "currency": "SAR"}]}]
    return value


@pytest.mark.parametrize(("basis", "expected"), [("markup", "1250.00"), ("margin", "1333.33")])
def test_profit_basis_changes_selling_price(basis, expected):
    value = estimate()
    value["commercial"].update(profit_basis=basis, profit_percent="25")
    result = calculate_estimate(value, "SAR")
    assert result["status"] == "calculated"
    assert result["summary"]["Selling price excluding tax"] == expected


def test_tax_follows_discount_and_explicit_cost_bridge():
    value = estimate()
    value["commercial"].update(indirects="100", indirects_basis="Synthetic site allowance", profit_percent="20", discount="20", tax_percent="15")
    summary = calculate_estimate(value, "SAR")["summary"]
    assert summary["Cost base"] == "1100.00"
    assert summary["Selling price excluding tax"] == "1300.00"
    assert summary["Tax amount"] == "195.00"
    assert summary["Total including tax"] == "1495.00"


@pytest.mark.parametrize(("field", "invalid"), [("rate", None), ("rate", "NaN"), ("rate", "Infinity"), ("rate", "-1"), ("consumption", "0"), ("source", ""), ("price_date", "bad-date"), ("currency", "USD")])
def test_missing_unusable_or_mixed_currency_resource_blocks_final_price(field, invalid):
    value = estimate()
    value["items"][0]["resources"][0][field] = invalid
    result = calculate_estimate(value, "SAR")
    assert result["status"] == "blocked"
    assert result["summary"] is None
    assert result["issues"]


def test_no_resources_means_unpriced_not_zero_cost():
    value = estimate()
    value["items"][0]["resources"] = []
    result = calculate_estimate(value, "SAR")
    assert result["status"] == "blocked"
    assert not result["items"]


def test_material_waste_is_exact_and_requires_basis():
    resource = estimate()["items"][0]["resources"][0]
    resource.update(consumption="0.1", rate="0.2", waste_percent="5", waste_basis="Synthetic allowance")
    assert resource_cost(resource, "SAR") == Decimal("0.021")
    resource["waste_basis"] = ""
    with pytest.raises(ValueError):
        resource_cost(resource, "SAR")


@pytest.mark.parametrize("change", [dict(profit_basis="margin", profit_percent="100"), dict(discount="1001"), dict(overhead="50")])
def test_invalid_commercial_inputs_block_price(change):
    value = estimate()
    value["commercial"].update(change)
    assert calculate_estimate(value, "SAR")["summary"] is None


def test_estimate_draft_persists_separately_per_project(scheduling_repository, saved_project, project_service, valid_project_input):
    other = project_service.create_project({**valid_project_input, "name": "Other project"})
    value = estimate()
    scheduling_repository.save_estimate_draft(saved_project.project_id, value)
    assert scheduling_repository.get_estimate_draft(saved_project.project_id) == value
    assert scheduling_repository.get_estimate_draft(other.project_id) is None
