from contextlib import asynccontextmanager
from typing import AsyncIterable, Iterable, Literal, Union

from htmltools import css

from .. import _utils, reactive
from .._docstring import add_example
from .._typing_extensions import TypedDict
from ..session import require_active_session
from ..types import NotifyException
from ..ui.css import CssUnit, as_css_unit
from . import Tag
from ._html_deps_py_shiny import markdown_stream_dependency

__all__ = (
    "markdown_stream_ui",
    "MarkdownStream",
)

StreamingContentType = Literal[
    "markdown",
    "html",
    "semi-markdown",
    "text",
]


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
    on_error
        How to handle errors that occur while streaming. When `"unhandled"`,
        the app will stop running when an error occurs. Otherwise, a notification
        is displayed to the user and the app continues to run.

        * `"auto"`: Sanitize the error message if the app is set to sanitize errors,
          otherwise display the actual error message.
        * `"actual"`: Display the actual error message to the user.
        * `"sanitize"`: Sanitize the error message before displaying it to the user.
        * `"unhandled"`: Do not display any error message to the user.

    Note
    ----
    Markdown is parsed on the client via `marked.js`. Consider using :func:`~shiny.ui.markdown`
    for server-side rendering of markdown content.
    """

    def __init__(
        self,
        id: str,
        *,
        on_error: Literal["auto", "actual", "sanitize", "unhandled"] = "auto",
    ):
        self.id = id
        # TODO: remove the `None` when this PR lands:
        # https://github.com/posit-dev/py-shiny/pull/793/files
        self._session = require_active_session(None)

        # Default to sanitizing until we know the app isn't sanitizing errors
        if on_error == "auto":
            on_error = "sanitize"
            app = self._session.app
            if app is not None and not app.sanitize_errors:  # type: ignore
                on_error = "actual"

        self.on_error = on_error

    def ui(
        self,
        *,
        content: str = "",
        content_type: StreamingContentType = "markdown",
        auto_scroll: bool = True,
        width: CssUnit = "100%",
        height: CssUnit = "auto",
    ) -> Tag:
        """
        Get the UI element for this markdown stream.

        This method is only relevant for Shiny Express. In Shiny Core, use
        :func:`~shiny.ui.output_markdown_stream` for placing the markdown stream
        in the UI.

        Parameters
        ----------
        content
            Some content to display before any streaming occurs.
        content_type
            The content type. Default is "markdown" (specifically, CommonMark).
            Other supported options are:
            - `"html"`: for rendering HTML content.
            - `"text"`: for plain text.
            - `"semi-markdown"`: for rendering markdown, but with HTML tags escaped.
        auto_scroll
            Whether to automatically scroll to the bottom of a scrollable container
            when new content is added. Default is True.
        width
            The width of the markdown stream container.
        height
            The height of the markdown stream container.

        Returns
        -------
        Tag
            The UI element for this markdown stream.
        """
        return markdown_stream_ui(
            self.id,
            content=content,
            content_type=content_type,
            auto_scroll=auto_scroll,
            width=width,
            height=height,
        )

    async def stream(
        self,
        content: Iterable[str] | AsyncIterable[str],
        clear: bool = True,
    ):
        """
        Stream content into the markdown stream.

        Parameters
        ----------
        content
            The content to stream. This can be any iterable of strings, such as a list,
            generator, or file-like object.
        clear
            Whether to clear the existing content before streaming the new content.
        """

        content = _utils.wrap_async_iterable(content)

        @reactive.extended_task
        async def _task():
            if clear:
                await self._send_content_message("", "replace")

            result = ""
            async with self._streaming_dot():
                async for c in content:
                    result += c
                    await self._send_content_message(c, "append")

            return result

        _task()

        # Since the task runs in the background (outside/beyond the current context,
        # if any), we need to manually raise any exceptions that occur
        @reactive.effect
        async def _handle_error():
            e = _task.error()
            if e:
                await self._raise_exception(e)
            _handle_error.destroy()  # type: ignore

        return _task

    async def clear(self):
        """
        Clear the content of the markdown stream.
        """
        return await self.stream([], clear=True)

    @asynccontextmanager
    async def _streaming_dot(self):
        await self._send_stream_message(True)
        try:
            yield
        finally:
            await self._send_stream_message(False)

    async def _send_content_message(
        self,
        content: str,
        operation: Literal["append", "replace"],
    ):
        msg: ContentMessage = {
            "id": self.id,
            "content": content,
            "operation": operation,
        }
        await self._send_custom_message(msg)

    async def _send_stream_message(self, is_streaming: bool):
        msg: isStreamingMessage = {
            "id": self.id,
            "isStreaming": is_streaming,
        }
        await self._send_custom_message(msg)

    async def _send_custom_message(
        self, msg: Union[ContentMessage, isStreamingMessage]
    ):
        if self._session.is_stub_session():
            return
        await self._session.send_custom_message("shinyMarkdownStreamMessage", {**msg})

    async def _raise_exception(self, e: BaseException):
        if self.on_error == "unhandled":
            raise e
        else:
            sanitize = self.on_error == "sanitize"
            msg = f"Error in MarkdownStream('{self.id}'): {str(e)}"
            raise NotifyException(msg, sanitize=sanitize) from e


@add_example()
def markdown_stream_ui(
    id: str,
    *,
    content: str = "",
    content_type: StreamingContentType = "markdown",
    auto_scroll: bool = True,
    width: CssUnit = "100%",
    height: CssUnit = "auto",
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
        Some content to display before any streaming occurs.
    content_type
        The content type. Default is "markdown" (specifically, CommonMark).
        Other supported options are:
        - `"html"`: for rendering HTML content.
        - `"text"`: for plain text.
        - `"semi-markdown"`: for rendering markdown, but with HTML tags escaped.
    auto_scroll
        Whether to automatically scroll to the bottom of a scrollable container
        when new content is added. Default is True.
    width
        The width of the markdown stream container.
    height
        The height of the markdown stream container.
    """
    return Tag(
        "shiny-markdown-stream",
        markdown_stream_dependency(),
        {
            "style": css(
                width=as_css_unit(width),
                height=as_css_unit(height),
            ),
            "content-type": content_type,
            "auto-scroll": "" if auto_scroll else None,
        },
        id=id,
        content=content,
    )
