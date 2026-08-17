"""Tests for `shiny.ui.input_slider()` value encoding."""

from __future__ import annotations

import contextlib
import os
import time
from datetime import date, datetime, timedelta, timezone
from typing import Generator

import pytest

from shiny.ui._input_slider import _as_numeric

TIMEZONES = [
    "UTC",
    "Europe/Amsterdam",  # +01:00 / +02:00 -- from the bug report (#2398)
    "Asia/Tokyo",  # +09:00
    "Asia/Kathmandu",  # +05:45 -- not a whole-hour offset
    "Pacific/Chatham",  # +12:45 / +13:45 -- not a whole-hour offset, and DST
    "Pacific/Kiritimati",  # +14:00 -- the furthest-forward offset on Earth
    "America/New_York",  # -05:00 / -04:00
    "Etc/GMT+12",  # -12:00 -- the furthest-behind offset
]

DATES = [date(2025, 1, 1), date(2026, 1, 1), date(2025, 7, 1)]

DATETIMES = [
    datetime(2025, 1, 1, 12, 0),
    datetime(2026, 1, 1, 0, 0),  # midnight: an offset shifts the calendar date too
    datetime(2025, 7, 1, 23, 59),
]

# `time.tzset()` is POSIX-only, so these tests cannot control the timezone on Windows.
skip_without_tzset = pytest.mark.skipif(
    not hasattr(time, "tzset"), reason="time.tzset() is not available on this platform"
)


@contextlib.contextmanager
def local_timezone(tz: str) -> Generator[None, None, None]:
    """Run the block as if the server were in timezone `tz`."""
    old_tz = os.environ.get("TZ")
    os.environ["TZ"] = tz
    time.tzset()
    try:
        yield
    finally:
        if old_tz is None:
            del os.environ["TZ"]
        else:
            os.environ["TZ"] = old_tz
        time.tzset()


def _read_back_date(ms: float) -> date:
    """Mimic the client's `formatDateUTC()` / `strftime.utc()` read-back."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date()


def _read_back_datetime(ms: float) -> datetime:
    """Mimic the `shiny.datetime` input handler's read-back."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).replace(tzinfo=None)


@skip_without_tzset
@pytest.mark.parametrize("tz", TIMEZONES)
def test_as_numeric_date_is_utc_midnight(tz: str):
    """`date` values must encode UTC midnight, regardless of the server's timezone.

    The client formats and reads slider dates back in UTC, so encoding local
    midnight loses a day for any positive UTC offset. See #2398.
    """
    with local_timezone(tz):
        for d in DATES:
            num = _as_numeric(d)
            assert (
                num
                == datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp()
                * 1000
            )
            assert _read_back_date(num) == d


@skip_without_tzset
@pytest.mark.parametrize("tz", TIMEZONES)
def test_as_numeric_naive_datetime_is_utc(tz: str):
    """Naive `datetime` values must be anchored to UTC, not the server's timezone.

    A naive `datetime` carries no offset of its own, and the client sends back
    epoch seconds that the `shiny.datetime` input handler decodes as UTC. Letting
    `.timestamp()` assume local time would shift the value by the server's offset.
    """
    with local_timezone(tz):
        for dt in DATETIMES:
            num = _as_numeric(dt)
            assert num == dt.replace(tzinfo=timezone.utc).timestamp() * 1000
            assert _read_back_datetime(num) == dt


@skip_without_tzset
@pytest.mark.parametrize("tz", TIMEZONES)
def test_as_numeric_aware_datetime_is_absolute(tz: str):
    """Aware `datetime` values already name an instant, so they keep their offset."""
    with local_timezone(tz):
        for dt in DATETIMES:
            for offset_hours in (0, 5, -8):
                aware = dt.replace(tzinfo=timezone(timedelta(hours=offset_hours)))
                num = _as_numeric(aware)
                assert num == aware.timestamp() * 1000
                assert _read_back_datetime(num) == dt - timedelta(hours=offset_hours)


def test_as_numeric_other_types():
    assert _as_numeric(10) == 10
    assert _as_numeric(1.5) == 1.5
    assert _as_numeric(timedelta(days=1)) == 86400000
