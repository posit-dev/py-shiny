from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from htmltools import MetadataNode, Tag, TagList

from ..._typing_extensions import Self
from ..._utils import is_async_callable, wrap_async

# TODO-barret; POST-merge; shinywidgets should not call `resolve_value_fn`

# TODO-barret; Q: Should `Renderer.default_ui` be renamed? `ui()`? `express_ui()`?
# TODO-barret; Q: Should `Renderer.default_ui` accept args? ... Should `output_args()` be renamed to `ui_kwargs()`? (If anything rename to `ui_args()`)
# TODO-barret; Q: Should `Renderer.default_ui` accept kwargs? ... Should `output_kwargs()` be renamed to `ui_kwargs()`? (If anything rename to `ui_kwargs()`) Add `.ui_kwargs()` method?


# TODO-future: docs; missing first paragraph from some classes: Example: TransformerMetadata.
# No init method for TransformerParams. This is because the `DocClass` object does not
# display methods that start with `_`. THerefore no `__init__` or `__call__` methods are
# displayed. Even if they have docs.


if TYPE_CHECKING:
    from ...session import Session


__all__ = (
    "Renderer",
    "RendererBase",
    "Renderer",
    "ValueFn",
    "JSONifiable",
    "AsyncValueFn",
)

# Input type for the user-spplied function that is passed to a render.xx
IT = TypeVar("IT")


# https://github.com/python/cpython/blob/df1eec3dae3b1eddff819fd70f58b03b3fbd0eda/Lib/json/encoder.py#L77-L95
# +-------------------+---------------+
# | Python            | JSON          |
# +===================+===============+
# | dict              | object        |
# +-------------------+---------------+
# | list, tuple       | array         |
# +-------------------+---------------+
# | str               | string        |
# +-------------------+---------------+
# | int, float        | number        |
# +-------------------+---------------+
# | True              | true          |
# +-------------------+---------------+
# | False             | false         |
# +-------------------+---------------+
# | None              | null          |
# +-------------------+---------------+
JSONifiable = Union[
    str,
    int,
    float,
    bool,
    None,
    List["JSONifiable"],
    Tuple["JSONifiable"],
    Dict[str, "JSONifiable"],
]


DefaultUIFnResult = Union[TagList, Tag, MetadataNode, str]
DefaultUIFnResultOrNone = Union[DefaultUIFnResult, None]
DefaultUIFn = Callable[[str], DefaultUIFnResultOrNone]
DefaultUIFnImpl = Union[
    DefaultUIFn,
    Callable[[Dict[str, object], str], DefaultUIFnResultOrNone],
]

ValueFnSync = Callable[[], IT]
"""
App-supplied output value function which returns type `IT`. This function is
synchronous.
"""
ValueFnAsync = Callable[[], Awaitable[IT]]
"""
App-supplied output value function which returns type `IT`. This function is
asynchronous.
"""
ValueFnApp = Union[Callable[[], IT], Callable[[], Awaitable[IT]]]
"""
App-supplied output value function which returns type `IT`. This function can be
synchronous or asynchronous.
"""
ValueFn = Optional[ValueFnApp[Union[IT, None]]]


class RendererBase(ABC):
    __name__: str
    """Name of output function supplied. (The value will not contain any module prefix.)"""

    _auto_registered: bool = False

    # Meta
    session: Session
    """
    :class:`~shiny.Session` object
    """
    name: str
    """
    Output function name or ID (provided to `@output(id=)`). This value will contain any module prefix.
    """

    def default_ui(
        self,
        id: str,
        # *args: object,
        # **kwargs: object,
    ) -> DefaultUIFnResultOrNone:
        return None

    @abstractmethod
    async def render(self) -> JSONifiable:
        ...

    def __init__(self) -> None:
        super().__init__()

    # Q: Could we do this with typing without putting `P` in the Generic?
    # A: No. Even if we had a `P` in the Generic, the calling decorator would not have access to it.
    # Idea: Possibly use a chained method of `.ui_kwargs()`? https://github.com/posit-dev/py-shiny/issues/971
    _default_ui_kwargs: dict[str, Any] = dict()
    # _default_ui_args: tuple[Any, ...] = tuple()

    def _on_register(self) -> None:
        if self._auto_registered:
            # We're being explicitly registered now. Undo the auto-registration.
            # (w/ module support)
            ns_name = self.session.output._ns(self.__name__)
            self.session.output.remove(ns_name)
            self._auto_registered = False

    def _auto_register(self) -> None:
        # If in Express mode, register the output
        if not self._auto_registered:
            from ...session import get_current_session

            s = get_current_session()
            if s is not None:
                s.output(self)
                # We mark the fact that we're auto-registered so that, if an explicit
                # registration now occurs, we can undo this auto-registration.
                self._auto_registered = True

    def _repr_html_(self) -> str | None:
        rendered_ui = self._render_default_ui()
        if rendered_ui is None:
            return None
        return TagList(rendered_ui)._repr_html_()

    def tagify(self) -> DefaultUIFnResult:
        rendered_ui = self._render_default_ui()
        if rendered_ui is None:
            raise TypeError(
                "No default UI exists for this type of render function: ",
                self.__class__.__name__,
            )
        return rendered_ui

    def _render_default_ui(self) -> DefaultUIFnResultOrNone:
        return self.default_ui(
            self.__name__,
            # Pass the `@ui_kwargs(foo="bar")` kwargs through to the default_ui function.
            **self._default_ui_kwargs,
        )


