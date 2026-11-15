"""Deterministic quantity/productivity duration calculations."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP, Decimal
from typing import Any

from construction_ai_scheduling.domain.errors import SchedulingInputError


ROUNDING_MODES = {
    "ROUND_HALF_UP": ROUND_HALF_UP,
    "ROUND_HALF_EVEN": ROUND_HALF_EVEN,
    "ROUND_UP": ROUND_UP,
    "ROUND_DOWN": ROUND_DOWN,
}


@dataclass(frozen=True, slots=True)
class DurationCalculation:
    exact_duration_hours: Decimal
    exact_duration_days: Decimal
    display_duration_days: Decimal
    formula: str
    calculation_trace: dict[str, Any]


def _issue(code: str, message: str, field: str) -> dict[str, str]:
    return {"code": code, "message": message, "field": field, "severity": "error"}


def calculate_duration(
    *,
    activity_type: str,
    quantity: Decimal | None,
    productivity_rate: Decimal | None,
    productivity_basis: str | None,
    crew_count: int | None,
    working_hours_per_day: Decimal | None,
    rounding_precision: int,
    rounding_mode: str,
) -> DurationCalculation:
    """Calculate exact hours/days, rounding only the displayed duration."""
    if activity_type in {"start_milestone", "finish_milestone"}:
        return DurationCalculation(
            Decimal("0"),
            Decimal("0"),
            Decimal("0").quantize(Decimal("1").scaleb(-rounding_precision)),
            "milestone = 0 working hours",
            {"activity_type": activity_type, "exact_duration_hours": "0", "exact_duration_days": "0"},
        )

    issues: list[dict[str, str]] = []
    if activity_type != "task_dependent":
        issues.append(_issue("ACTIVITY_TYPE_INVALID", "Activity type is not supported.", "activity_type"))
    if quantity is None:
        issues.append(_issue("QUANTITY_REQUIRED", "Quantity is required; it will not be invented.", "quantity"))
    elif quantity <= 0:
        issues.append(_issue("QUANTITY_NOT_POSITIVE", "Quantity must be greater than zero.", "quantity"))
    if productivity_rate is None:
        issues.append(
            _issue("PRODUCTIVITY_REQUIRED", "Productivity is required; it will not be assumed.", "productivity_rate")
        )
    elif productivity_rate <= 0:
        issues.append(
            _issue("PRODUCTIVITY_NOT_POSITIVE", "Productivity must be greater than zero.", "productivity_rate")
        )
    if productivity_basis not in {"per_day", "per_hour"}:
        issues.append(
            _issue("PRODUCTIVITY_BASIS_REQUIRED", "Select whether productivity is per day or per hour.", "productivity_basis")
        )
    if crew_count is None:
        issues.append(_issue("CREW_COUNT_REQUIRED", "Crew count is required; it will not be assumed.", "crew_count"))
    elif crew_count <= 0:
        issues.append(_issue("CREW_COUNT_NOT_POSITIVE", "Crew count must be greater than zero.", "crew_count"))
    if working_hours_per_day is None:
        issues.append(_issue("CALENDAR_HOURS_REQUIRED", "Calendar working hours are required.", "calendar_id"))
    elif working_hours_per_day <= 0:
        issues.append(_issue("CALENDAR_HOURS_NOT_POSITIVE", "Calendar working hours must be positive.", "calendar_id"))
    if rounding_precision < 0 or rounding_precision > 6:
        issues.append(_issue("ROUNDING_PRECISION_INVALID", "Rounding precision must be between 0 and 6.", "rounding_precision"))
    if rounding_mode not in ROUNDING_MODES:
        issues.append(_issue("ROUNDING_MODE_INVALID", "Rounding mode is not supported.", "rounding_mode"))
    if issues:
        raise SchedulingInputError("Activity duration inputs are invalid.", issues)

    assert quantity is not None
    assert productivity_rate is not None
    assert crew_count is not None
    assert working_hours_per_day is not None
    effective_output = productivity_rate * Decimal(crew_count)
    if productivity_basis == "per_day":
        exact_days = quantity / effective_output
        exact_hours = exact_days * working_hours_per_day
        formula = "duration_days = quantity / (productivity_per_day * crew_count)"
    else:
        exact_hours = quantity / effective_output
        exact_days = exact_hours / working_hours_per_day
        formula = "duration_hours = quantity / (productivity_per_hour * crew_count)"

    quantum = Decimal("1").scaleb(-rounding_precision)
    display_days = exact_days.quantize(quantum, rounding=ROUNDING_MODES[rounding_mode])
    return DurationCalculation(
        exact_duration_hours=exact_hours,
        exact_duration_days=exact_days,
        display_duration_days=display_days,
        formula=formula,
        calculation_trace={
            "quantity": format(quantity, "f"),
            "productivity_rate": format(productivity_rate, "f"),
            "productivity_basis": productivity_basis,
            "crew_count": crew_count,
            "effective_output": format(effective_output, "f"),
            "working_hours_per_day": format(working_hours_per_day, "f"),
            "exact_duration_hours": format(exact_hours, "f"),
            "exact_duration_days": format(exact_days, "f"),
            "display_duration_days": format(display_days, "f"),
            "rounding_precision": rounding_precision,
            "rounding_mode": rounding_mode,
        },
    )
