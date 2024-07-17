from __future__ import annotations

import inspect
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    Literal,
    Sequence,
    Tuple,
    Union,
    cast,
    overload,
)
from weakref import WeakValueDictionary

from htmltools import HTML, Tag, TagAttrValue, css

from .. import _utils, reactive
from .._docstring import add_example
from .._namespaces import resolve_id
from ..session import require_active_session, session_context
from ..types import MISSING, MISSING_TYPE, NotifyException
from ..ui.css import CssUnit, as_css_unit
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
from ._chat_types import ChatMessage, ClientMessage, StoredMessage, TransformedMessage
from ._html_deps_py_shiny import chat_deps
from .fill import as_fill_item, as_fillable_container

__all__ = (
    "Chat",
    "chat_ui",
    "ChatMessage",
)


# TODO: UserInput might need to be a list of dicts if we want to support multiple
# user input content types
TransformUserInput = Callable[[str], Union[str, None]]
TransformUserInputAsync = Callable[[str], Awaitable[Union[str, None]]]
TransformAssistantResponse = Callable[[str], Union[str, HTML]]
TransformAssistantResponseAsync = Callable[[str], Awaitable[Union[str, HTML]]]
TransformAssistantResponseChunk = Callable[[str, str, bool], Union[str, HTML]]
TransformAssistantResponseChunkAsync = Callable[
    [str, str, bool], Awaitable[Union[str, HTML]]
]
TransformAssistantResponseFunction = Union[
    TransformAssistantResponse,
    TransformAssistantResponseAsync,
    TransformAssistantResponseChunk,
    TransformAssistantResponseChunkAsync,
]
SubmitFunction = Callable[[], None]
SubmitFunctionAsync = Callable[[], Awaitable[None]]

ChunkOption = Literal["start", "end", True, False]

PendingMessage = Tuple[Any, ChunkOption, Union[str, None]]


