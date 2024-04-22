from typing import TYPE_CHECKING, Literal

from htmltools import HTMLDependency, Tag, TagAttrs, TagAttrValue, TagChild

from . import ui
from ._namespaces import resolve_id
from .session import require_active_session
from .ui._utils import _session_on_flush_send_msg

if TYPE_CHECKING:
    from . import Session

__all__ = (
    "box",
    "message",
    "insert_message",
    "insert_streaming_message",
)

Roles = Literal["user", "assistant", "system"]


# TODO:
# * Investigate langchain callbacks
# * Can we support streaming?
# * Add history() component.
# * Add box(suggestions)
def box(
    id: str,
    *,
    placeholder: str = "Your message",
    messages: ui.TagChild = None,
    width: str = "min(680px, 100%)",
    fill: bool = True,
) -> ui.Tag:
    """
    Create a chat box component.
    """

    id = resolve_id(id)

    chat_input = ui.div(
        {"class": "input-group"},
        ui.tags.textarea(
            {"class": "form-control", "style": "resize:none;"},
            id=id + "_input",
            placeholder=placeholder,
        ),
        ui.tags.button(
            # TODO: Icon customisation
            ui.HTML(
                '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-send" viewBox="0 0 16 16"><path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"/></svg>'
            ),
            {"class": "btn btn-primary"},
            id=id,
            type="button",
        ),
    )

    res = ui.div(
        {"class": "shiny-chat-box", "style": f"width: {width};"},
        messages,
        ui.div({"class": "shiny-chat-input"}, chat_input),
        id=resolve_id(id),
        placeholder=placeholder,
        width=width,
        fill=fill,
    )

    if fill:
        res = ui.fill.as_fill_item(res)

    return res


def message(content: str, *, role: Roles = "assistant") -> ui.Tag:
    """
    Create a chat message component.

    Parameters
    ----------
    content
        The content of the message (a markdown string).
    role
        The role of the message.
    """

    return chat_component("shiny-chat-message", role=role, content=content)


def insert_message(
    id: str,
    content: str,
    *,
    role: Roles = "assistant",
    session: "Session | None" = None,
):
    """
    Insert a message into the chat box.
    """

    msg = {"type": "insert_message", "message": {"content": content, "role": role}}

    _session_on_flush_send_msg(id, session, msg)  # type: ignore


async def insert_streaming_message(
    id: str,
    content: str,
    *,
    role: Roles = "assistant",
    session: "Session | None" = None,
):
    """
    Insert a message into the chat box.
    """

    msg = {
        "id": resolve_id(id),
        "content": content,
        "role": role,
    }

    session = require_active_session(session)
    await session.send_custom_message("shiny.insertStreamingMessage", msg)  # type: ignore


# ----------------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------------


def chat_component(
    tag_name: str,
    *args: TagChild | TagAttrs,
    **kwargs: TagAttrValue,
) -> Tag:
    return Tag(
        tag_name,
        chat_dep(),
        *args,
        _add_ws=False,
        **kwargs,
    )


def chat_dep():
    return HTMLDependency(
        "shiny-chat",
        "0.0.1",
        source={"package": "shiny", "subdir": "www/shared/py-shiny/chat"},
        script={"src": "chat.js"},
        stylesheet={"href": "chat.css"},
    )
