from contextlib import contextmanager
from typing import Iterable, Literal

from .. import reactive
from .._docstring import add_example
from .._typing_extensions import TypedDict
from ..session import require_active_session
from . import Tag
from ._html_deps_py_shiny import markdown_stream_dependency

__all__ = (
    "markdown_stream_ui",
    "MarkdownStream",
)

StreamingContentType = Literal["markdown", "semi-markdown", "html", "text"]


class ContentMessage(TypedDict):
    id: str
    content: str
    operation: Literal["append", "replace"]


class isStreamingMessage(TypedDict):
    id: str
    isStreaming: bool


@add_example()
class MarkdownStream:
    """
    Stream markdown (or HTML) content.

    Parameters
    ----------
    id
        A unique identifier for this markdown stream.
    content
        Initial (starting) content.
    content_type
        The content type of the markdown content. Default is "markdown".

    Note
    ----
    Markdown is parsed on the client via `marked.js`. Consider using :func:`~shiny.ui.markdown`
    for server-side rendering of markdown content.
    """

    def __init__(
        self,
        id: str,
        *,
        content: str = "",
        content_type: StreamingContentType = "markdown",
    ):
        self.id = id
        self._content = content
        self._content_type: StreamingContentType = content_type

        # TODO: remove the `None` when this PR lands:
        # https://github.com/posit-dev/py-shiny/pull/793/files
        self._session = require_active_session(None)

    def ui(self) -> Tag:
        """
        Get the UI element for this markdown stream.

        This method is only relevant fpr Shiny Express. In Shiny Core, use
        :func:`~shiny.ui.markdown_stream_ui` for placing the markdown stream
        in the UI.

        Returns
        -------
        Tag
            The UI element for this markdown stream.
        """
        return markdown_stream_ui(self.id, self._content, self._content_type)

    def stream(self, content: Iterable[str], clear: bool = True):
        """
        Stream content into the markdown stream.

        Parameters
        ----------
        clear
            Whether to clear the existing content before streaming the new content.
        """

        @reactive.extended_task
        async def _task():
            if clear:
                self._replace("")
            with self._streaming_dot():
                for c in content:
                    self._append(c)

        _task()

    def update(self, content: str):
        self._replace(content)

    def _append(self, content: str):
        msg: ContentMessage = {
            "id": self.id,
            "content": content,
            "operation": "append",
        }

        self._send_custom_message(msg)

    def _replace(self, content: str):
        msg: ContentMessage = {
            "id": self.id,
            "content": content,
            "operation": "replace",
        }

        self._send_custom_message(msg)

    @contextmanager
    def _streaming_dot(self):
        start: isStreamingMessage = {
            "id": self.id,
            "isStreaming": True,
        }
        self._send_custom_message(start)

        try:
            yield
        finally:
            end: isStreamingMessage = {
                "id": self.id,
                "isStreaming": False,
            }
            self._send_custom_message(end)

    def _send_custom_message(self, msg: ContentMessage | isStreamingMessage):
        if self._session.is_stub_session():
            return
        self._session._send_message_sync(
            {"custom": {"shinyMarkdownStreamMessage": msg}}
        )


def markdown_stream_ui(
    id: str,
    content: str = "",
    content_type: StreamingContentType = "markdown",
) -> Tag:
    """
    Create a UI element for a markdown stream.

    This method is only relevant for Shiny Core. In Shiny Express, use
    :meth:`~shiny.ui.MarkdownStream.ui` to get the UI element for the markdown stream

    Parameters
    ----------
    id
        A unique identifier for this markdown stream.
    content
        Initial (starting) content.
    content_type
        The content type of the markdown content. Default is "markdown".
    """
    return Tag(
        "shiny-markdown-stream",
        markdown_stream_dependency(),
        id=id,
        content=content,
        content_type=content_type,
    )
