"""
OpenTelemetry Download Span Instrumentation

Tests cover:
- shiny_otel_span_stream() helper: chunk passthrough, span attributes, status codes,
  error recording, and level gating
- Download handler OTel integration: file response path, async streaming path,
  sync streaming path (these will fail until the handler is instrumented)
"""

import os
from pathlib import Path
from typing import AsyncIterable, AsyncIterator, Iterator, Mapping, Tuple, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode

from shiny._namespaces import Root
from shiny.otel._collect import OtelCollectLevel
from shiny.otel._span_wrappers import shiny_otel_span_stream
from shiny.session._session import DownloadInfo

from .otel_helpers import get_exported_spans, patch_otel_tracing_state

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _collect_chunks(stream: AsyncIterator[bytes]) -> list[bytes]:
    """Consume an async iterator into a list."""
    result: list[bytes] = []
    async for chunk in stream:
        result.append(chunk)
    return result


async def _async_byte_iter(*chunks: bytes) -> AsyncIterator[bytes]:
    """Create a simple async iterator from byte chunks."""
    for chunk in chunks:
        yield chunk


async def _async_byte_iter_with_error(*chunks: bytes) -> AsyncIterator[bytes]:
    """Yield chunks then raise ValueError."""
    for chunk in chunks:
        yield chunk
    raise ValueError("disk read error")


# ---------------------------------------------------------------------------
# TestSpanStream — direct tests for shiny_otel_span_stream()
# ---------------------------------------------------------------------------


class TestSpanStream:
    """Tests for shiny_otel_span_stream() helper."""

    @pytest.mark.asyncio
    async def test_yields_all_chunks(
        self,
        otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter],
    ):
        """All chunks from the inner iterable are yielded unchanged."""
        _ = otel_tracer_provider  # ensure exporter is cleared between tests
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                inner = _async_byte_iter(b"hello", b" ", b"world")
                stream = shiny_otel_span_stream(
                    "download",
                    inner,
                    infer_session_id=True,
                    attributes={"session.id": "s1"},
                )
                chunks = await _collect_chunks(stream)

        assert chunks == [b"hello", b" ", b"world"]

    @pytest.mark.asyncio
    async def test_span_name_and_attributes(
        self,
        otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter],
    ):
        """Span is named 'download' and carries the provided attributes."""
        provider, exporter = otel_tracer_provider
        attrs = {
            "session.id": "abc123",
            "download.id": "my_file",
            "download.filename": "report.csv",
        }
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                inner = _async_byte_iter(b"data")
                stream = shiny_otel_span_stream(
                    "download",
                    inner,
                    infer_session_id=True,
                    attributes=attrs,
                )
                await _collect_chunks(stream)

        spans = get_exported_spans(provider, exporter)
        download_spans = [s for s in spans if s.name == "download"]
        assert len(download_spans) == 1

        span = download_spans[0]
        assert span.attributes is not None
        assert span.attributes["session.id"] == "abc123"
        assert span.attributes["download.id"] == "my_file"
        assert span.attributes["download.filename"] == "report.csv"

    @pytest.mark.asyncio
    async def test_span_ok_status_on_success(
        self,
        otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter],
    ):
        """Span has OK status after the stream is fully consumed."""
        provider, exporter = otel_tracer_provider
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                inner = _async_byte_iter(b"ok")
                stream = shiny_otel_span_stream(
                    "download", inner, infer_session_id=True
                )
                await _collect_chunks(stream)

        spans = get_exported_spans(provider, exporter)
        download_spans = [s for s in spans if s.name == "download"]
        assert len(download_spans) == 1
        assert download_spans[0].status.status_code == StatusCode.OK

    @pytest.mark.asyncio
    async def test_span_error_status_on_exception(
        self,
        otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter],
    ):
        """Span records ERROR status and an exception event when the inner stream fails."""
        provider, exporter = otel_tracer_provider
        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                inner = _async_byte_iter_with_error(b"partial")
                stream = shiny_otel_span_stream(
                    "download", inner, infer_session_id=True
                )
                with pytest.raises(ValueError, match="disk read error"):
                    await _collect_chunks(stream)

        spans = get_exported_spans(provider, exporter)
        download_spans = [s for s in spans if s.name == "download"]
        assert len(download_spans) == 1

        span = download_spans[0]
        assert span.status.status_code == StatusCode.ERROR
        assert len(span.events) == 1
        assert span.events[0].name == "exception"

    @pytest.mark.asyncio
    async def test_no_span_below_required_level(
        self,
        otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter],
    ):
        """No span is created when the collect level is below the required level."""
        provider, exporter = otel_tracer_provider
        with patch_otel_tracing_state(tracing_enabled=True):
            # SESSION (1) < REACTIVITY (3), so the span should be skipped
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "session"}):
                inner = _async_byte_iter(b"data")
                stream = shiny_otel_span_stream(
                    "download",
                    inner,
                    infer_session_id=True,
                    required_level=OtelCollectLevel.REACTIVITY,
                )
                chunks = await _collect_chunks(stream)

        # Data still passes through
        assert chunks == [b"data"]

        # But no download span was created
        spans = get_exported_spans(provider, exporter)
        download_spans = [s for s in spans if s.name == "download"]
        assert len(download_spans) == 0

    @pytest.mark.asyncio
    async def test_no_span_when_tracing_disabled(
        self,
        otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter],
    ):
        """Data passes through but no span is created when tracing is disabled."""
        provider, exporter = otel_tracer_provider
        with patch_otel_tracing_state(tracing_enabled=False):
            inner = _async_byte_iter(b"hello", b"world")
            stream = shiny_otel_span_stream(
                "download",
                inner,
                infer_session_id=True,
                attributes={"session.id": "s1"},
            )
            chunks = await _collect_chunks(stream)

        # Data passes through unchanged
        assert chunks == [b"hello", b"world"]

        # No spans created
        spans = get_exported_spans(provider, exporter)
        download_spans = [s for s in spans if s.name == "download"]
        assert len(download_spans) == 0


