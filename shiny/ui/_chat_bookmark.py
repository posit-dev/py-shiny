import importlib.util
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Protocol,
    cast,
    runtime_checkable,
)

from htmltools import TagChild

from .._utils import CancelCallback
from ..types import Jsonifiable

if TYPE_CHECKING:

    import chatlas

else:
    chatlas = object


chatlas_is_installed = importlib.util.find_spec("chatlas") is not None


def is_chatlas_chat_client(client: Any) -> bool:
    if not chatlas_is_installed:
        return False
    import chatlas

    return isinstance(client, chatlas.Chat)


@runtime_checkable
class ClientWithState(Protocol):
    async def get_state(self) -> Jsonifiable: ...

    """
    Retrieve JSON-like representation of chat client state.

    This method is used to retrieve the state of the client object when saving a bookmark.

    Returns
    -------
    :
        A JSON-like representation of the current state of the client. It is not required to be a JSON string but something that can be serialized to JSON without further conversion.
    """

    async def set_state(self, state: Jsonifiable): ...

    """
    Method to set the chat client state.

    This method is used to restore the state of the client when the app is restored from
    a bookmark.

    Parameters
    ----------
    state
        The value to infer the state from. This value will be the JSON capable value
        returned by the `get_state()` method (after a round trip through JSON
        serialization and unserialization).
    """


class BookmarkCancelCallback:
    def __init__(self, cancel: CancelCallback):
        self.cancel = cancel

    def __call__(self):
        self.cancel()

    def tagify(self) -> TagChild:
        return ""


# Chatlas specific implementation
def get_chatlas_state(
    client: chatlas.Chat[Any, Any],
) -> Callable[[], Awaitable[Jsonifiable]]:

    from chatlas import Turn as ChatlasTurn

    async def get_state() -> Jsonifiable:

        turns: list[ChatlasTurn[Any]] = client.get_turns()
        turns_json_str: list[str] = [turn.model_dump_json() for turn in turns]
        return cast(Jsonifiable, turns_json_str)

    return get_state


def set_chatlas_state(
    client: chatlas.Chat[Any, Any],
) -> Callable[[Jsonifiable], Awaitable[None]]:
    from chatlas import Turn as ChatlasTurn

    async def set_state(value: Jsonifiable) -> None:

        if not isinstance(value, list):
            raise ValueError("Chatlas bookmark value must be a list of JSON strings")
        for v in value:
            if not isinstance(v, str):
                raise ValueError("Chat bookmark value must be a list of strings")

        turns_json_str = cast(list[str], value)

        turns: list[ChatlasTurn[Any]] = [
            ChatlasTurn.model_validate_json(turn_json_str)
            for turn_json_str in turns_json_str
        ]
        client.set_turns(turns)  # pyright: ignore[reportUnknownMemberType]

    return set_state
