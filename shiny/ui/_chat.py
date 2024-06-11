import copy
import warnings
from typing import (
    AbstractSet,
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Collection,
    Generic,
    Iterable,
    Literal,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    Union,
    cast,
    overload,
)

from htmltools import HTML, Tag

from .. import _utils, reactive
from .._namespaces import resolve_id
from ..session import Session, require_active_session, session_context
from ..types import MISSING, MISSING_TYPE, NotifyException
from ._chat_types import (
    ChatMessage,
    ChatMessageChunk,
    normalize_message,
    normalize_message_chunk,
)
from ._html_deps_py_shiny import chat_deps
from .fill import as_fill_item, as_fillable_container

__all__ = (
    "Chat",
    "chat_ui",
    "ChatMessage",
    "ChatMessageChunk",
)

T = TypeVar("T")

SubmitFunction = Callable[[], None]
SubmitFunctionAsync = Callable[[], Awaitable[None]]


# A duck type for tiktoken.Encoding
class TiktokEncoding(Protocol):
    def encode(
        self,
        text: str,
        *,
        allowed_special: Union[Literal["all"], AbstractSet[str]] = set(),  # noqa: B006
        disallowed_special: Union[Literal["all"], Collection[str]] = "all",
    ) -> list[int]: ...


class Chat(Generic[T]):
    """
    Create a chat component.

    Creates a chat component for displaying and receiving messages. The chat can be
    used to build conversational interfaces, like chatbots.

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
    encoding
        The encoding method to use for tokenizing messages. This is used to enforce
        token limits on messages sent to the model. Any encoder that implements
        tiktoken's `Encoding` protocol can be used. If not provided, a warning is
        displayed when the chat is created. To disable the warning, set `encoding=None`.
    token_limits
        A tuple of two integers. The first integer is the maximum number of tokens
        that can be sent to the model in a single request. The second integer is the
        amount of tokens to reserve for the model's response.
    user_input_transformer
        A function to transform user input before storing it in the chat `.messages()`
        history. This is useful for implementing RAG workflows, like taking a URL and
        scraping it for text before sending it to the model.
    assistant_response_transformer
        A function to transform role="assistant" messages for display purposes.
        If the function returns a string, it will be interpreted and parsed as a markdown
        string on the client (and the resulting HTML is then sanitized). If the function
        returns HTML, it will be displayed as-is. Note that, for `.append_message_stream()`,
        the transformer will be applied to each message in the stream, so it should be
        performant. By default, assistant responses are interpreted as markdown on the client.
    session
        The :class:`~shiny.Session` instance that the chat should appear in. If not
        provided, the session is inferred via :func:`~shiny.session.get_current_session`.
    """

    def __init__(
        self,
        id: str,
        *,
        messages: Sequence[ChatMessage] = (),
        encoding: TiktokEncoding | MISSING_TYPE | None = MISSING,
        token_limits: tuple[int, int] = (4096, 400),
        user_input_transformer: (
            Callable[[str], str] | Callable[[str], Awaitable[str]]
        ) = lambda x: x,
        assistant_response_transformer: (
            Callable[[str], str | HTML]
            | Callable[[str], Awaitable[str | HTML]]
            | MISSING_TYPE
        ) = MISSING,
        session: Optional[Session] = None,
    ):

        self.id = id
        self.user_input_id = f"{id}_user_input"
        if isinstance(encoding, MISSING_TYPE):
            warnings.warn(
                "Without an `encoding`, `Chat` won't be able to enforce token limits. "
                "Consider using `tiktoken` to get an encoding for the relevant model "
                "or set to `None` to disable this warning.",
                stacklevel=2,
            )
            encoding = None
        self._encoding = encoding
        self._token_limits = token_limits
        self._token_counts: list[int] = []
        self._user_transformer = _utils.wrap_async(user_input_transformer)
        if isinstance(assistant_response_transformer, MISSING_TYPE):
            self._assistant_transformer = None
        else:
            self._assistant_transformer = _utils.wrap_async(
                assistant_response_transformer
            )
        self._session = require_active_session(session)

        # Chunked messages get accumulated (using this property) before changing state
        self._final_message = ""

        # Keep track of effects so we can destroy them when the chat is destroyed
        self._effects: list[reactive.Effect_] = []

        with session_context(self._session):
            # Initialize message state
            self._messages: reactive.Value[Sequence[ChatMessage]] = reactive.Value(())

            # Store (i.e. append) message state and display non-system messages
            for msg in messages:
                msg = normalize_message(msg)
                self._store_message(msg)
                if msg["role"] != "system":
                    _utils.run_coro_sync(self._send_message(msg))

            # When user input is submitted, transform, and store it in the chat state
            # (and make sure this runs before other effects since when the user
            #  calls `.messages()`, they should get the latest user input)
            @reactive.effect(priority=9999)
            @reactive.event(self.get_user_input)
            async def _store_user_input():
                input = self.get_user_input()
                content = await self._user_transformer(input)
                user_msg = ChatMessage(
                    content=content, role="user", original_content=input
                )
                self._store_message(user_msg)

            self._effects.append(_store_user_input)

    def ui(
        self,
        placeholder: str = "Enter a message...",
        width: str = "min(680px, 100%)",
        fill: bool = True,
    ) -> Tag:
        """
        Display/locate the chat component in the UI.

        This method is only available in Shiny Express. In Shiny Core, use
        :func:`~shiny.ui.chat_ui` instead.

        Parameters
        ----------
        placeholder
            The placeholder text to display in the chat input.
        width
            The width of the chat container.
        fill
            Whether the chat should fill a fillable container.
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
            fill=fill,
        )

    @overload
    def on_user_submit(
        self,
        fn: SubmitFunction | SubmitFunctionAsync,
        *,
        on_error: Literal["sanitize", "actual", "unhandled"] = "sanitize",
    ) -> reactive.Effect_: ...

    @overload
    def on_user_submit(
        self,
    ) -> Callable[[SubmitFunction | SubmitFunctionAsync], reactive.Effect_]: ...

    def on_user_submit(
        self,
        fn: SubmitFunction | SubmitFunctionAsync | None = None,
        *,
        on_error: Literal["sanitize", "actual", "unhandled"] = "sanitize",
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
            3. Append the response to the chat history using `.append_message()` or
              `.append_message_stream()`.

        Parameters
        ----------
        fn
            A function to invoke when user input is submitted.
        on_error
            How to handle errors that occur in response to user input. For options
            1 and 2, the error message is displayed to the user and the app continues
            to run. For option 3, the error message is not displayed, and the app stops:
            - "sanitize": Sanitize the error message before displaying it to the user.
            - "actual": Display the actual error message to the user.
            - "unhandled": Do not display any error message to the user.

        Note
        ----
        This method creates a reactive effect that only gets invalidated when the user
        submits a message. Thus, the function `fn` can read other reactive dependencies,
        but it will only be re-invoked when the user submits a message.
        """

        def create_effect(fn: SubmitFunction | SubmitFunctionAsync):
            afunc = _utils.wrap_async(fn)

            @reactive.effect
            @reactive.event(self.get_user_input)
            async def handle_user_input():
                if on_error == "unhandled":
                    await afunc()
                else:
                    try:
                        await afunc()
                    except Exception as e:
                        await self._remove_loading_message()
                        sanitize = on_error == "sanitize"
                        raise NotifyException(str(e), sanitize=sanitize)

            self._effects.append(handle_user_input)

            return handle_user_input

        if fn is None:
            return create_effect
        else:
            return create_effect(fn)

    def get_user_input(self) -> str:
        """
        Reactively read user input

        Returns
        -------
        The user input message (before any transformation).

        Note
        ----
        Most users shouldn't need to use this method directly since `.messages()`
        contains user input. However, this method can be useful when you need to access
        the un-transformed user input, and/or when you want to take a reactive
        dependency on user input.
        """
        id = self.user_input_id
        return cast(str, self._session.input[id]())

    def get_messages(
        self, user_input_transformed: bool = True
    ) -> Sequence[ChatMessage]:
        """
        Reactively read chat messages

        Obtain the current chat history within a reactive context. Messages are listed
        in the order they were added. As a result, when this method is called in a
        `.on_user_submit()` callback (as it most often is), the last message will be the
        most recent one submitted by the user.

        Parameters
        ----------
        user_input_transformed
            Whether to return user input messages with the transformation applied. This
            should be `True` when using the messages for generating responses, and `False`
            when you need (to save) the original user input.

        Returns
        -------
        A sequence of chat messages.
        """
        messages = self._messages()
        if user_input_transformed:
            # TODO: drop the original_content field?
            return messages
        else:
            # Move the original content to the content field for user messages
            messages2 = copy.copy(messages)
            for msg in messages2:
                msg["content"] = msg.get("original_content", msg["content"])
            return messages2

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

    async def _append_message(self, message: Any, *, chunk: bool = False) -> None:
        if chunk:
            msg = normalize_message_chunk(message)
            self._store_message_chunk(msg)
        else:
            msg = normalize_message(message)
            self._store_message(msg)

        await self._send_message(msg, chunk=chunk)

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

        @reactive.extended_task
        async def _do_stream():
            await self._append_message_stream(message)

        _do_stream()

    async def _append_message_stream(self, message: AsyncIterable[Any]):
        # Get the first message just to determine the role
        miter = message.__aiter__()
        msg_first = await miter.__anext__()
        role = normalize_message_chunk(msg_first)["role"]

        # Start the message
        msg_start = ChatMessageChunk(content="", chunk_type="message_start", role=role)
        await self._append_message(msg_start, chunk=True)

        try:
            async for msg in message:
                msg = normalize_message_chunk(msg)
                await self._append_message(msg, chunk=True)
        finally:
            msg_end = ChatMessageChunk(content="", chunk_type="message_end", role=role)
            await self._append_message(msg_end, chunk=True)

    # Send a message to the UI
    async def _send_message(
        self, message: ChatMessage | ChatMessageChunk, chunk: bool = False
    ):
        if callable(self._assistant_transformer) and message["role"] == "assistant":
            message["content"] = await self._assistant_transformer(message["content"])
            if isinstance(message["content"], HTML):
                message["content_type"] = "html"

        # print(message)

        if chunk:
            msg_type = "shiny-chat-append-message-chunk"
        else:
            msg_type = "shiny-chat-append-message"

        await self._send_custom_message(msg_type, message)
        # TODO: Joe said it's a good idea to yield here, but I'm not sure why?
        # await asyncio.sleep(0)

    # Store a message in the chat state
    def _store_message(self, message: ChatMessage):
        # Get the (current and new) messages
        with reactive.isolate():
            messages = tuple(self._messages()) + (message,)

        # Exit early if we don't have an encoder / token count
        if self._encoding is None:
            self._messages.set(messages)
            return

        # Otherwise, calculate the token count, and possibly
        # remove older messages to stay within the token limit
        token_count = len(self._encoding.encode(message["content"]))
        self._token_counts.append(token_count)

        # Take the newest messages up to the token limit
        limit, reserve = self._token_limits
        max_tokens = limit - reserve
        messages2: list[ChatMessage] = []
        for i, message in enumerate(reversed(messages)):
            if sum(self._token_counts[-i - 1 :]) > max_tokens:
                self._token_counts = self._token_counts[-i:]
                break
            messages2.append(message)

        messages2.reverse()

        self._messages.set(tuple(messages2))

    # For chunk messages, accumulate the chunks until we have a signal that the message
    # has ended
    def _store_message_chunk(self, msg: ChatMessageChunk):
        self._final_message += msg["content"]
        if "chunk_type" in msg and msg["chunk_type"] == "message_end":
            final = ChatMessage(content=self._final_message, role=msg["role"])
            self._store_message(final)
            self._final_message = ""

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

    async def _remove_loading_message(self):
        await self._send_custom_message("shiny-chat-remove-loading-message", None)

    async def _send_custom_message(
        self, handler: str, obj: ChatMessage | ChatMessageChunk | None
    ):
        await self._session.send_custom_message(
            "shinyChatMessage",
            {
                "id": self.id,
                "handler": handler,
                "obj": obj,
            },
        )


def chat_ui(
    id: str,
    placeholder: str = "Enter a message...",
    width: str = "min(680px, 100%)",
    fill: bool = True,
) -> Tag:
    """
    UI container for a chat component (Shiny Core).

    This function is for locating a :class:`~shiny.ui.Chat` instance in a Shiny Core
    app. If you are using Shiny Express, you should use the :method:`~shiny.ui.Chat.ui`
    method instead.

    Parameters
    ----------
    id
        A unique identifier for the chat session.
    placeholder
        The placeholder text to display in the chat input.
    width
        The width of the chat container.
    fill
        Whether the chat should fill the available width.
    """

    id = resolve_id(id)

    res = Tag(
        "shiny-chat-container",
        chat_deps(),
        {"style": f"width: {width}"},
        id=id,
        placeholder=placeholder,
        fill=fill,
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
