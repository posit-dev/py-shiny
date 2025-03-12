from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from htmltools import HTML

from .._typing_extensions import NotRequired

Role = Literal["assistant", "user", "system"]


# TODO: content should probably be [{"type": "text", "content": "..."}, {"type": "image", ...}]
# in order to support multiple content types...
class ChatMessage(TypedDict):
    content: str
    role: Role


# A message once transformed have been applied
@dataclass
class TransformedMessage:
    content_client: str | HTML
    content_server: str
    role: Role
    transform_key: Literal["content_client", "content_server"]
    pre_transform_key: Literal["content_client", "content_server"]

    @classmethod
    def from_message(cls, message: ChatMessage) -> TransformedMessage:
        if message["role"] == "user":
            transform_key = "content_server"
            pre_transform_key = "content_client"
        else:
            transform_key = "content_client"
            pre_transform_key = "content_server"

        return cls(
            content_client=message["content"],
            content_server=message["content"],
            role=message["role"],
            transform_key=transform_key,
            pre_transform_key=pre_transform_key,
        )


# A message that can be sent to the client
class ClientMessage(ChatMessage):
    content_type: Literal["markdown", "html"]
    chunk_type: Literal["message_start", "message_end"] | None
    operation: Literal["append", "replace"]
    icon: NotRequired[str]
