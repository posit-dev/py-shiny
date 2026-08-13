"""
Flushing reactives for work that starts outside the WebSocket message cycle
(posit-dev/py-shiny#1785).

Downloads and dynamic routes are served over plain HTTP requests, and
`session.send_input_message()` can be called from anywhere. None of those is a
client message, and the session's message loop is what flushes the reactive
graph, so anything they invalidate used to sit in the pending-flush queue until
an unrelated client message happened to arrive.

`Session._request_flush()` now wakes the message loop, so the flush happens on
the session's own task, in order with client messages.
"""

from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from copy import deepcopy
from pathlib import Path
from typing import Any, AsyncGenerator, AsyncIterable, Callable, Iterable, cast

import pytest
from starlette.requests import Request

# Not `shiny.http_staticfiles.FileResponse`, which is a stripped-down class under
# wasm; tests always run in native mode, where starlette's is used.
from starlette.responses import FileResponse, HTMLResponse, StreamingResponse

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny._connection import MockConnection
from shiny.session._session import AppSession

DOWNLOAD_ID = "download"
# Init message that marks the `count_text` output as visible, so that it renders.
INIT_MESSAGE = json.dumps(
    {
        "method": "init",
        "data": {".clientdata_output_count_text_hidden": False},
    }
)


def _request(action: str, subpath: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "headers": [],
            "query_string": b"",
            "path": f"/session/x/{action}/{subpath}",
        }
    )


async def _read_body(response: object) -> bytes:
    """Consume the body of a download response, the way an HTTP client would."""
    if isinstance(response, StreamingResponse):
        chunks: list[bytes] = []
        async for chunk in response.body_iterator:
            chunks.append(chunk.encode() if isinstance(chunk, str) else bytes(chunk))
        return b"".join(chunks)
    if isinstance(response, FileResponse):
        return Path(response.path).read_bytes()
    raise AssertionError(f"Unexpected download response: {response!r}")


async def _wait_for(predicate: Callable[[], bool], what: str) -> None:
    # The session runs in a separate task; yield to it until it catches up.
    for _ in range(1000):
        if predicate():
            return
        await asyncio.sleep(0)
    raise AssertionError(f"Timed out waiting for {what}")


class Harness:
    """A running session, plus the plumbing needed to observe what it sends."""

    def __init__(
        self,
        session: AppSession,
        conn: MockConnection,
        sent: list[dict[str, object]],
    ) -> None:
        self.session = session
        self.conn = conn
        self.sent = sent

    async def request(self, action: str, subpath: str) -> object:
        return await self.session._handle_request(
            _request(action=action, subpath=subpath),
            action=action,
            subpath=subpath,
        )

    async def download(self) -> object:
        return await self.request(action="download", subpath=DOWNLOAD_ID)

    async def settle(self) -> None:
        """
        Let the session's message loop wake up and flush.

        The flush is deliberately not awaited by whoever requested it, so tests
        have to yield to the loop's task. Nothing here does real I/O, so
        repeatedly ceding control is enough.
        """
        for _ in range(100):
            await asyncio.sleep(0)

    @property
    def values(self) -> dict[str, Any]:
        """Output values pushed to the client since the session went idle."""
        values: dict[str, Any] = {}
        for message in self.sent:
            values.update(message.get("values") or {})  # type: ignore[union-attr]
        return values

    @property
    def input_messages(self) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        for message in self.sent:
            messages.extend(message.get("inputMessages") or [])  # type: ignore[union-attr]
        return messages


@asynccontextmanager
async def _running_session(
    server: Callable[[Inputs, Outputs, Session], None],
) -> AsyncGenerator[Harness, None]:
    """
    Run `server` in a real session, parked and idle, ready to serve a request.

    Idle -- i.e. parked waiting for the next client message -- is the state a
    real session is in when the browser asks for a download.
    """
    conn = MockConnection()
    session = App(ui.TagList(), server)._create_session(conn)

    # Record everything the session pushes to the client.
    sent: list[dict[str, object]] = []
    send_message = session._send_message

    async def record_message(message: dict[str, object]) -> None:
        # Copy: `_flush()` sends the (mutable) outbound message queues, then
        # clears them.
        sent.append(deepcopy(message))
        await send_message(message)

    session._send_message = record_message  # type: ignore[method-assign]

    # Count how many times the loop asks the connection for a message; the 2nd
    # time means `init` (and its reactive flush) has been fully processed.
    n_receives = 0
    receive = conn.receive

    async def counted_receive() -> str:
        nonlocal n_receives
        n_receives += 1
        return await receive()

    conn.receive = counted_receive  # type: ignore[method-assign]

    run_task = asyncio.create_task(session._run())
    try:
        conn.cause_receive(INIT_MESSAGE)
        await _wait_for(lambda: n_receives >= 2, "the session to become idle")
        sent.clear()
        yield Harness(session, conn, sent)
    finally:
        # Unconditionally, so that a failing assertion above does not leave
        # `session._run()` parked with its reactive callbacks still registered
        # on the global environment.
        conn.cause_disconnect()
        await run_task


