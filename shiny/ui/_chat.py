from __future__ import annotations

import inspect
from contextlib import asynccontextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
    overload,
)
from weakref import WeakValueDictionary

from htmltools import HTML, RenderedHTML, Tag, TagAttrValue, TagChild, TagList, css

from .. import _utils, reactive
from .._deprecated import warn_deprecated
from .._docstring import add_example
from .._utils import CancelCallback, wrap_async
from ..bookmark import BookmarkState, RestoreState
from ..bookmark._types import BookmarkStore
from ..module import ResolvedId, resolve_id
from ..session import get_current_session, require_active_session, session_context
from ..types import MISSING, MISSING_TYPE, Jsonifiable, NotifyException
from ..ui.css import CssUnit, as_css_unit
from ._chat_bookmark import (
    BookmarkCancelCallback,
    ClientWithState,
    get_chatlas_state,
    is_chatlas_chat_client,
    set_chatlas_state,
)
from ._chat_normalize import normalize_message, normalize_message_chunk
from ._chat_provider_types import (
    AnthropicMessage,
    GoogleMessage,
    LangChainMessage,
    OllamaMessage,
    OpenAIMessage,
    ProviderMessage,
    ProviderMessageFormat,
    as_provider_message,
)
from ._chat_tokenizer import TokenEncoding, TokenizersEncoding, get_default_tokenizer
from ._chat_types import ChatMessage, ChatMessageDict, ClientMessage, TransformedMessage
from ._html_deps_py_shiny import chat_deps
from .fill import as_fill_item, as_fillable_container

if TYPE_CHECKING:

    import chatlas

else:
    chatlas = object

__all__ = (
    "Chat",
    "ChatExpress",
    "chat_ui",
    "ChatMessageDict",
)


# TODO: UserInput might need to be a list of dicts if we want to support multiple
# user input content types
TransformUserInput = Callable[[str], Union[str, None]]
TransformUserInputAsync = Callable[[str], Awaitable[Union[str, None]]]
TransformAssistantResponse = Callable[[str], Union[str, HTML, None]]
TransformAssistantResponseAsync = Callable[[str], Awaitable[Union[str, HTML, None]]]
TransformAssistantResponseChunk = Callable[[str, str, bool], Union[str, HTML, None]]
TransformAssistantResponseChunkAsync = Callable[
    [str, str, bool], Awaitable[Union[str, HTML, None]]
]
TransformAssistantResponseFunction = Union[
    TransformAssistantResponse,
    TransformAssistantResponseAsync,
    TransformAssistantResponseChunk,
    TransformAssistantResponseChunkAsync,
]
UserSubmitFunction0 = Union[
    Callable[[], None],
    Callable[[], Awaitable[None]],
]
UserSubmitFunction1 = Union[
    Callable[[str], None],
    Callable[[str], Awaitable[None]],
]
UserSubmitFunction = Union[
    UserSubmitFunction0,
    UserSubmitFunction1,
]

ChunkOption = Literal["start", "end", True, False]

PendingMessage = Tuple[
    Any,
    ChunkOption,
    Literal["append", "replace"],
    Union[str, None],
]


