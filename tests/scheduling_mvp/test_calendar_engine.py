from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

from construction_ai_scheduling.domain.calendar_engine import (
    add_working_hours,
    subtract_working_hours,
    validate_calendar,
    working_intervals,
)
from construction_ai_scheduling.domain.schedule_models import CalendarBreak, CalendarException, ProjectCalendar


ZONE = ZoneInfo("Asia/Riyadh")


def _calendar(*, exceptions=(), breaks=()) -> ProjectCalendar:
    moment = datetime(2026, 1, 1, tzinfo=ZONE)
    return ProjectCalendar(
        "CAL-1",
        "SCH-1",
        "6D-8H",
        "Six day calendar",
        "Asia/Riyadh",
        ("saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"),
        time(7),
        Decimal("8"),
        tuple(breaks),
        tuple(exceptions),
        moment,
        moment,
    )


def test_working_hours_are_net_and_break_extends_elapsed_time():
    calendar = _calendar(breaks=(CalendarBreak("B-1", time(12), time(13)),))
    intervals = working_intervals(calendar, date(2026, 9, 1))

    assert intervals == (
        (datetime(2026, 9, 1, 7, tzinfo=ZONE), datetime(2026, 9, 1, 12, tzinfo=ZONE)),
        (datetime(2026, 9, 1, 13, tzinfo=ZONE), datetime(2026, 9, 1, 16, tzinfo=ZONE)),
    )
    assert add_working_hours(datetime(2026, 9, 1, 7, tzinfo=ZONE), Decimal("8"), calendar) == datetime(
        2026, 9, 1, 16, tzinfo=ZONE
    )


def test_non_working_exception_overrides_weekly_calendar():
    calendar = _calendar(exceptions=(CalendarException("E-1", date(2026, 9, 2), False, None, None, "Holiday"),))

    finish = add_working_hours(datetime(2026, 9, 1, 15, tzinfo=ZONE), Decimal("2"), calendar)

    assert finish == datetime(2026, 9, 3, 9, tzinfo=ZONE)


def test_working_exception_can_override_weekend_and_hours():
    calendar = _calendar(
        exceptions=(CalendarException("E-1", date(2026, 9, 4), True, time(9), Decimal("4"), "Special shift"),)
    )

    assert working_intervals(calendar, date(2026, 9, 4)) == (
        (datetime(2026, 9, 4, 9, tzinfo=ZONE), datetime(2026, 9, 4, 13, tzinfo=ZONE)),
    )


def test_signed_working_time_shift_is_reversible_across_weekend():
    calendar = _calendar()
    start = datetime(2026, 9, 3, 14, tzinfo=ZONE)
    finish = add_working_hours(start, Decimal("4"), calendar)

    assert finish == datetime(2026, 9, 5, 10, tzinfo=ZONE)
    assert subtract_working_hours(finish, Decimal("4"), calendar) == start


def test_overlapping_breaks_are_invalid():
    calendar = _calendar(
        breaks=(CalendarBreak("B-1", time(10), time(11)), CalendarBreak("B-2", time(10, 30), time(12)))
    )
    assert {item["code"] for item in validate_calendar(calendar)} == {"CALENDAR_BREAK_OVERLAP"}