def _counting_server(
    seen: list[int],
    download: Callable[[reactive.Value[int]], Any],
) -> Callable[[Inputs, Outputs, Session], None]:
    """An app with a value, an effect and an output watching it, and a download."""

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        n_downloads = reactive.value(0)

        @reactive.effect
        def _():
            seen.append(n_downloads.get())

        @render.text
        def count_text():
            return f"downloads: {n_downloads.get()}"

        download(n_downloads)

    return server


@pytest.mark.asyncio
async def test_sync_generator_download_updates_reactives():
    """A `reactive.Value` set in a sync generator download handler is flushed."""
    seen: list[int] = []

    def make_download(n_downloads: reactive.Value[int]) -> None:
        @render.download_button(filename="data.csv")
        def download() -> Iterable[bytes]:
            n_downloads.set(n_downloads.get() + 1)
            yield b"a,b\n1,2\n"

    async with _running_session(_counting_server(seen, make_download)) as h:
        body = await _read_body(await h.download())
        await h.settle()

        assert body == b"a,b\n1,2\n"
        # The effect re-ran with the new value, without any further client input.
        assert seen == [0, 1]
        # ...and the new output value was pushed to the client.
        assert h.values.get("count_text") == "downloads: 1"
        # ...and the session is no longer telling the client it is busy.
        assert h.session._busy_count == 0


@pytest.mark.asyncio
async def test_async_generator_download_updates_reactives():
    """A `reactive.Value` set in an async generator download handler is flushed."""
    seen: list[int] = []

    def make_download(n_downloads: reactive.Value[int]) -> None:
        @render.download_button(filename="data.csv")
        async def download() -> AsyncIterable[bytes]:
            n_downloads.set(n_downloads.get() + 1)
            yield b"a,b\n1,2\n"

    async with _running_session(_counting_server(seen, make_download)) as h:
        body = await _read_body(await h.download())
        await h.settle()

        assert body == b"a,b\n1,2\n"
        assert seen == [0, 1]
        assert h.values.get("count_text") == "downloads: 1"
        assert h.session._busy_count == 0


