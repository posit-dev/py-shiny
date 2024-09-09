from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Literal, Optional

from . import _chat_typed_dicts as ctd


# TODO: content should probably be [{"type": "text", "content": "..."}, {"type": "image", ...}]
# in order to support multiple content types...
@dataclass
class UserMessage:
    content: str
    role: Literal["user"] = "user"

    def to_dict(self) -> ctd.UserMessage:
        return {"content": self.content, "role": self.role}


@dataclass
class AssistantMessage:
    content: str
    role: Literal["assistant"] = "assistant"
    tool_calls: Optional[list[ctd.ToolFunctionCall]] = None

    def to_dict(self) -> ctd.AssistantMessage:
        res: ctd.AssistantMessage = {"content": self.content, "role": self.role}
        if self.tool_calls is None:
            return res
        else:
            return {**res, "tool_calls": self.tool_calls}


@dataclass
class SystemMessage:
    content: str
    role: Literal["system"] = "system"

    def to_dict(self) -> ctd.SystemMessage:
        return {"content": self.content, "role": self.role}


# Inspired by LiteLLM's tool message format
@dataclass
class ToolMessage:
    content: str  # The result of the tool (function) call
    name: str  # The name of the tool (function) called
    tool_call_id: str
    role: Literal["tool"] = "tool"

    def to_dict(self) -> ctd.ToolMessage:
        return {
            "content": self.content,
            "name": self.name,
            "tool_call_id": self.tool_call_id,
            "role": self.role,
        }


ChatMessage = UserMessage | AssistantMessage | SystemMessage | ToolMessage


# A message once transformed have been applied
class TransformedMessage:
    def __init__(
        self,
        message: ChatMessage,
        transformed_content: str | None = None,
    ):
        self.message = message
        if transformed_content is None:
            transformed_content = message.content
        self.transformed_content = transformed_content

    @property
    def role(self) -> Literal["user", "assistant", "system", "tool"]:
        return self.message.role

    @property
    def content_client(self) -> str:
        if self.role == "user":
            return self.message.content
        else:
            return self.transformed_content

    @property
    def content_server(self) -> str:
        if self.role == "user":
            return self.transformed_content
        else:
            return self.message.content

    def get_message(self, transformed: bool = True) -> ChatMessage:
        res = copy.copy(self.message)
        if transformed:
            res.content = self.transformed_content
        return res


# A message that can be sent to the client
@dataclass
class ClientMessage:
    role: Literal["user", "assistant"]
    content: str
    content_type: Literal["markdown", "html"] = "markdown"
    chunk_type: Literal["message_start", "message_end"] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "content_type": self.content_type,
            "chunk_type": self.chunk_type,
        }


# The continuation of a (streaming) function call
class ToolFunctionCallDelta:
    def __init__(self, arguments: str, finished: bool = False):
        self.arguments = arguments
        self.finished = finished


# The start of a (streaming) function call
class ToolFunctionCall:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.arguments = ""
        self.finished = False

    def __add__(self, other: ToolFunctionCallDelta):
        self.arguments += other.arguments
        self.finished = other.finished

    def to_dict(self) -> ctd.ToolFunctionCall:
        return {
            "id": self.id,
            "function": {"name": self.name, "arguments": self.arguments},
            "type": "function",
        }
