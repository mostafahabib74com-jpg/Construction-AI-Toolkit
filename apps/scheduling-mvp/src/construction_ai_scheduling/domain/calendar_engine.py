"""Working-time arithmetic for project calendars."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from construction_ai_scheduling.domain.errors import SchedulingInputError
from construction_ai_scheduling.domain.schedule_models import CalendarException, ProjectCalendar


SECONDS_PER_HOUR = Decimal("3600")
MAX_SEARCH_DAYS = 36600


def _issue(code: str, message: str, field: str) -> dict[str, str]:
    return {"code": code, "message": message, "field": field, "severity": "error"}


def validate_calendar(calendar: ProjectCalendar) -> tuple[dict[str, str], ...]:
    issues: list[dict[str, str]] = []
    try:
        ZoneInfo(calendar.time_zone)
    except ZoneInfoNotFoundError:
        issues.append(_issue("CALENDAR_TIME_ZONE_INVALID", "Calendar time zone is not available.", "time_zone"))
    if not calendar.working_weekdays:
        issues.append(_issue("CALENDAR_WEEKDAYS_REQUIRED", "Select at least one working weekday.", "working_weekdays"))
    if calendar.working_hours_per_day <= 0:
        issues.append(_issue("CALENDAR_HOURS_NOT_POSITIVE", "Working hours per day must be positive.", "working_hours_per_day"))
    if len(set(calendar.working_weekdays)) != len(calendar.working_weekdays):
        issues.append(_issue("CALENDAR_WEEKDAY_DUPLICATE", "Working weekdays must be unique.", "working_weekdays"))
    valid_weekdays = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
    if set(calendar.working_weekdays) - valid_weekdays:
        issues.append(_issue("CALENDAR_WEEKDAY_INVALID", "A working weekday is invalid.", "working_weekdays"))

    previous_end: time | None = None
    for item in sorted(calendar.breaks, key=lambda value: value.start_time):
        if item.end_time <= item.start_time:
            issues.append(_issue("CALENDAR_BREAK_INVALID", "A break must end after it starts.", "breaks"))
        if previous_end and item.start_time < previous_end:
            issues.append(_issue("CALENDAR_BREAK_OVERLAP", "Calendar breaks must not overlap.", "breaks"))
        previous_end = max(previous_end, item.end_time) if previous_end else item.end_time
    dates = [item.exception_date for item in calendar.exceptions]
    if len(dates) != len(set(dates)):
        issues.append(_issue("CALENDAR_EXCEPTION_DUPLICATE", "Only one exception is allowed per date.", "exceptions"))
    for item in calendar.exceptions:
        if item.working and item.working_hours is not None and item.working_hours <= 0:
            issues.append(
                _issue("CALENDAR_EXCEPTION_HOURS_NOT_POSITIVE", "A working exception must have positive hours.", "exceptions")
            )
    return tuple(issues)


def assert_valid_calendar(calendar: ProjectCalendar) -> None:
    issues = validate_calendar(calendar)
    if issues:
        raise SchedulingInputError("Project calendar is invalid.", issues)


def _exception_for(calendar: ProjectCalendar, day: date) -> CalendarException | None:
    return next((item for item in calendar.exceptions if item.exception_date == day), None)


def _day_settings(calendar: ProjectCalendar, day: date) -> tuple[time, Decimal] | None:
    exception = _exception_for(calendar, day)
    if exception is not None:
        if not exception.working:
            return None
        return (
            exception.workday_start_time or calendar.workday_start_time,
            exception.working_hours or calendar.working_hours_per_day,
        )
    if day.strftime("%A").lower() not in calendar.working_weekdays:
        return None
    return calendar.workday_start_time, calendar.working_hours_per_day


def working_intervals(calendar: ProjectCalendar, day: date) -> tuple[tuple[datetime, datetime], ...]:
    """Return local, time-zone-aware productive intervals for one date."""
    settings = _day_settings(calendar, day)
    if settings is None:
        return ()
    start_time, hours = settings
    zone = ZoneInfo(calendar.time_zone)
    cursor = datetime.combine(day, start_time, zone)
    remaining_seconds = hours * SECONDS_PER_HOUR
    intervals: list[tuple[datetime, datetime]] = []
    for item in sorted(calendar.breaks, key=lambda value: value.start_time):
        break_start = datetime.combine(day, item.start_time, zone)
        break_end = datetime.combine(day, item.end_time, zone)
        if break_end <= cursor:
            continue
        if break_start > cursor:
            available = Decimal(str((break_start - cursor).total_seconds()))
            consumed = min(available, remaining_seconds)
            if consumed > 0:
                end = cursor + timedelta(seconds=float(consumed))
                intervals.append((cursor, end))
                remaining_seconds -= consumed
                cursor = end
            if remaining_seconds == 0:
                break
        cursor = max(cursor, break_end)
    if remaining_seconds > 0:
        intervals.append((cursor, cursor + timedelta(seconds=float(remaining_seconds))))
    return tuple(intervals)


def _as_calendar_time(moment: datetime, calendar: ProjectCalendar) -> datetime:
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("Scheduling datetimes must be time-zone aware.")
    return moment.astimezone(ZoneInfo(calendar.time_zone))


def next_working_time(moment: datetime, calendar: ProjectCalendar) -> datetime:
    """Return the same instant if productive, otherwise the next productive instant."""
    current = _as_calendar_time(moment, calendar)
    for offset in range(MAX_SEARCH_DAYS):
        day = current.date() + timedelta(days=offset)
        for start, finish in working_intervals(calendar, day):
            if offset == 0 and start <= current < finish:
                return current
            if start >= current:
                return start
    raise SchedulingInputError(
        "No future working time could be found.",
        (_issue("CALENDAR_NO_FUTURE_WORK", "No future working time could be found.", "calendar_id"),),
    )


def previous_working_time(moment: datetime, calendar: ProjectCalendar) -> datetime:
    """Return the same instant if productive, otherwise the previous productive boundary."""
    current = _as_calendar_time(moment, calendar)
    for offset in range(MAX_SEARCH_DAYS):
        day = current.date() - timedelta(days=offset)
        for start, finish in reversed(working_intervals(calendar, day)):
            if offset == 0 and start < current <= finish:
                return current
            if finish <= current:
                return finish
    raise SchedulingInputError(
        "No previous working time could be found.",
        (_issue("CALENDAR_NO_PREVIOUS_WORK", "No previous working time could be found.", "calendar_id"),),
    )


def add_working_hours(moment: datetime, hours: Decimal, calendar: ProjectCalendar) -> datetime:
    """Shift an instant by signed working hours using this calendar."""
    assert_valid_calendar(calendar)
    if hours == 0:
        return _as_calendar_time(moment, calendar)
    if hours < 0:
        return subtract_working_hours(moment, -hours, calendar)

    remaining = hours * SECONDS_PER_HOUR
    current = next_working_time(moment, calendar)
    while remaining > 0:
        intervals = working_intervals(calendar, current.date())
        progressed = False
        for start, finish in intervals:
            if finish <= current:
                continue
            active = max(current, start)
            available = Decimal(str((finish - active).total_seconds()))
            if remaining <= available:
                return active + timedelta(seconds=float(remaining))
            remaining -= available
            current = finish
            progressed = True
        if not progressed and not intervals:
            current = next_working_time(current + timedelta(days=1), calendar)
        else:
            current = next_working_time(current + timedelta(microseconds=1), calendar)
    return current


def subtract_working_hours(moment: datetime, hours: Decimal, calendar: ProjectCalendar) -> datetime:
    if hours < 0:
        return add_working_hours(moment, -hours, calendar)
    if hours == 0:
        return _as_calendar_time(moment, calendar)
    remaining = hours * SECONDS_PER_HOUR
    current = previous_working_time(moment, calendar)
    while remaining > 0:
        intervals = working_intervals(calendar, current.date())
        progressed = False
        for start, finish in reversed(intervals):
            if start >= current:
                continue
            active = min(current, finish)
            available = Decimal(str((active - start).total_seconds()))
            if remaining <= available:
                return active - timedelta(seconds=float(remaining))
            remaining -= available
            current = start
            progressed = True
        if not progressed and not intervals:
            current = previous_working_time(current - timedelta(days=1), calendar)
        else:
            current = previous_working_time(current - timedelta(microseconds=1), calendar)
    return current