# ---------------------------------------------------------------------------
# TestDownloadHandlerSpans — tests for OTel integration in the download
# handler (will fail until Task 3 instruments the handler)
# ---------------------------------------------------------------------------


class TestDownloadHandlerSpans:
    """
    Tests that the download handler in AppSession._handle_request_impl calls
    the appropriate OTel span helpers.

    These tests will FAIL until the download handler is instrumented with
    shiny_otel_span / shiny_otel_span_stream calls.
    """

    @pytest.mark.asyncio
    async def test_file_response_path_calls_shiny_otel_span(self, tmp_path: Path):
        """
        File-response download (handler returns a path string) should call
        shiny_otel_span with name='download' and appropriate attributes.
        """
        report_csv = tmp_path / "report.csv"
        report_csv.write_text("col1,col2\n1,2\n")

        mock_session = MagicMock()
        mock_session.id = "test-session-id"
        mock_session.ns = Root
        mock_session._downloads = {
            "my_file": DownloadInfo(
                filename="report.csv",
                content_type="text/csv",
                handler=lambda: str(report_csv),
                encoding="utf-8",
            )
        }
        mock_session._debug = False

        # Build a mock GET request
        mock_request = MagicMock()
        mock_request.method = "GET"

        with patch_otel_tracing_state(tracing_enabled=True):
            with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
                with patch("shiny.session._session.shiny_otel_span") as mock_span:
                    # Configure mock as async context manager
                    mock_span.return_value.__aenter__ = AsyncMock(return_value=None)
                    mock_span.return_value.__aexit__ = AsyncMock(return_value=None)

                    # Call the handler code path directly
                    from shiny.session._session import AppSession

                    await AppSession._handle_request_impl(
                        mock_session, mock_request, "download", "my_file"
                    )

                    # Verify shiny_otel_span was called for the download
                    mock_span.assert_called_once()
            call_args = mock_span.call_args
            assert call_args[0][0] == "download my_file"
            assert call_args[1]["required_level"] == OtelCollectLevel.REACTIVITY
            raw_attrs = call_args[1]["attributes"]
            # Attributes may be a callable; resolve if needed
            resolved_attrs = cast(
                Mapping[str, object], raw_attrs() if callable(raw_attrs) else raw_attrs
            )
            assert "download.id" in resolved_attrs
            assert "download.filename" in resolved_attrs

    @pytest.mark.asyncio
    async def test_async_streaming_path_calls_shiny_otel_span_stream(self):
        """
        Async-generator download handler should call shiny_otel_span_stream
        with name='download' and required_level=REACTIVITY.
        """

        async def async_download_handler() -> AsyncIterator[bytes]:
            yield b"chunk1"
            yield b"chunk2"

        mock_session = MagicMock()
        mock_session.id = "test-session-id"
        mock_session.ns = Root
        mock_session._downloads = {
            "stream_file": DownloadInfo(
                filename="data.bin",
                content_type="application/octet-stream",
                handler=async_download_handler,
                encoding="utf-8",
            )
        }
        mock_session._debug = False

        mock_request = MagicMock()
        mock_request.method = "GET"

        def _passthrough(
            name: str, inner: AsyncIterable[bytes], **kw: object
        ) -> AsyncIterable[bytes]:
            return inner

        with patch(
            "shiny.session._session.shiny_otel_span_stream", create=True
        ) as mock_stream_span:
            # Return the inner iterable unchanged so the response can be created
            mock_stream_span.side_effect = _passthrough

            from shiny.session._session import AppSession

            await AppSession._handle_request_impl(
                mock_session, mock_request, "download", "stream_file"
            )

            mock_stream_span.assert_called_once()
            call_args = mock_stream_span.call_args
            assert call_args[0][0] == "download stream_file"
            assert call_args[1]["required_level"] == OtelCollectLevel.REACTIVITY

    @pytest.mark.asyncio
    async def test_sync_streaming_path_calls_shiny_otel_span_stream(self):
        """
        Sync-generator download handler should call shiny_otel_span_stream
        with name='download' and required_level=REACTIVITY.
        """

        def sync_download_handler() -> Iterator[bytes]:
            yield b"chunk1"
            yield b"chunk2"

        mock_session = MagicMock()
        mock_session.id = "test-session-id"
        mock_session.ns = Root
        mock_session._downloads = {
            "sync_file": DownloadInfo(
                filename="data.bin",
                content_type="application/octet-stream",
                handler=sync_download_handler,
                encoding="utf-8",
            )
        }
        mock_session._debug = False

        mock_request = MagicMock()
        mock_request.method = "GET"

        def _passthrough(
            name: str, inner: AsyncIterable[bytes], **kw: object
        ) -> AsyncIterable[bytes]:
            return inner

        with patch(
            "shiny.session._session.shiny_otel_span_stream", create=True
        ) as mock_stream_span:
            mock_stream_span.side_effect = _passthrough

            from shiny.session._session import AppSession

            await AppSession._handle_request_impl(
                mock_session, mock_request, "download", "sync_file"
            )

            mock_stream_span.assert_called_once()
            call_args = mock_stream_span.call_args
            assert call_args[0][0] == "download sync_file"
            assert call_args[1]["required_level"] == OtelCollectLevel.REACTIVITY