@add_example("app-core.py")
class Chat:
    """
    Create a chat interface.

    A UI component for building conversational interfaces. With it, end users can submit
    messages, which will cause a `.on_user_submit()` callback to run. That callback gets
    passed the user input message, which can be used to generate a response. The
    response can then be appended to the chat using `.append_message()` or
    `.append_message_stream()`.

    Here's a rough outline for how to implement a `Chat`:

    ```python
    from shiny.express import ui

    # Create and display chat instance
    chat = ui.Chat(id="my_chat")
    chat.ui()

    # Define a callback to run when the user submits a message
    @chat.on_user_submit
    async def handle_user_input(user_input: str):
        # Create a response message stream
        response = await my_model.generate_response(user_input, stream=True)
        # Append the response into the chat
        await chat.append_message_stream(response)
    ```

    In the outline above, `my_model.generate_response()` is a placeholder for
    the function that generates a response based on the chat's messages. This function
    will look different depending on the model you're using, but it will generally
    involve passing the messages to the model and getting a response back. Also, you'll
    typically have a choice to `stream=True` the response generation, and in that case,
    you'll use `.append_message_stream()` instead of `.append_message()` to append the
    response to the chat. Streaming is preferrable when available since it allows for
    more responsive and scalable chat interfaces.

    It is also highly recommended to use a package like
    [chatlas](https://posit-dev.github.io/chatlas/) to generate responses, especially
    when responses should be aware of the chat history, support tool calls, etc.
    See this [article](https://posit-dev.github.io/chatlas/web-apps.html) to learn more.

    Parameters
    ----------
    id
        A unique identifier for the chat session. In Shiny Core, make sure this id
        matches a corresponding :func:`~shiny.ui.chat_ui` call in the UI.
    messages
        A sequence of messages to display in the chat. A given message can be one of the
        following:

        * A string, which is interpreted as markdown and rendered to HTML on the client.
            * To prevent interpreting as markdown, mark the string as
              :class:`~shiny.ui.HTML`.
        * A UI element (specifically, a :class:`~shiny.ui.TagChild`).
            * This includes :class:`~shiny.ui.TagList`, which take UI elements
              (including strings) as children. In this case, strings are still
              interpreted as markdown as long as they're not inside HTML.
        * A dictionary with `content` and `role` keys. The `content` key can contain a
          content as described above, and the `role` key can be "assistant" or "user".

        **NOTE:** content may include specially formatted **input suggestion** links
        (see `.append_message()` for more information).
    on_error
        How to handle errors that occur in response to user input. When `"unhandled"`,
        the app will stop running when an error occurs. Otherwise, a notification
        is displayed to the user and the app continues to run.

        * `"auto"`: Sanitize the error message if the app is set to sanitize errors,
          otherwise display the actual error message.
        * `"actual"`: Display the actual error message to the user.
        * `"sanitize"`: Sanitize the error message before displaying it to the user.
        * `"unhandled"`: Do not display any error message to the user.
    tokenizer
        The tokenizer to use for calculating token counts, which is required to impose
        `token_limits` in `.messages()`. If not provided, a default generic tokenizer
        is attempted to be loaded from the tokenizers library. A specific tokenizer
        may also be provided by following the `TokenEncoding` (tiktoken or tozenizers)
        protocol (e.g., `tiktoken.encoding_for_model("gpt-4o")`).
    """

    def __init__(
        self,
        id: str,
        *,
        messages: Sequence[Any] = (),
        on_error: Literal["auto", "actual", "sanitize", "unhandled"] = "auto",
        tokenizer: TokenEncoding | None = None,
    ):
        if not isinstance(id, str):
            raise TypeError("`id` must be a string.")

        self.id = resolve_id(id)
        self.user_input_id = ResolvedId(f"{self.id}_user_input")
        self._transform_user: TransformUserInputAsync | None = None
        self._transform_assistant: TransformAssistantResponseChunkAsync | None = None
        self._tokenizer = tokenizer

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

        # Chunked messages get accumulated (using this property) before changing state
        self._current_stream_message: str = ""
        self._current_stream_id: str | None = None
        self._pending_messages: list[PendingMessage] = []

        # For tracking message stream state when entering/exiting nested streams
        self._message_stream_checkpoint: str = ""

        # If a user input message is transformed into a response, we need to cancel
        # the next user input submit handling
        self._suspend_input_handler: bool = False

        # Keep track of effects so we can destroy them when the chat is destroyed
        self._effects: list[reactive.Effect_] = []
        self._cancel_bookmarking_callbacks: CancelCallback | None = None

        # Initialize chat state and user input effect
        with session_context(self._session):
            # Initialize message state
            self._messages: reactive.Value[tuple[TransformedMessage, ...]] = (
                reactive.Value(())
            )

            self._latest_user_input: reactive.Value[TransformedMessage | None] = (
                reactive.Value(None)
            )

            @reactive.extended_task
            async def _mock_task() -> str:
                return ""

            self._latest_stream: reactive.Value[reactive.ExtendedTask[[], str]] = (
                reactive.Value(_mock_task)
            )

            # TODO: deprecate messages once we start promoting managing LLM message
            # state through other means
            async def _append_init_messages():
                for msg in messages:
                    await self.append_message(msg)

            @reactive.effect
            async def _init_chat():
                await _append_init_messages()

            self._append_init_messages = _append_init_messages
            self._init_chat = _init_chat

            # When user input is submitted, transform, and store it in the chat state
            # (and make sure this runs before other effects since when the user
            #  calls `.messages()`, they should get the latest user input)
            @reactive.effect(priority=9999)
            @reactive.event(self._user_input)
            async def _on_user_input():
                msg = ChatMessage(content=self._user_input(), role="user")
                # It's possible that during the transform, a message is appended, so get
                # the length now, so we can insert the new message at the right index
                n_pre = len(self._messages())
                msg_post = await self._transform_message(msg)
                if msg_post is not None:
                    self._store_message(msg_post)
                    self._suspend_input_handler = False
                else:
                    # A transformed value of None is a special signal to suspend input
                    # handling (i.e., don't generate a response)
                    self._store_message(msg, index=n_pre)
                    await self._remove_loading_message()
                    self._suspend_input_handler = True

            self._effects.append(_init_chat)
            self._effects.append(_on_user_input)

        # Prevent repeated calls to Chat() with the same id from accumulating effects
        instance_id = self.id + "_session" + self._session.id
        instance = CHAT_INSTANCES.pop(instance_id, None)
        if instance is not None:
            instance.destroy()
        CHAT_INSTANCES[instance_id] = self

    @overload
    def on_user_submit(self, fn: UserSubmitFunction) -> reactive.Effect_: ...

    @overload
    def on_user_submit(
        self,
    ) -> Callable[[UserSubmitFunction], reactive.Effect_]: ...

    def on_user_submit(
        self, fn: UserSubmitFunction | None = None
    ) -> reactive.Effect_ | Callable[[UserSubmitFunction], reactive.Effect_]:
        """
        Define a function to invoke when user input is submitted.

        Apply this method as a decorator to a function (`fn`) that should be invoked
        when the user submits a message. This function can take an optional argument,
        which will be the user input message.

        In many cases, the implementation of `fn` should also do the following:

        1. Generate a response based on the user input.
          * If the response should be aware of chat history, use a package
             like [chatlas](https://posit-dev.github.io/chatlas/) to manage the chat
             state, or use the `.messages()` method to get the chat history.
        2. Append that response to the chat component using `.append_message()` ( or
           `.append_message_stream()` if the response is streamed).

        Parameters
        ----------
        fn
            A function to invoke when user input is submitted.

        Note
        ----
        This method creates a reactive effect that only gets invalidated when the user
        submits a message. Thus, the function `fn` can read other reactive dependencies,
        but it will only be re-invoked when the user submits a message.
        """

        def create_effect(fn: UserSubmitFunction):
            fn_params = inspect.signature(fn).parameters

            @reactive.effect
            @reactive.event(self._user_input)
            async def handle_user_input():
                if self._suspend_input_handler:
                    from .. import req

                    req(False)
                try:
                    if len(fn_params) > 1:
                        raise ValueError(
                            "A on_user_submit function should not take more than 1 argument"
                        )
                    elif len(fn_params) == 1:
                        input = self.user_input(transform=True)
                        # The line immediately below handles the possibility of input
                        # being transformed to None. Technically, input should never be
                        # None at this point (since the handler should be suspended).
                        input = "" if input is None else input
                        afunc = _utils.wrap_async(cast(UserSubmitFunction1, fn))
                        await afunc(input)
                    else:
                        afunc = _utils.wrap_async(cast(UserSubmitFunction0, fn))
                        await afunc()
                except Exception as e:
                    await self._raise_exception(e)

            self._effects.append(handle_user_input)

            return handle_user_input

        if fn is None:
            return create_effect
        else:
            return create_effect(fn)

    async def _raise_exception(
        self,
        e: BaseException,
    ) -> None:
        if self.on_error == "unhandled":
            raise e
        else:
            await self._remove_loading_message()
            sanitize = self.on_error == "sanitize"
            msg = f"Error in Chat('{self.id}'): {str(e)}"
            raise NotifyException(msg, sanitize=sanitize) from e

    @overload
    def messages(
        self,
        *,
        format: Literal["anthropic"],
        token_limits: tuple[int, int] | None = None,
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[AnthropicMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: Literal["google"],
        token_limits: tuple[int, int] | None = None,
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[GoogleMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: Literal["langchain"],
        token_limits: tuple[int, int] | None = None,
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[LangChainMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: Literal["openai"],
        token_limits: tuple[int, int] | None = None,
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[OpenAIMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: Literal["ollama"],
        token_limits: tuple[int, int] | None = None,
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[OllamaMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: MISSING_TYPE = MISSING,
        token_limits: tuple[int, int] | None = None,
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[ChatMessageDict, ...]: ...

    def messages(
        self,
        *,
        format: MISSING_TYPE | ProviderMessageFormat = MISSING,
        token_limits: tuple[int, int] | None = None,
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[ChatMessageDict | ProviderMessage, ...]:
        """
        Reactively read chat messages

        Obtain chat messages within a reactive context. The default behavior is
        intended for passing messages along to a model for response generation where
        you typically want to:

        1. Cap the number of tokens sent in a single request (i.e., `token_limits`).
        2. Apply user input transformations (i.e., `transform_user`), if any.
        3. Not apply assistant response transformations (i.e., `transform_assistant`)
           since these are predominantly for display purposes (i.e., the model shouldn't
           concern itself with how the responses are displayed).

        Parameters
        ----------
        format
            The message format to return. The default value of `MISSING` means
            chat messages are returned as :class:`ChatMessage` objects (a dictionary
            with `content` and `role` keys). Other supported formats include:

            * `"anthropic"`: Anthropic message format.
            * `"google"`: Google message (aka content) format.
            * `"langchain"`: LangChain message format.
            * `"openai"`: OpenAI message format.
            * `"ollama"`: Ollama message format.
        token_limits
            Limit the conversation history based on token limits. If specified, only
            the most recent messages that fit within the token limits are returned. This
            is useful for avoiding "exceeded token limit" errors when sending messages
            to the relevant model, while still providing the most recent context available.
            A specified value must be a tuple of two integers. The first integer is the
            maximum number of tokens that can be sent to the model in a single request.
            The second integer is the amount of tokens to reserve for the model's response.
            Note that token counts based on the `tokenizer` provided to the `Chat`
            constructor.
        transform_user
            Whether to return user input messages with transformation applied. This only
            matters if a `transform_user_input` was provided to the chat constructor.
            The default value of `"all"` means all user input messages are transformed.
            The value of `"last"` means only the last user input message is transformed.
            The value of `"none"` means no user input messages are transformed.
        transform_assistant
            Whether to return assistant messages with transformation applied. This only
            matters if an `transform_assistant_response` was provided to the chat
            constructor.

        Note
        ----
        Messages are listed in the order they were added. As a result, when this method
        is called in a `.on_user_submit()` callback (as it most often is), the last
        message will be the most recent one submitted by the user.

        Returns
        -------
        tuple[ChatMessage, ...]
            A tuple of chat messages.
        """

        messages = self._messages()

        # Anthropic requires a user message first and no system messages
        if format == "anthropic":
            messages = self._trim_anthropic_messages(messages)

        if token_limits is not None:
            messages = self._trim_messages(messages, token_limits, format)

        res: list[ChatMessageDict | ProviderMessage] = []
        for i, m in enumerate(messages):
            transform = False
            if m.role == "assistant":
                transform = transform_assistant
            elif m.role == "user":
                transform = transform_user == "all" or (
                    transform_user == "last" and i == len(messages) - 1
                )
            content_key = getattr(
                m, "transform_key" if transform else "pre_transform_key"
            )
            content = getattr(m, content_key)
            chat_msg = ChatMessageDict(content=str(content), role=m.role)
            if not isinstance(format, MISSING_TYPE):
                chat_msg = as_provider_message(chat_msg, format)
            res.append(chat_msg)

        return tuple(res)

    async def append_message(
        self,
        message: Any,
        *,
        icon: HTML | Tag | TagList | None = None,
    ):
        """
        Append a message to the chat.

        Parameters
        ----------
        message
            A given message can be one of the following:

            * A string, which is interpreted as markdown and rendered to HTML on the
              client.
                * To prevent interpreting as markdown, mark the string as
                  :class:`~shiny.ui.HTML`.
            * A UI element (specifically, a :class:`~shiny.ui.TagChild`).
                * This includes :class:`~shiny.ui.TagList`, which take UI elements
                  (including strings) as children. In this case, strings are still
                  interpreted as markdown as long as they're not inside HTML.
            * A dictionary with `content` and `role` keys. The `content` key can contain
              content as described above, and the `role` key can be "assistant" or
              "user".

            **NOTE:** content may include specially formatted **input suggestion** links
            (see note below).
        icon
            An optional icon to display next to the message, currently only used for
            assistant messages. The icon can be any HTML element (e.g., an
            :func:`~shiny.ui.img` tag) or a string of HTML.

        Note
        ----
        :::{.callout-note title="Input suggestions"}
        Input suggestions are special links that send text to the user input box when
        clicked (or accessed via keyboard). They can be created in the following ways:

        * `<span class='suggestion'>Suggestion text</span>`: An inline text link that
            places 'Suggestion text' in the user input box when clicked.
        * `<img data-suggestion='Suggestion text' src='image.jpg'>`: An image link with
            the same functionality as above.
        * `<span data-suggestion='Suggestion text'>Actual text</span>`: An inline text
            link that places 'Suggestion text' in the user input box when clicked.

        A suggestion can also be submitted automatically by doing one of the following:

        * Adding a `submit` CSS class or a `data-suggestion-submit="true"` attribute to
          the suggestion element.
        * Holding the `Ctrl/Cmd` key while clicking the suggestion link.

        Note that a user may also opt-out of submitting a suggestion by holding the
        `Alt/Option` key while clicking the suggestion link.
        :::

        :::{.callout-note title="Streamed messages"}
        Use `.append_message_stream()` instead of this method when `stream=True` (or
        similar) is specified in model's completion method.
        :::
        """
        # If we're in a stream, queue the message
        if self._current_stream_id:
            self._pending_messages.append((message, False, "append", None))
            return

        msg = normalize_message(message)
        msg = await self._transform_message(msg)
        if msg is None:
            return
        self._store_message(msg)
        await self._send_append_message(
            message=msg,
            chunk=False,
            icon=icon,
        )

    @asynccontextmanager
    async def message_stream_context(self):
        """
        Message stream context manager.

        A context manager for appending streaming messages into the chat. This context
        manager can:

        1. Be used in isolation to append a new streaming message to the chat.
            * Compared to `.append_message_stream()` this method is more flexible but
              isn't non-blocking by default (i.e., it doesn't launch an extended task).
        2. Be nested within itself
            * Nesting is primarily useful for making checkpoints to `.clear()` back
              to (see the example below).
        3. Be used from within a `.append_message_stream()`
            * Useful for inserting additional content from another context into the
              stream (e.g., see the note about tool calls below).

        Yields
        ------
        :
            A `MessageStream` class instance, which has a method for `.append()`ing
            message content chunks to as well as way to `.clear()` the stream back to
            it's initial state. Note that `.append()` supports the same message content
            types as `.append_message()`.

        Example
        -------
        ```python
        import asyncio

        from shiny import reactive
        from shiny.express import ui

        chat = ui.Chat(id="my_chat")
        chat.ui()

        @reactive.effect
        async def _():
            async with chat.message_stream_context() as msg:
                await msg.append("Starting stream...\n\nProgress:")
                async with chat.message_stream_context() as progress:
                    for x in [0, 50, 100]:
                        await progress.append(f" {x}%")
                        await asyncio.sleep(1)
                        await progress.clear()
                await msg.clear()
                await msg.append("Completed stream")
        ```

        Note
        ----
        A useful pattern for displaying tool calls in a chatbot is for the tool to
        display using `.message_stream_context()` while the the response generation is
        happening through `.append_message_stream()`. This allows the tool to display
        things like progress updates (or other "ephemeral" content) and optionally
        `.clear()` the stream back to it's initial state when ready to display the
        "final" content.
        """
        # Checkpoint the current stream state so operation="replace"  can return to it
        old_checkpoint = self._message_stream_checkpoint
        self._message_stream_checkpoint = self._current_stream_message

        # No stream currently exists, start one
        stream_id = self._current_stream_id
        is_root_stream = stream_id is None
        if is_root_stream:
            stream_id = _utils.private_random_id()
            await self._append_message_chunk("", chunk="start", stream_id=stream_id)

        try:
            yield MessageStream(self, stream_id)
        finally:
            # Restore the checkpoint
            self._message_stream_checkpoint = old_checkpoint

            # If this was the root stream, end it
            if is_root_stream:
                await self._append_message_chunk(
                    "",
                    chunk="end",
                    stream_id=stream_id,
                )

    async def _append_message_chunk(
        self,
        message: Any,
        *,
        chunk: Literal[True, "start", "end"] = True,
        stream_id: str,
        operation: Literal["append", "replace"] = "append",
        icon: HTML | Tag | TagList | None = None,
    ) -> None:
        # If currently we're in a *different* stream, queue the message chunk
        if self._current_stream_id and self._current_stream_id != stream_id:
            self._pending_messages.append((message, chunk, operation, stream_id))
            return

        self._current_stream_id = stream_id

        # Normalize various message types into a ChatMessage()
        msg = normalize_message_chunk(message)

        if operation == "replace":
            self._current_stream_message = self._message_stream_checkpoint + msg.content
            msg.content = self._current_stream_message
        else:
            self._current_stream_message += msg.content

        try:
            if self._needs_transform(msg):
                # Transforming may change the meaning of msg.content to be a *replace*
                # not *append*. So, update msg.content and the operation accordingly.
                chunk_content = msg.content
                msg.content = self._current_stream_message
                operation = "replace"
                msg = await self._transform_message(
                    msg, chunk=chunk, chunk_content=chunk_content
                )
                # Act like nothing happened if transformed to None
                if msg is None:
                    return
                if chunk == "end":
                    self._store_message(msg)
            elif chunk == "end":
                # When `operation="append"`, msg.content is just a chunk, but we must
                # store the full message
                self._store_message(
                    ChatMessage(content=self._current_stream_message, role=msg.role)
                )

            # Send the message to the client
            await self._send_append_message(
                message=msg,
                chunk=chunk,
                operation=operation,
                icon=icon,
            )
        finally:
            if chunk == "end":
                self._current_stream_id = None
                self._current_stream_message = ""
                self._message_stream_checkpoint = ""

    async def append_message_stream(
        self,
        message: Iterable[Any] | AsyncIterable[Any],
        *,
        icon: HTML | Tag | None = None,
    ):
        """
        Append a message as a stream of message chunks.

        Parameters
        ----------
        message
            An (async) iterable of message chunks. Each chunk can be one of the
            following:

            * A string, which is interpreted as markdown and rendered to HTML on the
              client.
                * To prevent interpreting as markdown, mark the string as
                  :class:`~shiny.ui.HTML`.
            * A UI element (specifically, a :class:`~shiny.ui.TagChild`).
                * This includes :class:`~shiny.ui.TagList`, which take UI elements
                  (including strings) as children. In this case, strings are still
                  interpreted as markdown as long as they're not inside HTML.
            * A dictionary with `content` and `role` keys. The `content` key can contain
              content as described above, and the `role` key can be "assistant" or
              "user".

            **NOTE:** content may include specially formatted **input suggestion** links
            (see note below).
        icon
            An optional icon to display next to the message, currently only used for
            assistant messages. The icon can be any HTML element (e.g., an
            :func:`~shiny.ui.img` tag) or a string of HTML.

        Note
        ----
        ```{.callout-note title="Input suggestions"}
        Input suggestions are special links that send text to the user input box when
        clicked (or accessed via keyboard). They can be created in the following ways:

        * `<span class='suggestion'>Suggestion text</span>`: An inline text link that
            places 'Suggestion text' in the user input box when clicked.
        * `<img data-suggestion='Suggestion text' src='image.jpg'>`: An image link with
            the same functionality as above.
        * `<span data-suggestion='Suggestion text'>Actual text</span>`: An inline text
            link that places 'Suggestion text' in the user input box when clicked.

        A suggestion can also be submitted automatically by doing one of the following:

        * Adding a `submit` CSS class or a `data-suggestion-submit="true"` attribute to
          the suggestion element.
        * Holding the `Ctrl/Cmd` key while clicking the suggestion link.

        Note that a user may also opt-out of submitting a suggestion by holding the
        `Alt/Option` key while clicking the suggestion link.
        ```

        ```{.callout-note title="Streamed messages"}
        Use this method (over `.append_message()`) when `stream=True` (or similar) is
        specified in model's completion method.
        ```

        Returns
        -------
        :
            An extended task that represents the streaming task. The `.result()` method
            of the task can be called in a reactive context to get the final state of the
            stream.
        """

        message = _utils.wrap_async_iterable(message)

        # Run the stream in the background to get non-blocking behavior
        @reactive.extended_task
        async def _stream_task():
            return await self._append_message_stream(message, icon=icon)

        _stream_task()

        self._latest_stream.set(_stream_task)

        # Since the task runs in the background (outside/beyond the current context,
        # if any), we need to manually raise any exceptions that occur
        @reactive.effect
        async def _handle_error():
            e = _stream_task.error()
            if e:
                await self._raise_exception(e)
            _handle_error.destroy()  # type: ignore

        return _stream_task

    @property
    def latest_message_stream(self) -> reactive.ExtendedTask[[], str]:
        """
        React to changes in the latest message stream.

        Reactively reads for the :class:`~shiny.reactive.ExtendedTask` behind an
        `.append_message_stream()`.

        From the return value (i.e., the extended task), you can then:

        1. Reactively read for the final `.result()`.
        2. `.cancel()` the stream.
        3. Check the `.status()` of the stream.

        Returns
        -------
        :
            An extended task that represents the streaming task. The `.result()` method
            of the task can be called in a reactive context to get the final state of the
            stream.

        Note
        ----
        If no stream has yet been started when this method is called, then it returns an
        extended task with `.status()` of `"initial"` and that it status doesn't change
        state until a message is streamed.
        """
        return self._latest_stream()

    async def _append_message_stream(
        self,
        message: AsyncIterable[Any],
        icon: HTML | Tag | None = None,
    ):
        id = _utils.private_random_id()

        empty = ChatMessageDict(content="", role="assistant")
        await self._append_message_chunk(empty, chunk="start", stream_id=id, icon=icon)

        try:
            async for msg in message:
                await self._append_message_chunk(msg, chunk=True, stream_id=id)
            return self._current_stream_message
        finally:
            await self._append_message_chunk(empty, chunk="end", stream_id=id)
            await self._flush_pending_messages()

    async def _flush_pending_messages(self):
        pending = self._pending_messages
        self._pending_messages = []
        for msg, chunk, operation, stream_id in pending:
            if chunk is False:
                await self.append_message(msg)
            else:
                await self._append_message_chunk(
                    msg,
                    chunk=chunk,
                    operation=operation,
                    stream_id=cast(str, stream_id),
                )

    # Send a message to the UI
    async def _send_append_message(
        self,
        message: TransformedMessage | ChatMessage,
        chunk: ChunkOption = False,
        operation: Literal["append", "replace"] = "append",
        icon: HTML | Tag | TagList | None = None,
    ):
        if not isinstance(message, TransformedMessage):
            message = TransformedMessage.from_chat_message(message)

        if message.role == "system":
            # System messages are not displayed in the UI
            return

        if chunk:
            msg_type = "shiny-chat-append-message-chunk"
        else:
            msg_type = "shiny-chat-append-message"

        chunk_type = None
        if chunk == "start":
            chunk_type = "message_start"
        elif chunk == "end":
            chunk_type = "message_end"

        content = message.content_client
        content_type = "html" if isinstance(content, HTML) else "markdown"

        # TODO: pass along dependencies for both content and icon (if any)
        msg = ClientMessage(
            content=str(content),
            role=message.role,
            content_type=content_type,
            chunk_type=chunk_type,
            operation=operation,
        )

        if icon is not None:
            msg["icon"] = str(icon)

        deps = message.html_deps
        if deps:
            msg["html_deps"] = deps

        # print(msg)

        await self._send_custom_message(msg_type, msg)
        # TODO: Joe said it's a good idea to yield here, but I'm not sure why?
        # await asyncio.sleep(0)

    @overload
    def transform_user_input(
        self, fn: TransformUserInput | TransformUserInputAsync
    ) -> None: ...

    @overload
    def transform_user_input(
        self,
    ) -> Callable[[TransformUserInput | TransformUserInputAsync], None]: ...

    def transform_user_input(
        self, fn: TransformUserInput | TransformUserInputAsync | None = None
    ) -> None | Callable[[TransformUserInput | TransformUserInputAsync], None]:
        """
        Transform user input.

        Use this method as a decorator on a function (`fn`) that transforms user input
        before storing it in the chat messages returned by `.messages()`. This is
        useful for implementing RAG workflows, like taking a URL and scraping it for
        text before sending it to the model.

        Parameters
        ----------
        fn
            A function to transform user input before storing it in the chat
            `.messages()`. If `fn` returns `None`, the user input is effectively
            ignored, and `.on_user_submit()` callbacks are suspended until more input is
            submitted. This behavior is often useful to catch and handle errors that
            occur during transformation. In this case, the transform function should
            append an error message to the chat (via `.append_message()`) to inform the
            user of the error.
        """

        def _set_transform(fn: TransformUserInput | TransformUserInputAsync):
            self._transform_user = _utils.wrap_async(fn)

        if fn is None:
            return _set_transform
        else:
            return _set_transform(fn)

    @overload
    def transform_assistant_response(
        self, fn: TransformAssistantResponseFunction
    ) -> None: ...

    @overload
    def transform_assistant_response(
        self,
    ) -> Callable[[TransformAssistantResponseFunction], None]: ...

    def transform_assistant_response(
        self,
        fn: TransformAssistantResponseFunction | None = None,
    ) -> None | Callable[[TransformAssistantResponseFunction], None]:
        """
        Transform assistant responses.

        Use this method as a decorator on a function (`fn`) that transforms assistant
        responses before displaying them in the chat. This is useful for post-processing
        model responses before displaying them to the user.

        Parameters
        ----------
        fn
            A function that takes a string and returns either a string,
            :class:`shiny.ui.HTML`, or `None`. If `fn` returns a string, it gets
            interpreted and parsed as a markdown on the client (and the resulting HTML
            is then sanitized). If `fn` returns :class:`shiny.ui.HTML`, it will be
            displayed as-is. If `fn` returns `None`, the response is effectively ignored.

        Note
        ----
        When doing an `.append_message_stream()`, `fn` gets called on every chunk of the
        response (thus, it should be performant), and can optionally access more
        information (i.e., arguments) about the stream. The 1st argument (required)
        contains the accumulated content, the 2nd argument (optional) contains the
        current chunk, and the 3rd argument (optional) is a boolean indicating whether
        this chunk is the last one in the stream.
        """

        def _set_transform(
            fn: TransformAssistantResponseFunction,
        ):
            nparams = len(inspect.signature(fn).parameters)
            if nparams == 1:
                fn = cast(
                    Union[TransformAssistantResponse, TransformAssistantResponseAsync],
                    fn,
                )
                fn = _utils.wrap_async(fn)

                async def _transform_wrapper(content: str, chunk: str, done: bool):
                    return await fn(content)

                self._transform_assistant = _transform_wrapper

            elif nparams == 3:
                fn = cast(
                    Union[
                        TransformAssistantResponseChunk,
                        TransformAssistantResponseChunkAsync,
                    ],
                    fn,
                )
                self._transform_assistant = _utils.wrap_async(fn)
            else:
                raise Exception(
                    "A @transform_assistant_response function must take 1 or 3 arguments"
                )

        if fn is None:
            return _set_transform
        else:
            return _set_transform(fn)

    async def _transform_message(
        self,
        message: ChatMessage,
        chunk: ChunkOption = False,
        chunk_content: str = "",
    ) -> TransformedMessage | None:
        res = TransformedMessage.from_chat_message(message)

        if message.role == "user" and self._transform_user is not None:
            content = await self._transform_user(message.content)
        elif message.role == "assistant" and self._transform_assistant is not None:
            content = await self._transform_assistant(
                message.content,
                chunk_content,
                chunk == "end" or chunk is False,
            )
        else:
            return res

        if content is None:
            return None

        setattr(res, res.transform_key, content)
        return res

    def _needs_transform(self, message: ChatMessage) -> bool:
        if message.role == "user" and self._transform_user is not None:
            return True
        elif message.role == "assistant" and self._transform_assistant is not None:
            return True
        return False

    # Just before storing, handle chunk msg type and calculate tokens
    def _store_message(
        self,
        message: TransformedMessage | ChatMessage,
        index: int | None = None,
    ) -> None:

        if not isinstance(message, TransformedMessage):
            message = TransformedMessage.from_chat_message(message)

        with reactive.isolate():
            messages = self._messages()

        if index is None:
            index = len(messages)

        messages = list(messages)
        messages.insert(index, message)

        self._messages.set(tuple(messages))
        if message.role == "user":
            self._latest_user_input.set(message)

        return None

    def _trim_messages(
        self,
        messages: tuple[TransformedMessage, ...],
        token_limits: tuple[int, int],
        format: MISSING_TYPE | ProviderMessageFormat,
    ) -> tuple[TransformedMessage, ...]:
        n_total, n_reserve = token_limits
        if n_total <= n_reserve:
            raise ValueError(
                f"Invalid token limits: {token_limits}. The 1st value must be greater "
                "than the 2nd value."
            )

        # Since don't trim system messages, 1st obtain their total token count
        # (so we can determine how many non-system messages can fit)
        n_system_tokens: int = 0
        n_system_messages: int = 0
        n_other_messages: int = 0
        token_counts: list[int] = []
        for m in messages:
            count = self._get_token_count(m.content_server)
            token_counts.append(count)
            if m.role == "system":
                n_system_tokens += count
                n_system_messages += 1
            else:
                n_other_messages += 1

        remaining_non_system_tokens = n_total - n_reserve - n_system_tokens

        if remaining_non_system_tokens <= 0:
            raise ValueError(
                f"System messages exceed `.messages(token_limits={token_limits})`. "
                "Consider increasing the 1st value of `token_limit` or setting it to "
                "`token_limit=None` to disable token limits."
            )

        # Now, iterate through the messages in reverse order and appending
        # until we run out of tokens
        messages2: list[TransformedMessage] = []
        n_other_messages2: int = 0
        token_counts.reverse()
        for i, m in enumerate(reversed(messages)):
            if m.role == "system":
                messages2.append(m)
                continue
            remaining_non_system_tokens -= token_counts[i]
            if remaining_non_system_tokens >= 0:
                messages2.append(m)
                n_other_messages2 += 1

        messages2.reverse()

        if len(messages2) == n_system_messages and n_other_messages2 > 0:
            raise ValueError(
                f"Only system messages fit within `.messages(token_limits={token_limits})`. "
                "Consider increasing the 1st value of `token_limit` or setting it to "
                "`token_limit=None` to disable token limits."
            )

        return tuple(messages2)

    def _trim_anthropic_messages(
        self,
        messages: tuple[TransformedMessage, ...],
    ) -> tuple[TransformedMessage, ...]:
        if any(m.role == "system" for m in messages):
            raise ValueError(
                "Anthropic requires a system prompt to be specified in it's `.create()` method "
                "(not in the chat messages with `role: system`)."
            )
        for i, m in enumerate(messages):
            if m.role == "user":
                return messages[i:]

        return ()

    def _get_token_count(
        self,
        content: str,
    ) -> int:
        if self._tokenizer is None:
            self._tokenizer = get_default_tokenizer()

        encoded = self._tokenizer.encode(content)
        if isinstance(encoded, TokenizersEncoding):
            return len(encoded.ids)
        else:
            return len(encoded)

    def user_input(self, transform: bool = False) -> str | None:
        """
        Reactively read the user's message.

        Parameters
        ----------
        transform
            Whether to apply the user input transformation function (if one was
            provided).

        Returns
        -------
        str | None
            The user input message (before any transformation).

        Note
        ----
        Most users shouldn't need to use this method directly since the last item in
        `.messages()` contains the most recent user input. It can be useful for:

          1. Taking a reactive dependency on the user's input outside of a `.on_user_submit()` callback.
          2. Maintaining message state separately from `.messages()`.

        """
        msg = self._latest_user_input()
        if msg is None:
            return None
        key = "content_server" if transform else "content_client"
        val = getattr(msg, key)
        return str(val)

    def _user_input(self) -> str:
        id = self.user_input_id
        return cast(str, self._session.input[id]())

    def update_user_input(
        self,
        *,
        value: str | None = None,
        placeholder: str | None = None,
        submit: bool = False,
        focus: bool = False,
    ):
        """
        Update the user input.

        Parameters
        ----------
        value
            The value to set the user input to.
        placeholder
            The placeholder text for the user input.
        submit
            Whether to automatically submit the text for the user. Requires `value`.
        focus
            Whether to move focus to the input element. Requires `value`.
        """

        if value is None and (submit or focus):
            raise ValueError(
                "An input `value` must be provided when `submit` or `focus` are `True`."
            )

        obj = _utils.drop_none(
            {
                "value": value,
                "placeholder": placeholder,
                "submit": submit,
                "focus": focus,
            }
        )

        msg = {
            "id": self.id,
            "handler": "shiny-chat-update-user-input",
            "obj": obj,
        }

        self._session._send_message_sync({"custom": {"shinyChatMessage": msg}})

    def set_user_message(self, value: str):
        """
        Deprecated. Use `update_user_input(value=value)` instead.
        """

        warn_deprecated(
            "set_user_message() is deprecated. Use update_user_input(value=value) instead."
        )

        self.update_user_input(value=value)

    async def clear_messages(self):
        """
        Clear all chat messages.
        """
        self._messages.set(())
        await self._send_custom_message("shiny-chat-clear-messages", None)

    def destroy(self):
        """
        Destroy the chat instance.
        """
        self._destroy_effects()
        self._destroy_bookmarking()

    def _destroy_effects(self):
        for x in self._effects:
            x.destroy()
        self._effects.clear()

    def _destroy_bookmarking(self):
        if not self._cancel_bookmarking_callbacks:
            return

        self._cancel_bookmarking_callbacks()
        self._cancel_bookmarking_callbacks = None

    async def _remove_loading_message(self):
        await self._send_custom_message("shiny-chat-remove-loading-message", None)

    async def _send_custom_message(self, handler: str, obj: ClientMessage | None):
        await self._session.send_custom_message(
            "shinyChatMessage",
            {
                "id": self.id,
                "handler": handler,
                "obj": obj,
            },
        )

    def enable_bookmarking(
        self,
        client: ClientWithState | chatlas.Chat[Any, Any],
        /,
        *,
        bookmark_on: Optional[Literal["response"]] = "response",
    ) -> CancelCallback:
        """
        Enable bookmarking for the chat instance.

        This method registers `on_bookmark` and `on_restore` hooks on `session.bookmark`
        (:class:`shiny.bookmark.Bookmark`) to save/restore chat state on both the `Chat`
        and `client=` instances. In order for this method to actually work correctly, a
        `bookmark_store=` must be specified in `shiny.App()`.

        Parameters
        ----------
        client
            The chat client instance to use for bookmarking. This can be a Chat model
            provider from [chatlas](https://posit-dev.github.io/chatlas/), or more
            generally, an instance following the `ClientWithState` protocol.
        bookmark_on
            The event to trigger the bookmarking on. Supported values include:

            - `"response"` (the default): a bookmark is triggered when the assistant is done responding.
            - `None`: no bookmark is triggered

            When this method triggers a bookmark, it also updates the URL query string to reflect the bookmarked state.


        Raises
        ------
        ValueError
            If the Shiny App does have bookmarking enabled.

        Returns
        -------
        :
            A callback to cancel the bookmarking hooks.
        """
        from ..express._stub_session import ExpressStubSession

        session = get_current_session()
        if session is None or isinstance(session, ExpressStubSession):
            return BookmarkCancelCallback(lambda: None)

        if session.bookmark.store == "disable":
            raise ValueError(
                "Bookmarking requires a `bookmark_store` to be set. "
                "Please set `bookmark_store=` in `shiny.App()` or `shiny.express.app_opts()."
            )

        resolved_bookmark_id_str = str(self.id)
        resolved_bookmark_id_msgs_str = resolved_bookmark_id_str + "--msgs"
        get_state: Callable[[], Awaitable[Jsonifiable]]
        set_state: Callable[[Jsonifiable], Awaitable[None]]

        # Retrieve get_state/set_state functions from the client
        if isinstance(client, ClientWithState):
            # Do client with state stuff here
            get_state = wrap_async(client.get_state)
            set_state = wrap_async(client.set_state)

        elif is_chatlas_chat_client(client):

            get_state = get_chatlas_state(client)
            set_state = set_chatlas_state(client)

        else:
            raise ValueError(
                "Bookmarking requires a client that supports "
                "`async def get_state(self) -> shiny.types.Jsonifiable` (which returns an object that can be used when bookmarking to save the state of the `client=`) and "
                "`async def set_state(self, value: Jsonifiable)` (which should restore the `client=`'s state given the `state=`)."
            )

        # Reset prior bookmarking hooks
        self._destroy_bookmarking()

        # Must use `root_session` as the id is already resolved. :-/
        # Using a proxy session would double-encode the proxy-prefix
        root_session = session.root_scope()
        root_session.bookmark.exclude.append(self.id + "_user_input")

        # ###########
        # Bookmarking

        if bookmark_on is not None:

            # When ever the bookmark is requested, update the query string (indep of store type)
            @root_session.bookmark.on_bookmarked
            async def _(url: str):
                await session.bookmark.update_query_string(url)

        if bookmark_on == "response":

            @reactive.effect
            @reactive.event(lambda: self.messages(format=MISSING), ignore_init=True)
            async def _():
                messages = self.messages(format=MISSING)

                if len(messages) == 0:
                    return

                last_message = messages[-1]

                if last_message.get("role") == "assistant":
                    await session.bookmark()

        ###############
        # Client Bookmarking

        @root_session.bookmark.on_bookmark
        async def _on_bookmark_client(state: BookmarkState):
            if resolved_bookmark_id_str in state.values:
                raise ValueError(
                    f'Bookmark value with id (`"{resolved_bookmark_id_str}"`) already exists.'
                )

            with reactive.isolate():
                state.values[resolved_bookmark_id_str] = await get_state()

        @root_session.bookmark.on_restore
        async def _on_restore_client(state: RestoreState):
            if resolved_bookmark_id_str not in state.values:
                return

            # Retrieve the chat turns from the bookmark state
            info = state.values[resolved_bookmark_id_str]
            await set_state(info)

        ###############
        # UI Bookmarking

        @root_session.bookmark.on_bookmark
        def _on_bookmark_ui(state: BookmarkState):
            if resolved_bookmark_id_msgs_str in state.values:
                raise ValueError(
                    f'Bookmark value with id (`"{resolved_bookmark_id_msgs_str}"`) already exists.'
                )

            with reactive.isolate():
                # This does NOT contain the `chat.ui(messages=)` values.
                # When restoring, the `chat.ui(messages=)` values will need to be kept
                # and the `ui.Chat(messages=)` values will need to be reset
                state.values[resolved_bookmark_id_msgs_str] = self.messages(
                    format=MISSING
                )

        # Attempt to stop the initialization of the `ui.Chat(messages=)` messages
        self._init_chat.destroy()

        @root_session.bookmark.on_restore
        async def _on_restore_ui(state: RestoreState):
            # Do not call `self.clear_messages()` as it will clear the
            # `chat.ui(messages=)` in addition to the `self.messages()`
            # (which is not what we want).

            # We always want to keep the `chat.ui(messages=)` values
            # and `self.messages()` are never initialized due to
            # calling `self._init_chat.destroy()` above

            if resolved_bookmark_id_msgs_str not in state.values:
                # If no messages to restore, display the `__init__(messages=)` messages
                await self._append_init_messages()
                return

            msgs: list[Any] = state.values[resolved_bookmark_id_msgs_str]
            if not isinstance(msgs, list):
                raise ValueError(
                    f"Bookmark value with id (`{resolved_bookmark_id_msgs_str}`) must be a list of messages."
                )

            for message_dict in msgs:
                await self.append_message(message_dict)

        def _cancel_bookmarking():
            _on_bookmark_client()
            _on_bookmark_ui()
            _on_restore_client()
            _on_restore_ui()

        # Store the callbacks to be able to destroy them later
        self._cancel_bookmarking_callbacks = _cancel_bookmarking

        return BookmarkCancelCallback(_cancel_bookmarking)


@add_example("app-express.py")
class ChatExpress(Chat):
    def ui(
        self,
        *,
        messages: Optional[Sequence[str | ChatMessageDict]] = None,
        placeholder: str = "Enter a message...",
        width: CssUnit = "min(680px, 100%)",
        height: CssUnit = "auto",
        fill: bool = True,
        icon_assistant: HTML | Tag | TagList | None = None,
        **kwargs: TagAttrValue,
    ) -> Tag:
        """
        Create a UI element for this `Chat`.

        Parameters
        ----------
        messages
            A sequence of messages to display in the chat. Each message can be either a
            string or a dictionary with `content` and `role` keys. The `content` key
            should contain the message text, and the `role` key can be "assistant" or
            "user".
        placeholder
            Placeholder text for the chat input.
        width
            The width of the UI element.
        height
            The height of the UI element.
        fill
            Whether the chat should vertically take available space inside a fillable
            container.
        icon_assistant
            The icon to use for the assistant chat messages. Can be a HTML or a tag in
            the form of :class:`~htmltools.HTML` or :class:`~htmltools.Tag`. If `None`,
            a default robot icon is used.
        kwargs
            Additional attributes for the chat container element.
        """

        return chat_ui(
            id=self.id,
            messages=messages,
            placeholder=placeholder,
            width=width,
            height=height,
            fill=fill,
            icon_assistant=icon_assistant,
            **kwargs,
        )

    def enable_bookmarking(
        self,
        client: ClientWithState | chatlas.Chat[Any, Any],
        /,
        *,
        bookmark_store: Optional[BookmarkStore] = None,
        bookmark_on: Optional[Literal["response"]] = "response",
    ) -> CancelCallback:
        """
        Enable bookmarking for the chat instance.

        This method registers `on_bookmark` and `on_restore` hooks on `session.bookmark`
        (:class:`shiny.bookmark.Bookmark`) to save/restore chat state on both the `Chat`
        and `client=` instances. In order for this method to actually work correctly, a
        `bookmark_store=` must be specified in `shiny.express.app_opts()`.

        Parameters
        ----------
        client
            The chat client instance to use for bookmarking. This can be a Chat model
            provider from [chatlas](https://posit-dev.github.io/chatlas/), or more
            generally, an instance following the `ClientWithState` protocol.
        bookmark_store
            A convenience parameter to set the `shiny.express.app_opts(bookmark_store=)`
            which is required for bookmarking (and `.enable_bookmarking()`). If `None`,
            no value will be set.
        bookmark_on
            The event to trigger the bookmarking on. Supported values include:

            - `"response"` (the default): a bookmark is triggered when the assistant is done responding.
            - `None`: no bookmark is triggered

            When this method triggers a bookmark, it also updates the URL query string to reflect the bookmarked state.

        Raises
        ------
        ValueError
            If the Shiny App does have bookmarking enabled.

        Returns
        -------
        :
            A callback to cancel the bookmarking hooks.
        """

        if bookmark_store is not None:
            from ..express import app_opts

            app_opts(bookmark_store=bookmark_store)

        return super().enable_bookmarking(client, bookmark_on=bookmark_on)


@add_example(ex_dir="../api-examples/Chat")
def chat_ui(
    id: str,
    *,
    messages: Optional[Sequence[TagChild | ChatMessageDict]] = None,
    placeholder: str = "Enter a message...",
    width: CssUnit = "min(680px, 100%)",
    height: CssUnit = "auto",
    fill: bool = True,
    icon_assistant: HTML | Tag | TagList | None = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    UI container for a chat component (Shiny Core).

    This function is for locating a :class:`~shiny.ui.Chat` instance in a Shiny Core
    app. If you are using Shiny Express, use the :method:`~shiny.ui.Chat.ui` method
    instead.

    Parameters
    ----------
    id
        A unique identifier for the chat UI.
    messages
        A sequence of messages to display in the chat. A given message can be one of the
        following:

        * A string, which is interpreted as markdown and rendered to HTML on the client.
            * To prevent interpreting as markdown, mark the string as
              :class:`~shiny.ui.HTML`.
        * A UI element (specifically, a :class:`~shiny.ui.TagChild`).
            * This includes :class:`~shiny.ui.TagList`, which take UI elements
              (including strings) as children. In this case, strings are still
              interpreted as markdown as long as they're not inside HTML.
        * A dictionary with `content` and `role` keys. The `content` key can contain a
          content as described above, and the `role` key can be "assistant" or "user".

        **NOTE:** content may include specially formatted **input suggestion** links
        (see :method:`~shiny.ui.Chat.append_message` for more info).
    placeholder
        Placeholder text for the chat input.
    width
        The width of the chat container.
    height
        The height of the chat container.
    fill
        Whether the chat should vertically take available space inside a fillable container.
    icon_assistant
            The icon to use for the assistant chat messages. Can be a HTML or a tag in
            the form of :class:`~htmltools.HTML` or :class:`~htmltools.Tag`. If `None`,
            a default robot icon is used.
    kwargs
        Additional attributes for the chat container element.
    """

    id = resolve_id(id)

    icon_attr = None
    if icon_assistant is not None:
        icon_attr = str(icon_assistant)

    icon_deps = None
    if isinstance(icon_assistant, (Tag, TagList)):
        icon_deps = icon_assistant.get_dependencies()

    message_tags: list[Tag] = []
    if messages is None:
        messages = []
    for x in messages:
        role = "assistant"
        content: TagChild = None
        if not isinstance(x, dict):
            content = x
        else:
            if "content" not in x:
                raise ValueError("Each message dictionary must have a 'content' key.")

            content = x["content"]
            if "role" in x:
                role = x["role"]

        # `content` is most likely a string, so avoid overhead in that case
        # (it's also important that we *don't escape HTML* here).
        if isinstance(content, str):
            ui: RenderedHTML = {"html": content, "dependencies": []}
        else:
            ui = TagList(content).render()

        if role == "user":
            tag_name = "shiny-user-message"
        else:
            tag_name = "shiny-chat-message"

        message_tags.append(
            Tag(
                tag_name,
                ui["dependencies"],
                content=ui["html"],
                icon=icon_attr,
            )
        )

    res = Tag(
        "shiny-chat-container",
        Tag("shiny-chat-messages", *message_tags),
        Tag(
            "shiny-chat-input",
            id=f"{id}_user_input",
            placeholder=placeholder,
        ),
        chat_deps(),
        icon_deps,
        {
            "style": css(
                width=as_css_unit(width),
                height=as_css_unit(height),
            )
        },
        id=id,
        placeholder=placeholder,
        fill=fill,
        # Also include icon on the parent so that when messages are dynamically added,
        # we know the default icon has changed
        icon_assistant=icon_attr,
        **kwargs,
    )

    if fill:
        res = as_fillable_container(as_fill_item(res))

    return res


class MessageStream:
    """
    An object to yield from a `.message_stream_context()` context manager.
    """

    def __init__(self, chat: Chat, stream_id: str):
        self._chat = chat
        self._stream_id = stream_id

    async def replace(self, message_chunk: Any):
        """
        Replace the content of the stream with new content.

        Parameters
        -----------
        message_chunk
            The new content to replace the current content.
        """
        await self._chat._append_message_chunk(
            message_chunk,
            operation="replace",
            stream_id=self._stream_id,
        )

    async def append(self, message_chunk: Any):
        """
        Append a message chunk to the stream.

        Parameters
        -----------
        message_chunk
            A message chunk to append to this stream
        """
        await self._chat._append_message_chunk(
            message_chunk,
            stream_id=self._stream_id,
        )


CHAT_INSTANCES: WeakValueDictionary[str, Chat] = WeakValueDictionary()
