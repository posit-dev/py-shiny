from __future__ import annotations

from typing import Literal, TypedDict

Role = Literal["assistant", "user", "system"]


# TODO: content should probably be [{"type": "text", "content": "..."}, {"type": "image", ...}]
# in order to support multiple content types...
class ChatMessage(TypedDict):
    content: str
    role: Role


# A message once transformed have been applied
class TransformedMessage(TypedDict):
    content_client: str
    content_server: str
    role: Role
    transform_key: Literal["content_client", "content_server"]
    pre_transform_key: Literal["content_client", "content_server"]


# A message that has been stored in the server-side chat history
class StoredMessage(TransformedMessage):
    # Number of tokens in the content
    token_count: int | None


# A message that can be sent to the client
class ClientMessage(ChatMessage):
    content_type: Literal["markdown", "html"]
    chunk_type: Literal["message_start", "message_end"] | None
