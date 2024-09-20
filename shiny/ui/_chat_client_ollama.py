import json
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Iterable,
    Optional,
    Sequence,
    cast,
)

from ._chat_client import LLMClientWithTools
from ._chat_client_utils import ToolFunction, ToolSchema, func_to_schema
from ._chat_merge import merge_dicts

if TYPE_CHECKING:
    from ollama import AsyncClient, Message
    from ollama._types import ChatResponse, Tool, ToolCall


class OllamaClient(LLMClientWithTools["Message"]):
    _messages: list["Message"] = []
    _tool_schemas: list["Tool"] = []
    _tool_functions: dict[str, ToolFunction] = {}

    def __init__(
        self,
        client: "AsyncClient | None" = None,
        model: Optional[str] = None,
        tools: Iterable[ToolFunction] = (),
    ) -> None:
        if client is None:
            client = self._get_client()
        self.client = client
        self._model = model
        for tool in tools:
            self.register_tool(tool)

    def _get_client(self) -> "AsyncClient":
        try:
            from ollama import AsyncClient

            return AsyncClient()
        except ImportError:
            raise ImportError(
                f"The {self.__class__.__name__} class requires the `ollama` package. "
                "Install it with `pip install ollama`."
            )

    async def generate_response(
        self,
        input: str,
        *,
        stream: bool = True,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        self._add_message({"role": "user", "content": input})
        while True:
            async for chunk in self._submit_messages(stream, **kwargs):
                yield chunk
            if not self._invoke_tools():
                break

    async def _submit_messages(
        self,
        stream: bool,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:

        model = kwargs.pop("model", self._model)
        tools: list["Tool"] = kwargs.pop("tools", [])
        tools.extend(self._tool_schemas)

        if stream:

            # https://github.com/ollama/ollama-python/issues/279
            if len(tools) > 0:
                raise ValueError(
                    "Ollama currently doesn't work correctly with tools in streaming mode."
                )

            response = await self.client.chat(
                model=model,
                messages=self.messages(),
                tools=tools,
                stream=True,
            )

            result: "Message | None" = None
            async for chunk in response:
                # .chat() returns a generator of generic dicts, but it seems safe to assume it's a ChatResponse
                # https://github.com/ollama/ollama-python/blob/ebe332b2/ollama/_client.py#L157
                chunk = cast("ChatResponse", chunk)
                if "message" not in chunk:
                    raise Exception(f"Unknown ollama response chunk: {chunk}")
                message = chunk["message"]
                if "content" in message:
                    yield message["content"]
                if result is None:
                    result = message
                else:
                    result = merge_dicts(result, message)  # type: ignore

            if result is not None:
                self._add_message(result)

        else:

            response = await self.client.chat(
                model=model,
                messages=self.messages(),
                tools=tools,
                stream=False,
            )

            # .chat() returns a generic dict, but it seems safe to assume it's a ChatResponse
            # https://github.com/ollama/ollama-python/blob/ebe332b2/ollama/_client.py#L157
            response = cast("ChatResponse", response)

            if "message" not in response:
                raise Exception(f"Unknown ollama response object: {response}")
            else:
                message = response["message"]
                if "content" in message:
                    yield message["content"]
                self._add_message(message)

    def messages(self) -> list["Message"]:
        return self._messages

    def _add_message(self, message: "Message") -> None:
        self._messages.append(message)

    def _add_messages(self, messages: Sequence["Message"]) -> None:
        self._messages.extend(messages)

    def register_tool(
        self,
        func: ToolFunction,
        *,
        schema: Optional["Tool"] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameter_descriptions: Optional[dict[str, str]] = None,
    ):
        if schema is None:
            final_schema = self._transform_tool_schema(
                func_to_schema(func, name, description, parameter_descriptions)
            )
        else:
            final_schema = schema

        name = final_schema["function"]["name"]

        self._tool_schemas = [
            x for x in self._tool_schemas if x["function"]["name"] != name
        ]
        self._tool_schemas.append(final_schema)
        self._tool_functions[name] = func

    @staticmethod
    def _transform_tool_schema(
        schema: ToolSchema,
    ) -> "Tool":
        fn = schema["function"]
        name = fn["name"]
        params = fn["parameters"]
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": fn["description"] or "",
                "parameters": {
                    "type": "object",
                    "properties": params["properties"],  # type: ignore
                    "required": params["required"],
                },
            },
        }

    def _invoke_tools(self) -> bool:
        if self._tool_functions:
            last = self.messages()[-1]
            assert last["role"] == "assistant"
            tool_messages = self._call_tools(last)
            if len(tool_messages) > 0:
                self._add_messages(tool_messages)
                return True
        return False

    def _call_tools(self, last_message: "Message") -> Sequence["Message"]:
        tool_calls = last_message.get("tool_calls", None)
        if tool_calls is None:
            return []
        res: list["Message"] = []
        for x in tool_calls:
            msg = self._call_tool(x)
            res.append(msg)
        return res

    def _call_tool(
        self,
        tool_call: "ToolCall",
    ) -> "Message":
        name = tool_call["function"]["name"]
        tool_fun = self._tool_functions.get(name, None)
        if tool_fun is None:
            raise ValueError(f"Tool {name} not found.")

        args = tool_call["function"].get("arguments", {})

        try:
            result = tool_fun(**args)
        except Exception as e:
            raise ValueError(f"Error calling tool {name}: {e}")

        return {
            "role": "tool",
            "content": json.dumps({name: result, **args}),
        }

    def get_response_content(self, message: Any) -> str:
        if "message" not in message:
            raise ValueError(f"Expected 'message' key in response: {message}")

        msg = cast("ChatResponse", message)

        return msg.get("content", "")

    def get_streaming_response_content(self, delta: Any) -> str:
        if "message" not in delta:
            raise ValueError(f"Expected 'message' key in response: {delta}")

        msg = cast("ChatResponse", delta)
        return msg.get("content", "")
