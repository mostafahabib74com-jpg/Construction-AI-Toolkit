"""Basic project and BOQ validation for the intake milestone."""

from __future__ import annotations

import math
import re
from datetime import date, time
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import ValidationIssue

WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)
UNIT_SYSTEMS = {"SI", "imperial", "mixed"}
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")


def _required_text(value: dict[str, Any], field: str, label: str) -> ValidationIssue | None:
    candidate = value.get(field)
    if not isinstance(candidate, str) or not candidate.strip():
        return ValidationIssue(field, "REQUIRED", f"{label} is required.", "missing")
    return None


def validate_project_input(value: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for field, label in (
        ("name", "Project name"),
        ("client", "Client"),
        ("contractor", "Contractor"),
        ("consultant", "Consultant"),
        ("project_type", "Project type"),
        ("location", "Location"),
        ("currency", "Currency"),
        ("unit_system", "Unit system"),
        ("time_zone", "Time zone"),
        ("workday_start_time", "Workday start time"),
    ):
        issue = _required_text(value, field, label)
        if issue:
            issues.append(issue)

    start = value.get("planned_start_date")
    finish = value.get("required_completion_date")
    if not isinstance(start, date):
        issues.append(ValidationIssue("planned_start_date", "REQUIRED", "Planned start date is required.", "missing"))
    if not isinstance(finish, date):
        issues.append(ValidationIssue("required_completion_date", "REQUIRED", "Required completion date is required.", "missing"))
    if isinstance(start, date) and isinstance(finish, date) and finish < start:
        issues.append(ValidationIssue(
            "required_completion_date",
            "DATE_ORDER",
            "Required completion date cannot be earlier than the planned start date.",
        ))

    days = value.get("working_days_per_week")
    if not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= 7:
        issues.append(ValidationIssue(
            "working_days_per_week",
            "WORKING_DAYS_RANGE",
            "Working days per week must be a whole number from 1 to 7.",
        ))

    hours = value.get("working_hours_per_day")
    if not isinstance(hours, (int, float)) or isinstance(hours, bool) or not math.isfinite(float(hours)) or not 0 < float(hours) <= 24:
        issues.append(ValidationIssue(
            "working_hours_per_day",
            "WORKING_HOURS_RANGE",
            "Working hours per day must be greater than 0 and no more than 24.",
        ))

    weekdays = value.get("working_weekdays")
    if not isinstance(weekdays, (list, tuple)) or not weekdays:
        issues.append(ValidationIssue("working_weekdays", "REQUIRED", "Select the actual working weekdays.", "missing"))
    else:
        unknown = [day for day in weekdays if day not in WEEKDAYS]
        if unknown or len(set(weekdays)) != len(weekdays):
            issues.append(ValidationIssue("working_weekdays", "WORKDAY_INVALID", "Working weekdays contain an invalid or duplicate value."))
        if isinstance(days, int) and len(weekdays) != days:
            issues.append(ValidationIssue(
                "working_weekdays",
                "WORKDAY_COUNT_MISMATCH",
                "The selected weekdays must match working days per week.",
            ))

    currency = value.get("currency")
    if isinstance(currency, str) and currency.strip() and not CURRENCY_PATTERN.fullmatch(currency.strip().upper()):
        issues.append(ValidationIssue("currency", "CURRENCY_INVALID", "Currency must be a three-letter ISO-style code such as SAR or USD."))

    unit_system = value.get("unit_system")
    if isinstance(unit_system, str) and unit_system and unit_system not in UNIT_SYSTEMS:
        issues.append(ValidationIssue("unit_system", "UNIT_SYSTEM_INVALID", "Unit system must be SI, imperial, or mixed."))

    time_value = value.get("workday_start_time")
    if isinstance(time_value, time):
        pass
    elif isinstance(time_value, str) and time_value and not TIME_PATTERN.fullmatch(time_value):
        issues.append(ValidationIssue("workday_start_time", "TIME_INVALID", "Workday start time must use 24-hour HH:MM format."))

    time_zone = value.get("time_zone")
    if isinstance(time_zone, str) and time_zone.strip():
        try:
            ZoneInfo(time_zone.strip())
        except ZoneInfoNotFoundError:
            issues.append(ValidationIssue("time_zone", "TIME_ZONE_INVALID", "Enter a valid IANA time zone such as Asia/Riyadh."))

    return issues


def validate_boq_fields(*, description: Any, quantity: Any, quantity_raw: Any, unit: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(description, str) or not description.strip():
        issues.append(ValidationIssue("description", "BOQ_DESCRIPTION_REQUIRED", "Description is required.", "missing"))

    if quantity is None:
        code = "BOQ_QUANTITY_INVALID" if quantity_raw not in (None, "") else "BOQ_QUANTITY_REQUIRED"
        message = "Quantity must be numeric." if code.endswith("INVALID") else "Quantity is required."
        category = "invalid" if code.endswith("INVALID") else "missing"
        issues.append(ValidationIssue("quantity", code, message, category))
    elif isinstance(quantity, bool) or not isinstance(quantity, (int, float)) or not math.isfinite(float(quantity)):
        issues.append(ValidationIssue("quantity", "BOQ_QUANTITY_INVALID", "Quantity must be a finite number."))
    elif float(quantity) < 0:
        issues.append(ValidationIssue("quantity", "BOQ_QUANTITY_NEGATIVE", "Quantity cannot be negative."))

    if not isinstance(unit, str) or not unit.strip():
        issues.append(ValidationIssue("unit", "BOQ_UNIT_REQUIRED", "Unit is required.", "missing"))
    elif not re.fullmatch(r"[A-Za-z0-9._/%-]{1,24}", unit.strip()):
        issues.append(ValidationIssue("unit", "BOQ_UNIT_INVALID", "Unit must use 1-24 letters, numbers, or . _ / % - characters."))
    return issues


def boq_validation_status(issues: list[ValidationIssue]) -> str:
    if not issues:
        return "valid"
    return "invalid" if any(issue.category == "invalid" for issue in issues) else "incomplete"
