from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from htmltools import HTML, TagChild

from .._typing_extensions import NotRequired
from ..session import require_active_session

Role = Literal["assistant", "user", "system"]


# TODO: content should probably be [{"type": "text", "content": "..."}, {"type": "image", ...}]
# in order to support multiple content types...
class ChatMessageDict(TypedDict):
    content: str
    role: Role


class ChatMessage:
    def __init__(
        self,
        content: TagChild,
        role: Role,
    ):
        self.role: Role = role

        # content _can_ be a TagChild, but it's most likely just a string (of
        # markdown), so only process it if it's not a string.
        deps = []
        if not isinstance(content, str):
            session = require_active_session(None)
            res = session._process_ui(content)
            content = res["html"]
            deps = res["deps"]

        self.content = content
        self.html_deps = deps


# A message once transformed have been applied
@dataclass
class TransformedMessage:
    content_client: str | HTML
    content_server: str
    role: Role
    transform_key: Literal["content_client", "content_server"]
    pre_transform_key: Literal["content_client", "content_server"]
    html_deps: list[dict[str, str]] | None = None

    @classmethod
    def from_chat_message(cls, message: ChatMessage) -> "TransformedMessage":
        if message.role == "user":
            transform_key = "content_server"
            pre_transform_key = "content_client"
        else:
            transform_key = "content_client"
            pre_transform_key = "content_server"

        return TransformedMessage(
            content_client=message.content,
            content_server=message.content,
            role=message.role,
            transform_key=transform_key,
            pre_transform_key=pre_transform_key,
            html_deps=message.html_deps,
        )


# A message that can be sent to the client
class ClientMessage(TypedDict):
    content: str
    role: Literal["assistant", "user"]
    content_type: Literal["markdown", "html"]
    chunk_type: Literal["message_start", "message_end"] | None
    operation: Literal["append", "replace"]
    icon: NotRequired[str]
    html_deps: NotRequired[list[dict[str, str]]]
