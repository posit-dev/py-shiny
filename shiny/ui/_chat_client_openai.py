import json
from typing import TYPE_CHECKING, Any, AsyncGenerator, Iterable, Optional, Sequence

from ._chat_client import LLMClientWithTools
from ._chat_client_utils import ToolFunction, ToolSchema, func_to_schema
from ._chat_merge import merge_dicts

if TYPE_CHECKING:
    from openai import AsyncOpenAI
    from openai.types.chat import (
        ChatCompletionAssistantMessageParam,
        ChatCompletionMessageParam,
        ChatCompletionMessageToolCallParam,
        ChatCompletionToolMessageParam,
        ChatCompletionToolParam,
    )
    from openai.types.chat_model import ChatModel


class OpenAIClient(LLMClientWithTools["ChatCompletionMessageParam"]):
    _messages: list["ChatCompletionMessageParam"] = []
    _tool_schemas: list["ChatCompletionToolParam"] = []
    _tool_functions: dict[str, ToolFunction] = {}

    def __init__(
        self,
        client: "AsyncOpenAI | None" = None,
        api_key: Optional[str] = None,
        model: "ChatModel" = "gpt-4o",
        tools: Iterable[ToolFunction] = (),
    ):
        if client is None:
            self.client = self._get_client(api_key)
        self._model = model
        for tool in tools:
            self.register_tool(tool)

    def _get_client(self, api_key: Optional[str]) -> "AsyncOpenAI":
        try:
            from openai import AsyncOpenAI

            return AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                f"The {self.__class__.__name__} class requires the `openai` package. "
                "Install it with `pip install openai`."
            )

    # TODO: make this an overloads (based on stream) and
    # suitable TypeDicts on kwargs
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
        from openai.types.chat import ChatCompletionAssistantMessageParam

        model = kwargs.pop("model", self._model)
        tools: list["ChatCompletionToolParam"] = kwargs.pop("tools", [])
        tools.extend(self._tool_schemas)

        if stream:
            response = await self.client.chat.completions.create(
                messages=self.messages(),
                model=model,
                stream=True,
                tools=self._tool_schemas,
                **kwargs,
            )
            # TODO: handle refusal?
            result = None
            async for chunk in response:
                d = chunk.choices[0].delta
                if result is None:
                    result = d.model_dump()
                else:
                    result = merge_dicts(result, d.model_dump())
                if d.content:
                    yield d.content

            if result is not None:
                self._add_message(ChatCompletionAssistantMessageParam(**result))
        else:
            response = await self.client.chat.completions.create(
                messages=self.messages(),
                model=model,
                stream=False,
                **kwargs,
            )
            # TODO: handle refusal?
            message = response.choices[0].message
            msg = ChatCompletionAssistantMessageParam(**message.model_dump())
            self._add_message(msg)

            if message.content:
                yield message.content

    def messages(self) -> list["ChatCompletionMessageParam"]:
        return self._messages

    def _add_messages(self, messages: Sequence["ChatCompletionMessageParam"]):
        self._messages.extend(messages)

    def _add_message(self, message: "ChatCompletionMessageParam"):
        self._messages.append(message)

    def register_tool(
        self,
        func: ToolFunction,
        *,
        schema: Optional["ChatCompletionToolParam"] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameter_descriptions: Optional[dict[str, str]] = None,
        strict: bool = False,
    ):

        if schema is None:
            final_schema = self._transform_tool_schema(
                func_to_schema(func, name, description, parameter_descriptions),
                strict=strict,
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
        tool: "ToolSchema", strict: bool = False
    ) -> "ChatCompletionToolParam":
        fn = tool["function"]
        name = fn["name"]
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": fn["description"],
                "parameters": {
                    "type": "object",
                    "properties": fn["parameters"]["properties"],
                    "required": fn["parameters"]["required"],
                },
                "strict": strict,
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

    def _call_tools(
        self, last_message: "ChatCompletionAssistantMessageParam"
    ) -> Sequence["ChatCompletionToolMessageParam"]:
        tool_calls = last_message.get("tool_calls", None)
        if tool_calls is None:
            return []
        res: list["ChatCompletionToolMessageParam"] = []
        for x in tool_calls:
            msg = self._call_tool(x)
            res.append(msg)
        return res

    def _call_tool(
        self,
        tool_call: "ChatCompletionMessageToolCallParam",
    ) -> "ChatCompletionToolMessageParam":
        name = tool_call["function"]["name"]
        tool_fun = self._tool_functions.get(name, None)
        if tool_fun is None:
            raise ValueError(f"Tool {name} not found.")

        args_str = tool_call["function"]["arguments"]
        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON arguments for tool {name}")

        try:
            result = tool_fun(**args)
        except Exception as e:
            raise ValueError(f"Error calling tool {name}: {e}")

        return {
            "role": "tool",
            "content": json.dumps({name: result, **args}),
            "tool_call_id": tool_call["id"],
        }
