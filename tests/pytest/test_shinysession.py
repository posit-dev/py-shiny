"""Tests for `shiny.Session`."""

import pytest

from shiny import ui
from shiny.reactive import effect, flush, isolate
from shiny.session import Inputs
from shiny.types import SilentException


def test_require_active_session_error_messages():
    # require_active_session() should report the caller's name when an error occurs.
    with pytest.raises(RuntimeError, match=r"Progress\(\) must be called"):
        ui.Progress()

    with pytest.raises(RuntimeError, match=r"notification.remove\(\) must be called.*"):
        ui.notification_remove("abc")


def test_input_readonly():
    input = Inputs({})

    with isolate():
        with pytest.raises(RuntimeError):
            input.x.set(1)


def test_input_nonexistent():
    # Make sure that if you try to access an input that doesn't exist, it:
    # - Raises a SilentException
    # - Appears _not_ to add the item to the Inputs object (even though under the hood,
    #   it does actually add it)
    input = Inputs({})

    with isolate():
        assert "x" not in input
        with pytest.raises(SilentException):
            input.x()
        assert "x" not in input
        with pytest.raises(SilentException):
            input.x()

    with isolate():
        with pytest.raises(SilentException):
            input.y()
        assert "y" not in input
        with pytest.raises(SilentException):
            input.y()
        assert "y" not in input


@pytest.mark.asyncio
async def test_input_nonexistent_deps():
    # Make sure that `"x" in input` causes a reactive dependency to be created.
    input = Inputs({})
    result = None

    @effect()
    def o1():
        nonlocal result
        result = "x" in input

    await flush()
    assert result is False
    assert o1._exec_count == 1

    # This should invalidate o1 and cause it to re-execute on the next flush().
    input.x._set(1)
    await flush()
    assert result is True
    assert o1._exec_count == 2

    # This shouldn't invalidate o1, because it doesn't change the status of x's
    # existence. (x already exists; this just changes its value.)
    input.x._set(2)
    await flush()
    assert result is True
    assert o1._exec_count == 2
