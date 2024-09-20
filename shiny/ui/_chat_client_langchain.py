from typing import TYPE_CHECKING, Union

from ._chat_client import LLMClient

if TYPE_CHECKING:
    from langchain_core.messages import (
        AIMessage,
        HumanMessage,
        SystemMessage,
        ToolMessage,
    )

    LangChainMessage = Union[AIMessage, HumanMessage, SystemMessage, ToolMessage]


class LangChainClient(LLMClient["LangChainMessage"]):
    pass
