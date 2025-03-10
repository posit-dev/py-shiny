from __future__ import annotations

from typing import Literal, TypedDict

from htmltools import HTML

from .._typing_extensions import NotRequired

Role = Literal["assistant", "user", "system"]


# TODO: content should probably be [{"type": "text", "content": "..."}, {"type": "image", ...}]
# in order to support multiple content types...
class ChatMessage(TypedDict):
    content: str
    role: Role
    html_deps: NotRequired[list[dict[str, str]]]


# A message once transformed have been applied
class TransformedMessage(TypedDict):
    content_client: str | HTML
    content_server: str
    role: Role
    transform_key: Literal["content_client", "content_server"]
    pre_transform_key: Literal["content_client", "content_server"]
    html_deps: NotRequired[list[dict[str, str]]]


# A message that can be sent to the client
class ClientMessage(TypedDict):
    content: str
    role: Literal["assistant", "user"]
    content_type: Literal["markdown", "html"]
    chunk_type: Literal["message_start", "message_end"] | None
    icon: NotRequired[str]
    html_deps: NotRequired[list[dict[str, str]]]
