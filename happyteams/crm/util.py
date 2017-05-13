from calendar import Calendar, monthrange
from datetime import date, datetime
from dateutil.parser import parse as parse_date


_calendar = Calendar()


__all__ = ('get_first_day_of_the_month', 'get_month_start_time', 'get_month_start_dates',
           'get_last_day_of_the_month', 'get_month_end_time', 'calculate_work_hours')


def get_first_day_of_the_month(month=None, year=None):
    """Get a date object for the start of the month"""
    if isinstance(month, date):
        year = month.year
        month = month.month
    elif year is None and isinstance(month, str):
        month = parse_date(month)
        year = month.year
        month = month.month

    if None in (year, month):
        today = date.today()
        if year is None:
            year = today.year
        if month is None:
            month = today.month

    return date(year=year, month=month, day=1)


def get_month_start_time(*args, **kwargs):
    month = get_first_day_of_the_month(*args, **kwargs)
    return datetime(month.year, month.month, 1)


def get_month_end_time(*args, **kwargs):
    month = get_first_day_of_the_month(*args, **kwargs)
    return datetime(month.year, month.month, monthrange(month.year, month.month)[1], 23, 59, 59, 99999)


def get_last_day_of_the_month(*args, **kwargs):
    month = get_first_day_of_the_month(*args, **kwargs)
    return date(year=month.year, month=month.month, day=monthrange(month.year, month.month)[1])


def calculate_work_hours(year, month, start_day=1, end_day=31,
                         work_hrs_per_day=8, workweek_starts=0, workweek_ends=4):
    work_hours = 0
    end_day = min(end_day, monthrange(year, month)[1])
    for week in _calendar.monthdayscalendar(year, month):
        for i, day in enumerate(week):
            if all((day >= start_day,
                    day <= end_day,
                    i >= workweek_starts,
                    i <= workweek_ends)):
                work_hours += work_hrs_per_day
    return work_hours


def get_month_start_dates(start, end):
    """Generates the start date for the months in the period specified by the start and end dates."""

    assert start < end, "Must end after start (start: {}, end: {})".format(start, end)

    start_year = start.year
    start_month = start.month
    num_months = ((end.year - start_year) * 12 +
                  (end.month - start_month))

    yield start

    for i in range(num_months):
        next_month = start_month + i
        month = date(year=start_year + int(next_month / 12.),
                     month=1 + next_month % 12,
                     day=1)
        yield month
