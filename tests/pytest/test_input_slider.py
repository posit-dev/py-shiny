"""Tests for `shiny.ui.input_slider()` value encoding."""

from __future__ import annotations

import os
import time
from datetime import date, datetime, timedelta, timezone

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


def _format_date_utc(ms: float) -> date:
    """Mimic the client's `formatDateUTC()` / `strftime.utc()` read-back."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date()


@pytest.mark.skipif(
    not hasattr(time, "tzset"), reason="time.tzset() is not available on this platform"
)
@pytest.mark.parametrize("tz", TIMEZONES)
def test_as_numeric_date_is_utc_midnight(tz: str):
    """`date` values must encode UTC midnight, regardless of the server's timezone.

    The client formats and reads slider dates back in UTC, so encoding local
    midnight loses a day for any positive UTC offset. See #2398.
    """
    old_tz = os.environ.get("TZ")
    os.environ["TZ"] = tz
    time.tzset()
    try:
        for d in DATES:
            num = _as_numeric(d)
            assert (
                num
                == datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp()
                * 1000
            )
            assert _format_date_utc(num) == d
    finally:
        if old_tz is None:
            del os.environ["TZ"]
        else:
            os.environ["TZ"] = old_tz
        time.tzset()


def test_as_numeric_other_types():
    assert _as_numeric(10) == 10
    assert _as_numeric(1.5) == 1.5
    assert _as_numeric(timedelta(days=1)) == 86400000
    # `datetime` is an absolute point in time; it keeps its own conversion.
    dt = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert _as_numeric(dt) == dt.timestamp() * 1000
