from contextlib import asynccontextmanager
from typing import AsyncIterable, Iterable, Literal, Union

from htmltools import css

from .. import _utils, reactive
from .._docstring import add_example
from .._namespaces import resolve_id
from .._typing_extensions import TypedDict
from ..session import require_active_session, session_context
from ..types import NotifyException
from ..ui.css import CssUnit, as_css_unit
from . import Tag
from ._html_deps_py_shiny import markdown_stream_dependency

__all__ = (
    "output_markdown_stream",
    "MarkdownStream",
    "ExpressMarkdownStream",
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


@add_example("app-core.py")
class MarkdownStream:
    """
    A component for streaming markdown or HTML content.

    Parameters
    ----------
    id
        A unique identifier for this `MarkdownStream`. In Shiny Core, make sure this id
        matches a corresponding :func:`~shiny.ui.output_markdown_stream` call in the app's
        UI.
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
    Markdown is parsed on the client via `marked.js`. Consider using
    :func:`~shiny.ui.markdown` for server-side rendering of markdown content.
    """

    def __init__(
        self,
        id: str,
        *,
        on_error: Literal["auto", "actual", "sanitize", "unhandled"] = "auto",
    ):
        self.id = resolve_id(id)
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

        with session_context(self._session):
            self._latest_stream: reactive.Value[
                Union[reactive.ExtendedTask[[], str], None]
            ] = reactive.Value(None)

    async def stream(
        self,
        content: Union[Iterable[str], AsyncIterable[str]],
        clear: bool = True,
    ):
        """
        Send a stream of content to the UI.

        Stream content into the relevant UI element.

        Parameters
        ----------
        content
            The content to stream. This can be a Iterable or an AsyncIterable of strings.
            Note that this includes synchronous and asynchronous generators, which is
            a useful way to stream content in as it arrives (e.g. from a LLM).
        clear
            Whether to clear the existing content before streaming the new content.

        Note
        ----
        If you already have the content available as a string, you can do
        `.stream([content])` to set the content.

        Returns
        -------
        :
            An extended task that represents the streaming task. The `.result()` method
            of the task can be called in a reactive context to get the final state of the
            stream.
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

    def get_latest_stream_result(self) -> Union[str, None]:
        """
        Reactively read the latest stream result.

        This method reads a reactive value containing the result of the latest
        `.stream()`. Therefore, this method must be called in a reactive context (e.g.,
        a render function, a :func:`~shiny.reactive.calc`, or a
        :func:`~shiny.reactive.effect`).

        Returns
        -------
        :
            The result of the latest stream (a string).

        Raises
        ------
        :
            A silent exception if no stream has completed yet.
        """
        stream = self._latest_stream()
        if stream is None:
            from .. import req

            req(False)
        else:
            return stream.result()

    async def clear(self):
        """
        Empty the UI element of the `MarkdownStream`.
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


@add_example("app-express.py")
class ExpressMarkdownStream(MarkdownStream):
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
        Create a UI element for this `MarkdownStream`.

        Parameters
        ----------
        content
            Content to display when the UI element is first rendered.
        content_type
            The content type. Default is `"markdown"` (specifically, CommonMark).
            Other supported options are:
            - `"html"`: for rendering HTML content.
            - `"text"`: for plain text.
            - `"semi-markdown"`: for rendering markdown, but with HTML tags escaped.
        auto_scroll
            Whether to automatically scroll to the bottom of a scrollable container
            when new content is added. Default is `True`.
        width
            The width of the UI element.
        height
            The height of the UI element.

        Returns
        -------
        Tag
            A UI element for locating the `MarkdownStream` in the app.
        """
        return output_markdown_stream(
            self.id,
            content=content,
            content_type=content_type,
            auto_scroll=auto_scroll,
            width=width,
            height=height,
        )


@add_example(ex_dir="../api-examples/MarkdownStream")
def output_markdown_stream(
    id: str,
    *,
    content: str = "",
    content_type: StreamingContentType = "markdown",
    auto_scroll: bool = True,
    width: CssUnit = "100%",
    height: CssUnit = "auto",
) -> Tag:
    """
    Create a UI element for a :class:`~shiny.ui.MarkdownStream`.

    This function is only relevant for Shiny Core. In Shiny Express, use
    :meth:`~shiny.express.ui.MarkdownStream.ui` to create the UI element.

    Parameters
    ----------
    id
        A unique identifier for the UI element. This id should match the id of the
        :class:`~shiny.ui.MarkdownStream` instance.
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
        The width of the UI element.
    height
        The height of the UI element.
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
        id=resolve_id(id),
        content=content,
    )
