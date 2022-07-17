"""Tests for polling-related functionality."""

import os
import tempfile
from enum import Enum
from random import random
from types import TracebackType
from typing import Any, Dict, Callable, Optional, Type, cast

import pytest

from shiny import *
from shiny import _utils
from shiny.reactive import *
from shiny._namespaces import Root

from .mocktime import MockTime


class OnEndedSessionCallbacks:
    """
    A far-too-minimal mock of Session that implements nothing but on_ended. This is
    used so that invalidate_later calls can be cleaned up, otherwise you get warnings
    about pending tasks when pytest completes.

    Eventually we should have a proper mock of Session, then we can retire this.
    """

    ns = Root

    def __init__(self):
        self._on_ended_callbacks = _utils.Callbacks()
        # Unfortunately we have to lie here and say we're a session. Obvously, any
        # attempt to call anything but session.on_ended() will fail.
        self._session_context = session.session_context(cast(Session, self))

    def on_ended(self, fn: Callable[[], None]) -> Callable[[], None]:
        return self._on_ended_callbacks.register(fn)

    def _send_message_sync(self, message: Dict[str, object]) -> None:
        pass

    async def __aenter__(self):
        self._session_context.__enter__()

    async def __aexit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ):
        self._session_context.__exit__(exctype, excinst, exctb)
        self._on_ended_callbacks.invoke()


@pytest.mark.asyncio
async def test_poll():
    async with OnEndedSessionCallbacks():
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


@pytest.mark.asyncio
async def test_poll_errors():
    async with OnEndedSessionCallbacks():

        class Mode(Enum):
            NORMAL = 0
            RAISE = 1
            INCOMPARABLE = 2

        class Incomparable:
            def __eq__(self, other: Any):
                raise ValueError("I refused to be compared to anyone!")

        mock_time = MockTime()
        with mock_time():
            mode = Mode.NORMAL

            def poll_func() -> Any:
                if mode is Mode.NORMAL:
                    return random()
                if mode is Mode.RAISE:
                    raise ValueError("boom")
                if mode is Mode.INCOMPARABLE:
                    return Incomparable()

            @poll(poll_func)
            def bad_poll() -> Any:
                return random()

            invocations = 0

            @Effect()
            def _():
                nonlocal invocations
                invocations += 1
                if mode is Mode.NORMAL:
                    bad_poll()
                if mode is Mode.RAISE:
                    with pytest.raises(ValueError):
                        bad_poll()
                if mode is Mode.INCOMPARABLE:
                    with pytest.raises(TypeError):
                        bad_poll()

            with isolate():
                await flush()
                bad_poll()

                mode = Mode.RAISE
                # Doesn't raise because polling hasn't happened yet
                bad_poll()

                await mock_time.advance_time(1.01)
                await flush()

                with pytest.raises(ValueError):
                    bad_poll()

                mode = Mode.INCOMPARABLE
                await mock_time.advance_time(1.01)
                await flush()

                with pytest.raises(TypeError):
                    bad_poll()

                assert invocations == 3


@pytest.mark.asyncio
async def test_file_reader():
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    try:
        async with OnEndedSessionCallbacks():
            invocations = 0

            tmpfile.write("hello\n".encode())
            tmpfile.flush()
            tmpfile.close()

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

                    with open(tmpfile.name, "a") as f:
                        f.write("goodbye\n")

                    # The file's been updated, but we haven't looked yet
                    assert read_file() == "hello\n"

                    await mock_time.advance_time(1.01)

                    assert read_file() == "hello\ngoodbye\n"
                    assert invocations == 2
    finally:
        os.unlink(tmpfile.name)


@pytest.mark.asyncio
async def test_file_reader_error():
    async with OnEndedSessionCallbacks():

        tmpfile1 = tempfile.NamedTemporaryFile(delete=False)
        mock_time = MockTime()
        with mock_time():

            @file_reader(tmpfile1.name)
            def read_file():
                return True

            with isolate():
                await flush()
                assert read_file() is True
                tmpfile1.close()

                os.unlink(tmpfile1.name)
                await mock_time.advance_time(1.01)
                await flush()

                with pytest.raises(FileNotFoundError):
                    read_file()
