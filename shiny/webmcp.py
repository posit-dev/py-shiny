"""Experimental browser-agent tools for Shiny's live sessions."""

from __future__ import annotations

import inspect
import json
import re
from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast

from htmltools import HTMLDependency
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from ._docstring import no_example
from ._version import __version__
from .reactive import flush, isolate
from .session._utils import require_active_session, session_context
from .types import Jsonifiable, SafeException

if TYPE_CHECKING:
    from .session import Session

__all__ = ("tool",)
F = TypeVar("F", bound=Callable[..., Any])


@no_example()
def tool(
    *,
    input_schema: dict[str, Any],
    description: str,
    name: str | None = None,
    read_only: bool = False,
    consequential: bool = False,
    session: Session | None = None,
) -> Callable[[F], F]:
    """Expose a Python function to browser agents in the current session.

    Define tools inside a server function (including an Express or module server).
    Enable exposure with ``App(..., webmcp=True)`` or ``SHINY_WEBMCP=1``. When
    disabled, the decorated function remains callable but is not exposed.

    Parameters
    ----------
    input_schema
        A JSON Schema 2020-12 object schema. Arguments are validated on the server
        and passed as keyword arguments. Defaults in a schema are descriptive;
        use Python defaults for optional arguments. External references are not
        supported; keep schemas self-contained.
    description
        Describe the action, its effects, and its returned result for an agent.
    name
        Tool name, defaulting to the function name. Names are module-namespaced.
        The ``shiny_`` prefix is reserved for automatic tools.
    read_only
        Whether the function only reads application state. This is an agent hint,
        not an enforcement mechanism.
    consequential
        Whether the action has significant or irreversible effects.
    session
        Session to register with. Defaults to the current session.

    Returns
    -------
    :
        A decorator that returns the original function. Both synchronous and
        asynchronous functions are supported and must return JSON-serializable
        data. Calls execute in an isolated reactive context in their own session.

    Notes
    -----
    Tools are removed when their session or module is destroyed. They use the
    existing authenticated WebSocket and the app's error-sanitization settings.
    Browser cancellation stops waiting; it does not undo or interrupt Python
    work already dispatched. Long-running work should use an extended task.
    """
    schema = deepcopy(input_schema)
    Draft202012Validator.check_schema(schema)
    if schema.get("type") != "object":
        raise ValueError("A tool's input_schema must have type 'object'.")

    # Do not let schema validation fetch remote documents during a tool call.
    def check_refs(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in cast(dict[str, Any], value).items():
                if key in ("$ref", "$dynamicRef") and not str(item).startswith("#"):
                    raise ValueError("WebMCP schemas must use local references.")
                check_refs(item)
        elif isinstance(value, list):
            for item in cast(list[Any], value):
                check_refs(item)

    check_refs(schema)
    if not description.strip():
        raise ValueError("A tool description must not be empty.")

    def decorate(fn: F) -> F:
        current = require_active_session(session)
        local_name = name or fn.__name__
        if not re.fullmatch(r"[A-Za-z0-9_-]+", local_name) or local_name.startswith(
            "shiny_"
        ):
            raise ValueError(
                "Tool names must use letters, digits, '_' or '-', without the reserved 'shiny_' prefix."
            )
        registry: _SessionTools | None = getattr(
            current.root_scope(), "_webmcp_tools", None
        )
        if registry is not None:
            registry.add(
                _Tool(
                    name=str(current.ns(local_name)),
                    description=description,
                    schema=schema,
                    fn=fn,
                    session=current,
                    read_only=read_only,
                    consequential=consequential,
                )
            )
        return fn

    return decorate


@dataclass
class _Tool:
    name: str
    description: str
    schema: dict[str, Any]
    fn: Callable[..., Any]
    session: Session
    read_only: bool
    consequential: bool

    def manifest(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.schema,
            "annotations": {
                "readOnlyHint": self.read_only,
                "consequentialHint": self.consequential,
            },
        }


class _SessionTools:
    def __init__(self, session: Session):
        self.session = session
        self.tools: dict[str, _Tool] = {}
        self.dirty = False
        session.set_message_handler("shiny_webmcp_describe", self.describe)
        session.set_message_handler("shiny_webmcp_invoke", self.invoke)
        session.set_message_handler("shiny_webmcp_flush", self.barrier)
        session.on_flushed(self.publish, once=False)

    def add(self, tool: _Tool) -> None:
        if tool.name in self.tools:
            raise ValueError(f"WebMCP tool already registered: {tool.name}")
        self.tools[tool.name] = tool
        self.dirty = True

        def remove() -> None:
            self.tools.pop(tool.name, None)
            self.dirty = True

        tool.session.on_destroy(remove)

    def describe(self) -> list[Jsonifiable]:
        return [tool.manifest() for tool in self.tools.values()]

    async def publish(self) -> None:
        if self.dirty:
            self.dirty = False
            await self.session.send_custom_message(
                "shiny-webmcp-tools", {"tools": self.describe()}
            )

    async def barrier(self) -> None:
        # The update preceding this request has already been processed. Flushing
        # here also sends any output/input messages queued by a custom tool before
        # the RPC response, preserving browser message-queue ordering.
        await flush()

    async def invoke(self, name: str, arguments: dict[str, Any]) -> Jsonifiable:
        registered = self.tools.get(name)
        if registered is None:
            raise SafeException(f"Unknown WebMCP tool: {name}")
        # Shiny's input decoder freezes JSON arrays as tuples. Tool arguments
        # retain JSON semantics for schema validation and the Python callable.
        arguments = json.loads(json.dumps(arguments))
        try:
            validator = Draft202012Validator(registered.schema)
            validator.validate(arguments)  # pyright: ignore[reportUnknownMemberType]
        except ValidationError as error:
            raise SafeException(f"Invalid tool arguments: {error.message}") from error
        with session_context(registered.session), isolate():
            result = registered.fn(**arguments)
            if inspect.isawaitable(result):
                result = await result
        # Check the result before the WebSocket serializer, including NaN/Infinity.
        result = json.loads(json.dumps(result, allow_nan=False))
        await self.barrier()
        return result


def _dependency() -> HTMLDependency:
    return HTMLDependency(
        name="shiny-webmcp",
        version=__version__,
        source={"package": "shiny", "subdir": "www/py-shiny/webmcp"},
        script={"src": "webmcp.js"},
    )
