"""
Reactivity of download handlers (posit-dev/py-shiny#1785).

A download is served over a plain HTTP request, which happens outside of the
WebSocket message cycle that normally drives reactive flushes. These tests pin
down that a `reactive.Value` which is set inside a download handler takes effect
as soon as the download finishes -- downstream effects re-execute and the new
output values are pushed to the client -- rather than sitting invalidated until
some unrelated client message arrives.
"""

from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, AsyncIterable, Callable, Iterable, NamedTuple

import pytest
from starlette.requests import Request

# Not `shiny.http_staticfiles.FileResponse`, which is a stripped-down class under
# wasm; tests always run in native mode, where starlette's is used.
from starlette.responses import FileResponse, StreamingResponse

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny._connection import MockConnection

# The download id used by every app in this file.
DOWNLOAD_ID = "download"
# Init message that marks the `count_text` output as visible, so that it renders.
INIT_MESSAGE = json.dumps(
    {
        "method": "init",
        "data": {".clientdata_output_count_text_hidden": False},
    }
)


class DownloadResult(NamedTuple):
    body: bytes
    """The bytes an HTTP client would have received."""

    values: dict[str, Any]
    """Output values pushed to the client because of the download."""

    watched: list[int]
    """Snapshot of the caller's `watch` list, taken when the download finished."""


def _download_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "headers": [],
            "query_string": b"",
            "path": f"/session/x/download/{DOWNLOAD_ID}",
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


async def _download(
    server: Callable[[Inputs, Outputs, Session], None],
    watch: list[int],
) -> DownloadResult:
    """
    Run `server` in a real session, then request its download over HTTP.

    The download request is made only once the session is idle (i.e. parked
    waiting for the next client message), which is the state a real session is in
    when the browser asks for a download.
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

    # Count how many times the session's message loop parks on `receive()`; the
    # 2nd time means `init` (and its reactive flush) has been fully processed.
    n_receives = 0
    receive = conn.receive

    async def counted_receive() -> str:
        nonlocal n_receives
        n_receives += 1
        return await receive()

    conn.receive = counted_receive  # type: ignore[method-assign]

    result: list[DownloadResult] = []

    async def mock_client() -> None:
        conn.cause_receive(INIT_MESSAGE)
        await _wait_for(lambda: n_receives >= 2, "the session to become idle")
        sent.clear()

        response = await session._handle_request(
            _download_request(), "download", DOWNLOAD_ID
        )
        body = await _read_body(response)

        values: dict[str, Any] = {}
        for message in sent:
            values.update(message.get("values") or {})  # type: ignore[union-attr]
        result.append(DownloadResult(body, values, list(watch)))

        conn.cause_disconnect()

    await asyncio.gather(mock_client(), session._run())

    return result[0]


@pytest.mark.asyncio
async def test_sync_generator_download_updates_reactives():
    """A `reactive.Value` set in a sync generator download handler is flushed."""
    seen: list[int] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        n_downloads = reactive.value(0)

        @reactive.effect
        def _():
            seen.append(n_downloads.get())

        @render.text
        def count_text():
            return f"downloads: {n_downloads.get()}"

        @render.download_button(filename="data.csv")
        def download() -> Iterable[bytes]:
            n_downloads.set(n_downloads.get() + 1)
            yield b"a,b\n1,2\n"

    result = await _download(server, seen)

    assert result.body == b"a,b\n1,2\n"
    # The effect re-ran with the new value, without any further client input.
    assert result.watched == [0, 1]
    # ...and the new output value was pushed to the client.
    assert result.values.get("count_text") == "downloads: 1"


@pytest.mark.asyncio
async def test_async_generator_download_updates_reactives():
    """A `reactive.Value` set in an async generator download handler is flushed."""
    seen: list[int] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        n_downloads = reactive.value(0)

        @reactive.effect
        def _():
            seen.append(n_downloads.get())

        @render.text
        def count_text():
            return f"downloads: {n_downloads.get()}"

        @render.download_button(filename="data.csv")
        async def download() -> AsyncIterable[bytes]:
            n_downloads.set(n_downloads.get() + 1)
            yield b"a,b\n1,2\n"

    result = await _download(server, seen)

    assert result.body == b"a,b\n1,2\n"
    assert result.watched == [0, 1]
    assert result.values.get("count_text") == "downloads: 1"


@pytest.mark.asyncio
async def test_file_path_download_updates_reactives(tmp_path: Path):
    """A `reactive.Value` set in a file-path download handler is flushed."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b\n1,2\n")
    seen: list[int] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        n_downloads = reactive.value(0)

        @reactive.effect
        def _():
            seen.append(n_downloads.get())

        @render.text
        def count_text():
            return f"downloads: {n_downloads.get()}"

        @render.download_button()
        def download() -> str:
            n_downloads.set(n_downloads.get() + 1)
            return str(csv_file)

    result = await _download(server, seen)

    assert result.body == b"a,b\n1,2\n"
    assert result.watched == [0, 1]
    assert result.values.get("count_text") == "downloads: 1"


@pytest.mark.asyncio
async def test_download_flush_waits_for_the_stream_to_finish():
    """
    The flush happens after the download's contents are generated, not before.

    A generator handler's body does not start running until the response is
    streamed, so flushing when the handler is merely *called* would miss any
    reactive value it sets.
    """
    seen: list[int] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        n_chunks = reactive.value(0)

        @reactive.effect
        def _():
            seen.append(n_chunks.get())

        @render.text
        def count_text():
            return f"chunks: {n_chunks.get()}"

        @render.download_button(filename="data.txt")
        def download() -> Iterable[bytes]:
            for i in range(3):
                n_chunks.set(i + 1)
                yield b"x"

    result = await _download(server, seen)

    assert result.body == b"xxx"
    # One flush after the whole stream, not one per chunk.
    assert result.watched == [0, 3]
    assert result.values.get("count_text") == "chunks: 3"
