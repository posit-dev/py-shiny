from __future__ import annotations

from typing import (
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

from htmltools import HTML, Tag, TagAttrValue, css

from .. import _utils, reactive
from .._docstring import add_example
from .._namespaces import resolve_id
from ..session import Session, require_active_session, session_context
from ..types import MISSING, MISSING_TYPE, NotifyException
from ..ui.css import CssUnit, as_css_unit
from ._chat_normalize import normalize_message, normalize_message_chunk
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
SubmitFunction = Callable[[], None]
SubmitFunctionAsync = Callable[[], Awaitable[None]]

ChunkOption = Literal["start", "end", True, False]

PendingMessage = Tuple[Any, ChunkOption, Union[str, None]]


@add_example(ex_dir="../api-examples/chat")
class Chat:
    """
    Create a chat interface.

    The chat interface is a component that allows users to submit messages and receive
    responses. The chat interface can be used to build conversational AI applications,
    chatbots, and more.

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
        still be stored in the chat's `.get_messages()`.
    on_error
        How to handle errors that occur in response to user input. For options 1-3, the
        error message is displayed to the user and the app continues to run. For option
        4, the error message is not displayed, and the app stops:

        * "auto": Sanitize the error message if the app is set to sanitize errors, otherwise display the actual error message.
        * "sanitize": Sanitize the error message before displaying it to the user.
        * "actual": Display the actual error message to the user.
        * "unhandled": Do not display any error message to the user.

    tokenizer
        The tokenizer to use for calculating token counts, which is required to impose
        `token_limits` in `.get_messages()`. By default, a pre-trained tokenizer is
        attempted to be loaded the tokenizers library (if available). A custom tokenizer
        can be provided by following the `TokenEncoding` (tiktoken or tozenizer)
        protocol. If token limits are of no concern, provide `None`.
    session
        The :class:`~shiny.Session` instance that the chat should appear in. If not
        provided, the session is inferred via :func:`~shiny.session.get_current_session`.
    """

    def __init__(
        self,
        id: str,
        *,
        messages: Sequence[ChatMessage] = (),
        on_error: Literal["auto", "sanitize", "actual", "unhandled"] = "auto",
        tokenizer: TokenEncoding | MISSING_TYPE | None = MISSING,
        session: Optional[Session] = None,
    ):

        self.id = id
        self.user_input_id = f"{id}_user_input"
        self._transform_user: TransformUserInputAsync | None = None
        self._transform_assistant: TransformAssistantResponseAsync | None = None
        if isinstance(tokenizer, MISSING_TYPE):
            self._tokenizer = get_default_tokenizer()
        else:
            self._tokenizer = tokenizer
        self._session = require_active_session(session)

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

            # Initialize the chat with the provided messages
            for msg in messages:
                _utils.run_coro_sync(self.append_message(msg))

            # When user input is submitted, transform, and store it in the chat state
            # (and make sure this runs before other effects since when the user
            #  calls `.get_messages()`, they should get the latest user input)
            @reactive.effect(priority=9999)
            @reactive.event(self._get_user_input)
            async def _on_user_input():
                msg = ChatMessage(content=self._get_user_input(), role="user")
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

        This method is only available in Shiny Express. In Shiny Core, use
        :func:`~shiny.ui.chat_ui` instead.

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

        if not _express_is_active():
            raise RuntimeError(
                "The `ui()` method of the `ui.Chat` class only works in a Shiny Express context."
                " Use `ui.chat_ui()` instead in Shiny Core to locate the chat UI."
            )
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

        1. Call `.get_messages()` to obtain the current chat history.
        2. Generate a response based on those messages.
        3. Append the response to the chat history using `.append_message()` or `.append_message_stream()`.

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
            @reactive.event(self._get_user_input)
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

    def get_messages(
        self,
        *,
        token_limits: tuple[int, int] | None = (4096, 1000),
        apply_user_transform: bool = True,
        apply_assistant_transform: bool = False,
    ) -> tuple[ChatMessage, ...]:
        """
        Reactively read chat messages

        Obtain the current chat history within a reactive context. Messages are listed
        in the order they were added. As a result, when this method is called in a
        `.on_user_submit()` callback (as it most often is), the last message will be the
        most recent one submitted by the user.

        Parameters
        ----------
        token_limits
            A tuple of two integers. The first integer is the maximum number of tokens
            that can be sent to the model in a single request. The second integer is the
            amount of tokens to reserve for the model's response.
            Can also be `None` to disable message trimming based on token counts.
        apply_user_transform
            Whether to return user input messages with transformation applied. This only
            matters if a `user_input_transform` was provided to the chat constructor.
            This should be `True` when passing the messages to a model for response
            generation, but `False` when you need (to save) the original user input.
        apply_assistant_transform
            Whether to return assistant messages with transformation applied. This only
            matters if an `assistant_response_transform` was provided to the chat
            constructor.

        Returns
        -------
        A sequence of chat messages.
        """

        messages = self._get_trimmed_messages(token_limits=token_limits)

        res: list[ChatMessage] = []
        for m in messages:
            msg = ChatMessage(content=m["content"], role=m["role"])
            original = (apply_user_transform and m["role"] == "user") or (
                apply_assistant_transform and m["role"] == "assistant"
            )
            if original:
                msg["content"] = m["original_content"] or m["content"]
            res.append(msg)

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

        if not chunk:
            msg = normalize_message(message)
        else:
            msg = normalize_message_chunk(message)
            # Update the current stream message
            self._current_stream_message += msg["content"]
            msg["content"] = self._current_stream_message
            if chunk == "end":
                self._current_stream_message = ""

        msg = await self._transform_message(msg)
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

        msg = ClientMessage(
            content=message["content"],
            role=message["role"],
            content_type=message.get("content_type", "markdown"),
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
        Define a function to transform user input.

        Apply this method as a decorator to a function (`fn`) that transforms user input
        before storing it in the chat messages returned by `.get_messages()`. This is
        useful for implementing RAG workflows, like taking a URL and scraping it for
        text before sending it to the model.

        Parameters
        ----------
        fn
            A function to transform user input before storing it in the chat messages
            returned by `.get_messages()`. If `fn` returns `None`, the user input is
            effectively ignored, and `.on_user_submit()` callbacks are suspended until
            more input is submitted. This behavior is often useful to catch and handle
            errors that occur during transformation. In this case, the transform
            function should append an error message to the chat (via
            `.append_message()`) to inform the user of the error.
        """

        def _set_transform(fn: TransformUserInput | TransformUserInputAsync):
            self._transform_user = _utils.wrap_async(fn)

        if fn is None:
            return _set_transform
        else:
            return _set_transform(fn)

    @overload
    def transform_assistant_response(
        self, fn: TransformAssistantResponse | TransformAssistantResponseAsync
    ) -> None: ...

    @overload
    def transform_assistant_response(
        self,
    ) -> Callable[
        [TransformAssistantResponse | TransformAssistantResponseAsync], None
    ]: ...

    def transform_assistant_response(
        self,
        fn: TransformAssistantResponse | TransformAssistantResponseAsync | None = None,
    ) -> (
        None
        | Callable[[TransformAssistantResponse | TransformAssistantResponseAsync], None]
    ):
        """
        Define a function to transform assistant responses.

        Apply this method as a decorator to a function (`fn`) that transforms assistant
        responses before displaying them in the chat. This is useful for post-processing
        model responses before displaying them to the user.

        Parameters
        ----------
        fn
            A function to transform role="assistant" messages. If the function returns a
            string, it will be interpreted and parsed as a markdown string on the client
            (and the resulting HTML is then sanitized). If the function returns
            :class:`shiny.ui.HTML`, it will be displayed as-is. Note that, for
            `.append_message_stream()`, the transformer will be applied to each message
            in the stream, so it should be performant.
        """

        def _set_transform(
            fn: TransformAssistantResponse | TransformAssistantResponseAsync,
        ):
            self._transform_assistant = _utils.wrap_async(fn)

        if fn is None:
            return _set_transform
        else:
            return _set_transform(fn)

    async def _transform_message(
        self, message: ChatMessage
    ) -> TransformedMessage | None:

        res: TransformedMessage = {
            **message,
            "original_content": None,
            "content_type": "markdown",
        }

        original_content = message["content"]
        content = original_content

        if message["role"] == "user" and self._transform_user is not None:
            content = await self._transform_user(original_content)

        elif message["role"] == "assistant" and self._transform_assistant is not None:
            content = await self._transform_assistant(original_content)
            if isinstance(content, HTML):
                res["content_type"] = "html"

        if content is None:
            return None

        if original_content != content:
            res["original_content"] = content

        res["content"] = content

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
            # Always tokenize the "original" content for assistant messages
            if msg["role"] == "assistant":
                content = msg["original_content"] or msg["content"]
            else:
                content = msg["content"]
            encoded = self._tokenizer.encode(content)
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

        return msg

    def _get_trimmed_messages(
        self,
        *,
        token_limits: tuple[int, int] | None = (4096, 1000),
    ) -> tuple[StoredMessage, ...]:
        messages = self._messages()

        if token_limits is None:
            return messages

        # Can't trim if we don't have token counts
        token_counts = [m["token_count"] for m in messages]
        if None in token_counts:
            return messages

        token_counts = cast("list[int]", token_counts)

        # Take the newest messages up to the token limit
        limit, reserve = token_limits
        max_tokens = limit - reserve
        messages2: list[StoredMessage] = []
        for i, m in enumerate(reversed(messages)):
            if sum(token_counts[-i - 1 :]) > max_tokens:
                break
            messages2.append(m)

        messages2.reverse()

        return tuple(messages2)

    # TODO: Barret; can we make this sync?
    async def get_user_input(self, transform: bool = True) -> str | None:
        """
        Reactively read the user's message.

        Parameters
        ----------
        transform
            Whether to apply the user input transformation function (if one was
            provided).

        Returns
        -------
        The user input message (before any transformation).

        Note
        ----
        Most users shouldn't need to use this method directly since the last item in
        `.get_messages()` contains the most recent user input. It can be useful for:

          1. Taking a reactive dependency on the user's input outside of a `.on_user_submit()` callback.
          2. Maintaining message state separately from `.get_messages()`.

        """
        val = self._get_user_input()
        if transform and self._transform_user is not None:
            return await self._transform_user(val)
        else:
            return val

    def _get_user_input(self) -> str:
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


def _express_is_active() -> bool:
    from ..express._run import get_top_level_recall_context_manager

    try:
        get_top_level_recall_context_manager()
        return True
    except RuntimeError:
        return False


def as_transformed_message(message: ChatMessage) -> TransformedMessage:
    return TransformedMessage(
        **message,
        original_content=None,
        content_type="markdown",
    )


CHAT_INSTANCES: WeakValueDictionary[str, Chat] = WeakValueDictionary()
