from __future__ import annotations

from decimal import Decimal

import pytest

from construction_ai_scheduling.domain.duration_engine import calculate_duration
from construction_ai_scheduling.domain.errors import SchedulingInputError


def test_per_day_duration_keeps_exact_value_and_rounds_display_only():
    result = calculate_duration(
        activity_type="task_dependent",
        quantity=Decimal("100"),
        productivity_rate=Decimal("12"),
        productivity_basis="per_day",
        crew_count=3,
        working_hours_per_day=Decimal("8"),
        rounding_precision=2,
        rounding_mode="ROUND_HALF_UP",
    )

    assert result.exact_duration_days == Decimal("100") / Decimal("36")
    assert result.exact_duration_hours == Decimal("800") / Decimal("36")
    assert result.display_duration_days == Decimal("2.78")


def test_per_hour_duration_uses_calendar_hours_for_day_display():
    result = calculate_duration(
        activity_type="task_dependent",
        quantity=Decimal("120"),
        productivity_rate=Decimal("5"),
        productivity_basis="per_hour",
        crew_count=2,
        working_hours_per_day=Decimal("6"),
        rounding_precision=3,
        rounding_mode="ROUND_HALF_EVEN",
    )

    assert result.exact_duration_hours == Decimal("12")
    assert result.exact_duration_days == Decimal("2")
    assert result.display_duration_days == Decimal("2.000")


def test_milestone_is_zero_duration_without_fabricated_inputs():
    result = calculate_duration(
        activity_type="start_milestone",
        quantity=None,
        productivity_rate=None,
        productivity_basis=None,
        crew_count=None,
        working_hours_per_day=None,
        rounding_precision=2,
        rounding_mode="ROUND_HALF_UP",
    )

    assert result.exact_duration_hours == 0
    assert result.display_duration_days == Decimal("0.00")


def test_missing_or_non_positive_inputs_are_blocked():
    with pytest.raises(SchedulingInputError) as caught:
        calculate_duration(
            activity_type="task_dependent",
            quantity=None,
            productivity_rate=Decimal("0"),
            productivity_basis=None,
            crew_count=0,
            working_hours_per_day=Decimal("8"),
            rounding_precision=2,
            rounding_mode="ROUND_HALF_UP",
        )

    codes = {issue["code"] for issue in caught.value.issues}
    assert {"QUANTITY_REQUIRED", "PRODUCTIVITY_NOT_POSITIVE", "PRODUCTIVITY_BASIS_REQUIRED", "CREW_COUNT_NOT_POSITIVE"} <= codes
