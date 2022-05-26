"""Tests for polling-related functionality."""

import os
import tempfile
import pytest
import asyncio
from typing import List

from shiny.input_handler import ActionButtonValue
from shiny.reactive._core import ReactiveWarning
from shiny._decorators import *
from shiny.reactive import *
from shiny._validation import SilentException, req

from .mocktime import MockTime


@pytest.mark.asyncio
async def test_poll():
    poll_invocations = 0
    poll_return1 = 0  # A non-reactive component of the return value
    poll_return2 = Value(0)  # A reactive component of the return value
    value_invocations = 0
    value_dep = Value(0)

    def poll_func():
        nonlocal poll_invocations
        poll_invocations += 1
        return poll_return1 + poll_return2()

    @poll(poll_func)
    def value_func():
        value_dep()  # Take a reactive dependency on value_dep
        nonlocal value_invocations
        value_invocations += 1

    mock_time = MockTime()
    with mock_time():
        # Poll func is invoked once during @poll(), to seed the underlying reactive val
        assert (poll_invocations, value_invocations) == (1, 0)

        await flush()

        # The observer that updates poll has executed once.
        # @poll returns a lazy Calc, so value hasn't been invoked yet.
        assert (poll_invocations, value_invocations) == (2, 0)

        @Effect()
        def _():
            value_func()

        await flush()
        assert (poll_invocations, value_invocations) == (2, 1)

        await flush()
        assert (poll_invocations, value_invocations) == (2, 1)

        await mock_time.advance_time(1.01)
        # poll_invocations advances without a flush() because invalidate_later itself
        # invokes flush()
        assert (poll_invocations, value_invocations) == (3, 1)
        await flush()
        assert (poll_invocations, value_invocations) == (3, 1)

        # Now change value
        poll_return1 += 1
        await flush()
        # Nothing changes because no time has passed, poll() has not tried again
        assert (poll_invocations, value_invocations) == (3, 1)
        await mock_time.advance_time(1.01)
        assert (poll_invocations, value_invocations) == (4, 2)

        # When a reactive dependency of poll_func invalidates, there's no need to wait
        # until the next poll
        with isolate():
            poll_return2.set(poll_return2() + 1)
        await flush()
        assert (poll_invocations, value_invocations) == (5, 3)

        # When a reactive dependency of value_func invalidates, there's no need to wait
        # until the next poll
        with isolate():
            value_dep.set(value_dep() + 1)
        await flush()
        assert (poll_invocations, value_invocations) == (5, 4)

        await mock_time.advance_time(1.01)
        assert (poll_invocations, value_invocations) == (6, 4)


tmpfile = tempfile.NamedTemporaryFile()


@pytest.mark.asyncio
async def test_file_reader():
    invocations = 0

    tmpfile.write("hello\n".encode())
    tmpfile.flush()

    mock_time = MockTime()
    with mock_time():

        @file_reader(tmpfile.name)
        def read_file():
            with open(tmpfile.name, "r") as f:
                nonlocal invocations
                invocations += 1
                return f.read()

        with isolate():
            assert invocations == 0
            await flush()

            assert read_file() == "hello\n"
            assert invocations == 1
            # Advancing time without a write does nothing
            await mock_time.advance_time(1.01)
            assert read_file() == "hello\n"
            assert invocations == 1

            tmpfile.write("goodbye\n".encode())
            tmpfile.flush()
            # The file's been updated, but we haven't looked yet
            assert read_file() == "hello\n"

            await mock_time.advance_time(1.01)

            assert read_file() == "hello\ngoodbye\n"
            assert invocations == 2
