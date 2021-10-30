"""Tests for `shiny.shinysession`."""

import pytest

from shiny import *


def test_require_active_session_error_messages():
    # _require_active_session() should report the caller's name when an error occurs.
    with pytest.raises(RuntimeError, match=r"Progress\(\) must be called"):
        Progress()

    with pytest.raises(RuntimeError, match=r"notification_remove\(\) must be called.*"):
        notification_remove("abc")
