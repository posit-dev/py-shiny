"""Tests for `shiny.Session`."""

import pytest

from shiny import *


def test_require_active_session_error_messages():
    # require_active_session() should report the caller's name when an error occurs.
    with pytest.raises(RuntimeError, match=r"Progress\(\) must be called"):
        ui.Progress()

    with pytest.raises(RuntimeError, match=r"notification.remove\(\) must be called.*"):
        ui.notification_remove("abc")
