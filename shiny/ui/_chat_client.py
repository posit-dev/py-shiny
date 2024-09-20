from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Generic, Optional, TypeVar

from ._chat_client_utils import ToolFunction

MessageType = TypeVar("MessageType")


class LLMClient(ABC, Generic[MessageType]):
    @abstractmethod
    async def generate_response(
        self,
        input: str,
        *,
        stream: bool = True,
    ) -> AsyncGenerator[str, None]: ...

    @abstractmethod
    def messages(self) -> list[MessageType]: ...


class LLMClientWithTools(LLMClient[MessageType]):
    @abstractmethod
    def register_tool(
        self,
        func: ToolFunction,
        *,
        schema: Optional[Any] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameter_descriptions: Optional[dict[str, str]] = None,
    ) -> None: ...
