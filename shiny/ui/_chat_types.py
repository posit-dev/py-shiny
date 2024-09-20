from __future__ import annotations

import copy
from typing import Literal, TypedDict


class ChatMessage(TypedDict):
    content: str
    role: str


# A message once transformed have been applied
class TransformedMessage:
    def __init__(
        self,
        message: ChatMessage,
        transformed_content: str | None = None,
    ):
        self.message = message
        if transformed_content is None:
            transformed_content = message["content"]
        self.transformed_content = transformed_content

    @property
    def role(self) -> str:
        return self.message["role"]

    @property
    def content_client(self) -> str:
        if self.role == "user":
            return self.message["content"]
        else:
            return self.transformed_content

    @property
    def content_server(self) -> str:
        if self.role == "user":
            return self.transformed_content
        else:
            return self.message["content"]

    def get_message(self, transformed: bool = True) -> ChatMessage:
        res = copy.copy(self.message)
        if transformed:
            res["content"] = self.transformed_content
        return res


# A message that can be sent to the client
class ClientMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str
    content_type: Literal["markdown", "html"]
    chunk_type: Literal["message_start", "message_end", None]