@pytest.mark.asyncio
async def test_file_path_download_updates_reactives(tmp_path: Path):
    """A `reactive.Value` set in a file-path download handler is flushed."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b\n1,2\n")
    seen: list[int] = []

    def make_download(n_downloads: reactive.Value[int]) -> None:
        @render.download_button()
        def download() -> str:
            n_downloads.set(n_downloads.get() + 1)
            return str(csv_file)

    async with _running_session(_counting_server(seen, make_download)) as h:
        body = await _read_body(await h.download())
        await h.settle()

        assert body == b"a,b\n1,2\n"
        assert seen == [0, 1]
        assert h.values.get("count_text") == "downloads: 1"
        assert h.session._busy_count == 0


@pytest.mark.asyncio
async def test_download_flush_waits_for_the_stream_to_finish():
    """
    The flush happens after the download's contents are generated, not before.

    A generator handler's body does not start running until the response is
    streamed, so flushing when the handler is merely *called* would miss any
    reactive value it sets.
    """
    seen: list[int] = []

    def make_download(n_chunks: reactive.Value[int]) -> None:
        @render.download_button(filename="data.txt")
        def download() -> Iterable[bytes]:
            for i in range(3):
                n_chunks.set(i + 1)
                yield b"x"

    async with _running_session(_counting_server(seen, make_download)) as h:
        body = await _read_body(await h.download())
        await h.settle()

        assert body == b"xxx"
        # One flush after the whole stream, not one per chunk.
        assert seen == [0, 3]
        assert h.values.get("count_text") == "downloads: 3"


@pytest.mark.asyncio
async def test_download_flushes_when_the_handler_raises():
    """
    A handler that blows up mid-stream still flushes what it managed to set.

    Otherwise the invalidated effects never re-run, their busy-count increments
    are never balanced, and the client's "recalculating" indicator stays on.
    """
    seen: list[int] = []

    def make_download(n_downloads: reactive.Value[int]) -> None:
        @render.download_button(filename="data.csv")
        def download() -> Iterable[bytes]:
            n_downloads.set(n_downloads.get() + 1)
            yield b"partial"
            raise RuntimeError("boom")

    async with _running_session(_counting_server(seen, make_download)) as h:
        with pytest.raises(RuntimeError, match="boom"):
            await _read_body(await h.download())
        await h.settle()

        assert seen == [0, 1]
        assert h.values.get("count_text") == "downloads: 1"
        assert h.session._busy_count == 0


@pytest.mark.asyncio
async def test_download_flushes_when_the_client_aborts():
    """
    A download the client walks away from still flushes what the handler set.

    Starlette closes the body iterator when the client disconnects, which throws
    `GeneratorExit` in at the `yield`, skipping the rest of the generator body.
    Only a `finally` still runs.
    """
    seen: list[int] = []

    def make_download(n_downloads: reactive.Value[int]) -> None:
        @render.download_button(filename="data.csv")
        def download() -> Iterable[bytes]:
            n_downloads.set(n_downloads.get() + 1)
            yield b"first"
            yield b"second"

    async with _running_session(_counting_server(seen, make_download)) as h:
        response = await h.download()
        assert isinstance(response, StreamingResponse)

        # Read one chunk, then hang up, the way an aborted download does.
        iterator = cast("AsyncGenerator[bytes, None]", response.body_iterator)
        assert await iterator.__anext__() == b"first"
        await iterator.aclose()

        await h.settle()

        assert seen == [0, 1]
        assert h.values.get("count_text") == "downloads: 1"
        assert h.session._busy_count == 0


@pytest.mark.asyncio
async def test_dynamic_route_updates_reactives():
    """A dynamic route is served out-of-band too, so it needs the same flush."""
    seen: list[int] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        n_hits = reactive.value(0)

        @reactive.effect
        def _():
            seen.append(n_hits.get())

        @render.text
        def count_text():
            return f"downloads: {n_hits.get()}"

        def handler(request: Request) -> HTMLResponse:
            n_hits.set(n_hits.get() + 1)
            return HTMLResponse("ok")

        session.dynamic_route("thing", handler)

    async with _running_session(server) as h:
        response = await h.request(action="dynamic_route", subpath="thing")
        assert isinstance(response, HTMLResponse)

        await h.settle()

        assert seen == [0, 1]
        assert h.values.get("count_text") == "downloads: 1"
        assert h.session._busy_count == 0


@pytest.mark.asyncio
async def test_send_input_message_outside_the_message_cycle_is_delivered():
    """
    `send_input_message()` queues a message and calls `_request_flush()`.

    Called from outside the message cycle -- from an `on_ended` callback, a
    background task, or just directly -- the queued message needs the loop to
    wake up, or it sits there until the client happens to say something.
    """

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @render.text
        def count_text():
            return "hi"

    async with _running_session(server) as h:
        h.session.send_input_message("slider", {"value": 42})
        await h.settle()

        assert h.input_messages == [{"id": "slider", "message": {"value": 42}}]


@pytest.mark.asyncio
async def test_a_flush_request_does_not_swallow_the_next_client_message():
    """
    Waking the loop for a flush must not lose the pending `receive()`.

    The loop now waits on a client message *or* a flush request, so a flush that
    wins the race has to leave the in-flight receive alone. Getting this wrong
    drops or double-processes client input, which is far worse than the bug
    being fixed.
    """
    seen: list[int] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _():
            # Silent until the client sends `n`, so `seen` records exactly the
            # updates the message loop actually processed.
            seen.append(input.n())

        @render.text
        def count_text():
            return "hi"

    async with _running_session(server) as h:
        # Wake the loop for a flush while it is parked on `receive()`.
        h.session._request_flush()
        await h.settle()
        assert seen == []

        # A client message sent afterwards is still processed normally.
        h.conn.cause_receive(json.dumps({"method": "update", "data": {"n": 7}}))
        await _wait_for(lambda: seen == [7], "the update message to be processed")


@pytest.mark.asyncio
async def test_repeated_downloads_each_flush():
    """A second download is flushed too, i.e. the loop keeps waking up."""
    seen: list[int] = []

    def make_download(n_downloads: reactive.Value[int]) -> None:
        @render.download_button(filename="data.csv")
        def download() -> Iterable[bytes]:
            n_downloads.set(n_downloads.get() + 1)
            yield b"x"

    async with _running_session(_counting_server(seen, make_download)) as h:
        await _read_body(await h.download())
        await h.settle()
        await _read_body(await h.download())
        await h.settle()

        assert seen == [0, 1, 2]
        assert h.values.get("count_text") == "downloads: 2"
        assert h.session._busy_count == 0
