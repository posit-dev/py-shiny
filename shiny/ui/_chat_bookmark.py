import importlib.util
from typing import Any, Awaitable, Callable, Protocol, runtime_checkable

from htmltools import TagChild

from .._utils import CancelCallback
from ..types import Jsonifiable

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
    client: Any,
) -> Callable[[], Awaitable[Jsonifiable]]:

    from chatlas import Chat, Turn

    assert isinstance(client, Chat)

    async def get_state() -> Jsonifiable:

        turns: list[Turn[Any]] = client.get_turns()
        return {
            "version": 1,
            "turns": [turn.model_dump(mode="json") for turn in turns],
        }

    return get_state


def set_chatlas_state(
    client: Any,
) -> Callable[[Jsonifiable], Awaitable[None]]:
    from chatlas import Chat, Turn

    assert isinstance(client, Chat)

    # TODO-future: Use pydantic model for validation
    # instead of manual validation
    async def set_state(value: Jsonifiable) -> None:

        if not isinstance(value, dict):
            raise ValueError("Chatlas bookmark value was not a dictionary")

        version = value.get("version")
        if version != 1:
            raise ValueError(f"Unsupported Chatlas bookmark version: {version}")
        turns_arr = value.get("turns")

        if not isinstance(turns_arr, list):
            raise ValueError(
                "Chatlas bookmark value was not a list of chat message information"
            )

        turns: list[Turn[Any]] = [
            Turn.model_validate(turn_obj) for turn_obj in turns_arr
        ]
        client.set_turns(turns)  # pyright: ignore[reportUnknownMemberType]

    return set_state
