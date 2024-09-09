from ..types import Literal, NotRequired, TypedDict


# TypedDicts are generally used for a user-facing types, since they are generally
# more friendly as input to (3rd-party) response generation.
# Note also, that we generally follow OpenAI/LiteLLM's conventions since they are
# are more widely supported (at least at the time of writing).
class UserMessage(TypedDict):
    content: str
    role: Literal["user"]


class AssistantMessage(TypedDict):
    content: str
    role: Literal["assistant"]
    tool_calls: NotRequired[list["ToolFunctionCall"]]


class SystemMessage(TypedDict):
    content: str
    role: Literal["system"]


class ToolMessage(TypedDict):
    content: str
    name: str
    tool_call_id: str
    role: Literal["tool"]


ChatMessage = UserMessage | AssistantMessage | SystemMessage | ToolMessage


class ToolFunction(TypedDict):
    name: str
    arguments: str


class ToolFunctionCall(TypedDict):
    id: str
    function: ToolFunction
    type: Literal["function"]