@add_example(ex_dir="../api-examples/chat")
class Chat:
    """
    Create a chat interface.

    A UI component for building conversational interfaces. With it, end users can submit
    messages, which will cause a `.on_user_submit()` callback to run. In that callback,
    a response can be generated based on the chat's `.messages()`, and appended to the
    chat using `.append_message()` or `.append_message_stream()`.

    Here's a rough outline for how to implement a `Chat`:

    ```python
    from shiny.express import ui

    # Create and display chat instance
    chat = ui.Chat(id="my_chat")
    chat.ui()

    # Define a callback to run when the user submits a message
    @chat.on_user_submit
    async def _():
        # Get messages currently in the chat
        messages = chat.messages()
        # Create a response message stream
        response = await my_model.generate_response(messages, stream=True)
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

    Parameters
    ----------
    id
        A unique identifier for the chat session. In Shiny Core, make sure this id
        matches a corresponding :func:`~shiny.ui.chat_ui` call in the UI.
    messages
        A sequence of messages to display in the chat. Each message can be a
        dictionary with a `content` and `role` key. The `content` key should contain
        the message text, and the `role` key can be "assistant", "user", or "system".
        Note that system messages are not actually displayed in the chat, but will
        still be stored in the chat's `.messages()`.
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
        `token_limits` in `.messages()`. By default, a pre-trained tokenizer is
        attempted to be loaded the tokenizers library (if available). A custom tokenizer
        can be provided by following the `TokenEncoding` (tiktoken or tozenizer)
        protocol. If token limits are of no concern, provide `None`.
    """

    def __init__(
        self,
        id: str,
        *,
        messages: Sequence[Any] = (),
        on_error: Literal["auto", "actual", "sanitize", "unhandled"] = "auto",
        tokenizer: TokenEncoding | MISSING_TYPE | None = MISSING,
    ):

        self.id = id
        self.user_input_id = f"{id}_user_input"
        self._transform_user: TransformUserInputAsync | None = None
        self._transform_assistant: TransformAssistantResponseChunkAsync | None = None
        if isinstance(tokenizer, MISSING_TYPE):
            self._tokenizer = get_default_tokenizer()
        else:
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
        self._current_stream_message = ""
        self._current_stream_id: str | None = None
        self._pending_messages: list[PendingMessage] = []

        # If a user input message is transformed into a response, we need to cancel
        # the next user input submit handling
        self._suspend_input_handler: bool = False

        # Keep track of effects so we can destroy them when the chat is destroyed
        self._effects: list[reactive.Effect_] = []

        # Initialize chat state and user input effect
        with session_context(self._session):
            # Initialize message state
            self._messages: reactive.Value[tuple[StoredMessage, ...]] = reactive.Value(
                ()
            )

            self._latest_user_input: reactive.Value[StoredMessage | None] = (
                reactive.Value(None)
            )

            # Initialize the chat with the provided messages
            @reactive.effect
            async def _init_chat():
                for msg in messages:
                    await self.append_message(msg)

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
                    self._store_message(as_transformed_message(msg), index=n_pre)
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

    def ui(
        self,
        *,
        placeholder: str = "Enter a message...",
        width: CssUnit = "min(680px, 100%)",
        height: CssUnit = "auto",
        fill: bool = True,
        **kwargs: TagAttrValue,
    ) -> Tag:
        """
        Place a chat component in the UI.

        This method is only relevant fpr Shiny Express. In Shiny Core, use
        :func:`~shiny.ui.chat_ui` instead to insert the chat UI.

        Parameters
        ----------
        placeholder
            Placeholder text for the chat input.
        width
            The width of the chat container.
        height
            The height of the chat container.
        fill
            Whether the chat should vertically take available space inside a fillable
            container.
        kwargs
            Additional attributes for the chat container element.
        """
        return chat_ui(
            id=self.id,
            placeholder=placeholder,
            width=width,
            height=height,
            fill=fill,
            **kwargs,
        )

    @overload
    def on_user_submit(
        self, fn: SubmitFunction | SubmitFunctionAsync
    ) -> reactive.Effect_: ...

    @overload
    def on_user_submit(
        self,
    ) -> Callable[[SubmitFunction | SubmitFunctionAsync], reactive.Effect_]: ...

    def on_user_submit(
        self, fn: SubmitFunction | SubmitFunctionAsync | None = None
    ) -> (
        reactive.Effect_
        | Callable[[SubmitFunction | SubmitFunctionAsync], reactive.Effect_]
    ):
        """
        Define a function to invoke when user input is submitted.

        Apply this method as a decorator to a function (`fn`) that should be invoked when the
        user submits a message. The function should take no arguments.

        In many cases, the implementation of `fn` should do at least the following:

        1. Call `.messages()` to obtain the current chat history.
        2. Generate a response based on those messages.
        3. Append the response to the chat history using `.append_message()` (
           or `.append_message_stream()` if the response is streamed).

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

        def create_effect(fn: SubmitFunction | SubmitFunctionAsync):
            afunc = _utils.wrap_async(fn)

            @reactive.effect
            @reactive.event(self._user_input)
            async def handle_user_input():
                if self._suspend_input_handler:
                    from .. import req

                    req(False)
                try:
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
            raise NotifyException(str(e), sanitize=sanitize)

    @overload
    def messages(
        self,
        *,
        format: Literal["anthropic"] = "anthropic",
        token_limits: tuple[int, int] | None = (4096, 1000),
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[AnthropicMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: Literal["google"] = "google",
        token_limits: tuple[int, int] | None = (4096, 1000),
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[GoogleMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: Literal["langchain"] = "langchain",
        token_limits: tuple[int, int] | None = (4096, 1000),
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[LangChainMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: Literal["openai"] = "openai",
        token_limits: tuple[int, int] | None = (4096, 1000),
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[OpenAIMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: Literal["ollama"] = "ollama",
        token_limits: tuple[int, int] | None = (4096, 1000),
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[OllamaMessage, ...]: ...

    @overload
    def messages(
        self,
        *,
        format: MISSING_TYPE = MISSING,
        token_limits: tuple[int, int] | None = (4096, 1000),
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[ChatMessage, ...]: ...

    def messages(
        self,
        *,
        format: MISSING_TYPE | ProviderMessageFormat = MISSING,
        token_limits: tuple[int, int] | None = (4096, 1000),
        transform_user: Literal["all", "last", "none"] = "all",
        transform_assistant: bool = False,
    ) -> tuple[ChatMessage | ProviderMessage, ...]:
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
            A tuple of two integers. The first integer is the maximum number of tokens
            that can be sent to the model in a single request. The second integer is the
            amount of tokens to reserve for the model's response.
            Can also be `None` to disable message trimming based on token counts.
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
        if token_limits is not None:
            messages = self._trim_messages(messages, token_limits, format)

        res: list[ChatMessage | ProviderMessage] = []
        for i, m in enumerate(messages):
            transform = False
            if m["role"] == "assistant":
                transform = transform_assistant
            elif m["role"] == "user":
                transform = transform_user == "all" or (
                    transform_user == "last" and i == len(messages) - 1
                )
            content_key = m["transform_key" if transform else "pre_transform_key"]
            chat_msg = ChatMessage(content=m[content_key], role=m["role"])
            if not isinstance(format, MISSING_TYPE):
                chat_msg = as_provider_message(chat_msg, format)
            res.append(chat_msg)

        return tuple(res)

    async def append_message(self, message: Any) -> None:
        """
        Append a message to the chat.

        Parameters
        ----------
        message
            The message to append. A variety of message formats are supported including
            a string, a dictionary with `content` and `role` keys, or a relevant chat
            completion object from platforms like OpenAI, Anthropic, Ollama, and others.

        Note
        ----
        Use `.append_message_stream()` instead of this method when `stream=True` (or
        similar) is specified in model's completion method.
        """
        await self._append_message(message)

    async def _append_message(
        self, message: Any, *, chunk: ChunkOption = False, stream_id: str | None = None
    ) -> None:
        # If currently we're in a stream, handle other messages (outside the stream) later
        if not self._can_append_message(stream_id):
            self._pending_messages.append((message, chunk, stream_id))
            return

        # Update current stream state
        self._current_stream_id = stream_id
        if chunk == "end":
            self._current_stream_id = None

        if chunk is False:
            msg = normalize_message(message)
            chunk_content = None
        else:
            msg = normalize_message_chunk(message)
            # Update the current stream message
            chunk_content = msg["content"]
            self._current_stream_message += chunk_content
            msg["content"] = self._current_stream_message
            if chunk == "end":
                self._current_stream_message = ""

        msg = await self._transform_message(
            msg, chunk=chunk, chunk_content=chunk_content
        )
        if msg is None:
            return
        msg = self._store_message(msg, chunk=chunk)
        await self._send_append_message(msg, chunk=chunk)

    async def append_message_stream(self, message: Iterable[Any] | AsyncIterable[Any]):
        """
        Append a message as a stream of message chunks.

        Parameters
        ----------
        message
            An iterable or async iterable of message chunks to append. A variety of
            message chunk formats are supported, including a string, a dictionary with
            `content` and `role` keys, or a relevant chat completion object from
            platforms like OpenAI, Anthropic, Ollama, and others.

        Note
        ----
        Use this method (over `.append_message()`) when `stream=True` (or similar) is
        specified in model's completion method.
        """

        message = _utils.wrap_async_iterable(message)

        # Run the stream in the background to get non-blocking behavior
        @reactive.extended_task
        async def _stream_task():
            await self._append_message_stream(message)

        _stream_task()

        # Since the task runs in the background (outside/beyond the current context,
        # if any), we need to manually raise any exceptions that occur
        try:
            ctx = reactive.get_current_context()
        except Exception:
            return

        @reactive.effect
        async def _handle_error():
            e = _stream_task.error()
            if e:
                await self._raise_exception(e)

        ctx.on_invalidate(_handle_error.destroy)
        self._effects.append(_handle_error)

    async def _append_message_stream(self, message: AsyncIterable[Any]):
        id = _utils.private_random_id()

        empty = ChatMessage(content="", role="assistant")
        await self._append_message(empty, chunk="start", stream_id=id)

        try:
            async for msg in message:
                await self._append_message(msg, chunk=True, stream_id=id)
        finally:
            await self._append_message(empty, chunk="end", stream_id=id)
            await self._flush_pending_messages()

    async def _flush_pending_messages(self):
        still_pending: list[PendingMessage] = []
        for msg, chunk, stream_id in self._pending_messages:
            if self._can_append_message(stream_id):
                await self._append_message(msg, chunk=chunk, stream_id=stream_id)
            else:
                still_pending.append((msg, chunk, stream_id))
        self._pending_messages = still_pending

    def _can_append_message(self, stream_id: str | None) -> bool:
        if self._current_stream_id is None:
            return True
        return self._current_stream_id == stream_id

    # Send a message to the UI
    async def _send_append_message(
        self,
        message: StoredMessage,
        chunk: ChunkOption = False,
    ):
        if message["role"] == "system":
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

        content = message["content_client"]
        content_type = "html" if isinstance(content, HTML) else "markdown"

        msg = ClientMessage(
            content=content,
            role=message["role"],
            content_type=content_type,
            chunk_type=chunk_type,
        )

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
            A function that takes a string and returns a string or
            :class:`shiny.ui.HTML`. If `fn` returns a string, it gets interpreted and
            parsed as a markdown on the client (and the resulting HTML is then
            sanitized). If `fn` returns :class:`shiny.ui.HTML`, it will be displayed
            as-is.

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
        chunk_content: str | None = None,
    ) -> TransformedMessage | None:

        res = as_transformed_message(message)
        key = res["transform_key"]

        if message["role"] == "user" and self._transform_user is not None:
            content = await self._transform_user(message["content"])
            if content is None:
                return None
            res[key] = content

        elif message["role"] == "assistant" and self._transform_assistant is not None:
            res[key] = await self._transform_assistant(
                message["content"],
                chunk_content or "",
                chunk == "end" or chunk is False,
            )

        return res

    # Just before storing, handle chunk msg type and calculate tokens
    def _store_message(
        self,
        message: TransformedMessage,
        chunk: ChunkOption = False,
        index: int | None = None,
    ) -> StoredMessage:

        msg: StoredMessage = {
            **message,
            "token_count": None,
        }

        # Don't actually store chunks until the end
        if chunk is True or chunk == "start":
            return msg

        if self._tokenizer is not None:
            encoded = self._tokenizer.encode(msg["content_server"])
            if isinstance(encoded, TokenizersEncoding):
                token_count = len(encoded.ids)
            else:
                token_count = len(encoded)
            msg["token_count"] = token_count

        with reactive.isolate():
            messages = self._messages()

        if index is None:
            index = len(messages)

        messages = list(messages)
        messages.insert(index, msg)

        self._messages.set(tuple(messages))
        if msg["role"] == "user":
            self._latest_user_input.set(msg)

        return msg

    @staticmethod
    def _trim_messages(
        messages: tuple[StoredMessage, ...],
        token_limits: tuple[int, int],
        format: MISSING_TYPE | ProviderMessageFormat,
    ) -> tuple[StoredMessage, ...]:

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
        for m in messages:
            count = m["token_count"]
            # Count can be None if the tokenizer is None
            if count is None:
                return messages
            if m["role"] == "system":
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

        messages2: list[StoredMessage] = []
        n_other_messages2: int = 0
        for m in reversed(messages):
            if m["role"] == "system":
                messages2.append(m)
                continue
            count = cast(int, m["token_count"])  # Already checked this
            remaining_non_system_tokens -= count
            if remaining_non_system_tokens >= 0:
                messages2.append(m)
                n_other_messages2 += 1

        # Anthropic doesn't support `role: system` and requires a user message to come 1st
        if format == "anthropic":
            if n_system_messages > 0:
                raise ValueError(
                    "Anthropic requires a system prompt to be specified in it's `.create()` method "
                    "(not in the chat messages with `role: system`)."
                )
            while n_other_messages2 > 0 and messages2[-1]["role"] != "user":
                messages2.pop()
                n_other_messages2 -= 1

        messages2.reverse()

        if len(messages2) == n_system_messages and n_other_messages2 > 0:
            raise ValueError(
                f"Only system messages fit within `.messages(token_limits={token_limits})`. "
                "Consider increasing the 1st value of `token_limit` or setting it to "
                "`token_limit=None` to disable token limits."
            )

        return tuple(messages2)

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
        return msg[key]

    def _user_input(self) -> str:
        id = self.user_input_id
        return cast(str, self._session.input[id]())

    def set_user_message(self, value: str):
        """
        Set the user's message.

        Parameters
        ----------
        value
            The value to set the user input to.
        """

        _utils.run_coro_sync(
            self._session.send_custom_message(
                "shinyChatMessage",
                {
                    "id": self.id,
                    "handler": "shiny-chat-set-user-input",
                    "obj": value,
                },
            )
        )

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
        for x in self._effects:
            x.destroy()
        self._effects.clear()

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


@add_example(ex_dir="../api-examples/chat")
def chat_ui(
    id: str,
    *,
    placeholder: str = "Enter a message...",
    width: CssUnit = "min(680px, 100%)",
    height: CssUnit = "auto",
    fill: bool = True,
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
    placeholder
        Placeholder text for the chat input.
    width
        The width of the chat container.
    height
        The height of the chat container.
    fill
        Whether the chat should vertically take available space inside a fillable container.
    kwargs
        Additional attributes for the chat container element.
    """

    id = resolve_id(id)

    res = Tag(
        "shiny-chat-container",
        chat_deps(),
        {
            "style": css(
                width=as_css_unit(width),
                height=as_css_unit(height),
            )
        },
        id=id,
        placeholder=placeholder,
        fill=fill,
        **kwargs,
    )

    if fill:
        res = as_fillable_container(as_fill_item(res))

    return res


def as_transformed_message(message: ChatMessage) -> TransformedMessage:
    if message["role"] == "user":
        transform_key = "content_server"
        pre_transform_key = "content_client"
    else:
        transform_key = "content_client"
        pre_transform_key = "content_server"

    return TransformedMessage(
        content_client=message["content"],
        content_server=message["content"],
        role=message["role"],
        transform_key=transform_key,
        pre_transform_key=pre_transform_key,
    )


CHAT_INSTANCES: WeakValueDictionary[str, Chat] = WeakValueDictionary()
