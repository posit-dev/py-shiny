import inspect
from types import NoneType
from typing import (
    Annotated,
    Any,
    Callable,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)

from typing_extensions import Literal, Required, TypedDict

__all__ = ("ToolFunction", "ToolSchema", "ToolSchemaFunction", "func_to_schema")

ToolFunction = Callable[..., Any]


class ToolSchemaProperty(TypedDict, total=False):
    type: Required[str]
    description: Required[str]


class ToolSchemaParams(TypedDict):
    type: Literal["object"]
    properties: dict[str, ToolSchemaProperty]
    required: list[str]


class ToolSchemaFunction(TypedDict):
    name: str
    description: str
    parameters: ToolSchemaParams


class ToolSchema(TypedDict):
    type: Literal["function"]
    function: ToolSchemaFunction


def func_to_schema(
    func: ToolFunction,
    name: str | None = None,
    description: str | None = None,
    parameter_descriptions: dict[str, str] | None = None,
) -> ToolSchema:
    signature = inspect.signature(func)
    required: list[str] = []

    for nm, param in signature.parameters.items():
        if param.default is param.empty and param.kind not in [
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ]:
            required.append(nm)

    annotations = get_type_hints(func, include_extras=True)

    param_desc = parameter_descriptions or {}

    params: ToolSchemaParams = {
        "type": "object",
        "properties": {
            k: type_to_json_schema(v, param_desc.get(k, None))
            for k, v in annotations.items()
            if k != "return"
        },
        "required": required,
    }

    desc = description or func.__doc__

    res: ToolSchema = {
        "type": "function",
        "function": {
            "name": name or func.__name__,
            "description": desc or "",
            "parameters": params,
        },
    }

    return res


def type_to_json_schema(
    t: type,
    desc: str | None = None,
) -> ToolSchemaProperty:
    origin = get_origin(t)
    args = get_args(t)
    if origin is Annotated:
        assert len(args) == 2
        assert desc is None or desc == ""
        assert isinstance(args[1], str)
        return type_to_json_schema(args[0], args[1])

    if origin is list:
        assert len(args) == 1
        return type_dict("array", desc, items=type_to_json_schema(args[0]))

    if origin is dict:
        assert len(args) == 2
        assert args[0] is str
        return type_dict(
            "object", desc, additionalProperties=type_to_json_schema(args[1])
        )

    if is_typeddict(t):
        annotations = get_type_hints(t, include_extras=True)
        return type_dict(
            "object",
            desc,
            properties={k: type_to_json_schema(v) for k, v in annotations.items()},
        )

    if t is dict:
        return type_dict("object", desc)
    if t is list:
        return type_dict("array", desc)
    if t is str:
        return type_dict("string", desc)
    if t is int:
        return type_dict("integer", desc)
    if t is float:
        return type_dict("number", desc)
    if t is bool:
        return type_dict("boolean", desc)
    if t is NoneType:
        return type_dict("null", desc)
    raise ValueError(f"Unsupported type: {t}")


def type_dict(
    type: str,
    description: str | None,
    **kwargs: Any,
) -> ToolSchemaProperty:
    res: ToolSchemaProperty = {
        "type": type,
        "description": description or "",
        **kwargs,  # type: ignore
    }
    return res