# Not inheriting from `WrapAsync[[], IT]` as python 3.8 needs typing extensions that doesn't support `[]` for a ParamSpec definition. :-(
# Would be minimal/clean if we could do `class AsyncValueFn(WrapAsync[[], IT]):`
class AsyncValueFn(Generic[IT]):
    """
    App-supplied output value function which returns type `IT`.
    asynchronous.

    Type definition: `Callable[[], Awaitable[IT]]`
    """

    def __init__(self, fn: Callable[[], IT] | Callable[[], Awaitable[IT]]):
        if isinstance(fn, AsyncValueFn):
            fn = cast(AsyncValueFn[IT], fn)
            return fn
        self._is_async = is_async_callable(fn)
        self._fn = wrap_async(fn)

    async def __call__(self) -> IT:
        """
        Call the asynchronous function.
        """
        return await self._fn()

    @property
    def is_async(self) -> bool:
        """
        Was the original function asynchronous?

        Returns
        -------
        :
            Whether the original function is asynchronous.
        """
        return self._is_async

    @property
    def fn(self) -> Callable[[], IT] | Callable[[], Awaitable[IT]]:
        """
        Retrieve the original function

        Returns
        -------
        :
            Original function supplied to the `AsyncValueFn` constructor.
        """
        return self._fn


# class RendererShim(RendererBase, Generic[IT, P]):
#     def default_ui(
#         self, id: str, *args: P.args, **kwargs: P.kwargs
#     ) -> DefaultUIFnResultOrNone:
#         return super().default_ui(id)


# class Renderer(RendererShim[IT, ...], Generic[IT]):
class Renderer(RendererBase, Generic[IT]):
    """
    Renderer cls docs here
    TODO-barret - docs
    """

    # __name__: str ??

    # UI
    # TODO-barret; Utilize these!
    # default_ui_passthrough_args: tuple[str, ...] | None = None

    # App value function
    # _value_fn_original: ValueFnApp[IT]  # TODO-barret; Remove this?
    _value_fn: AsyncValueFn[IT | None]

    @property
    def value_fn(self) -> AsyncValueFn[IT | None]:
        return self._value_fn

    def _set_value_fn(self, value_fn: ValueFnApp[Any | None]) -> None:
        if not callable(value_fn):
            raise TypeError("Value function must be callable")

        # Copy over function name as it is consistent with how Session and Output
        # retrieve function names
        self.__name__ = value_fn.__name__

        # Set value function with extra meta information
        self._value_fn = AsyncValueFn(value_fn)

        # Allow for App authors to not require `@output`
        self._auto_register()

    """
    App-supplied output value function which returns type `IT`. This function is always
    asyncronous as the original app-supplied function possibly wrapped to execute
    asynchonously.
    """

    def __call__(self, value_fn: ValueFnApp[IT | None]) -> Self:
        """
        Renderer __call__ docs here; Sets app's value function
        TODO-barret - docs
        """

        self._set_value_fn(value_fn)

        return self

    def __init__(
        self,
        value_fn: ValueFn[IT | None] = None,
    ):
        # Do not display docs here. If docs are present, it could highjack the docs of
        # the subclass's `__init__` method.
        # """
        # Renderer - init docs here
        # """
        super().__init__()
        if callable(value_fn):
            # Register the value function
            self(value_fn)

    async def transform(self, value: IT) -> JSONifiable:
        """
        Renderer - transform docs here
        TODO-barret - docs
        """
        raise NotImplementedError(
            "Please implement either the `transform(self, value: IT)` or `render(self)` method.\n"
            "* `transform(self, value: IT)` should transform the `value` (of type `IT`) into JSONifiable object. Ex: `dict`, `None`, `str`. (standard)\n"
            "* `render(self)` method has full control of how a value is retrieved and utilized. For full control, use this method. (rare)"
            "\n By default, the `render` retrieves the value and then calls `transform` method on non-`None` values."
        )

    async def render(self) -> JSONifiable:
        """
        Renderer - render docs here
        TODO-barret - docs
        """
        value = await self.value_fn()
        if value is None:
            return None

        rendered = await self.transform(value)
        return rendered
