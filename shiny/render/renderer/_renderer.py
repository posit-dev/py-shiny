from __future__ import annotations

import typing

# import inspect
from abc import ABC, abstractmethod
from typing import (  # NamedTuple,; Protocol,; cast,; overload,
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
)

from htmltools import MetadataNode, Tag, TagList

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

# from ... import ui as _ui
# from ..._deprecated import warn_deprecated
# from ..._docstring import add_example
# from ..._typing_extensions import Concatenate
from ..._utils import WrapAsync

__all__ = (
    "Renderer",
    "AsyncValueFn",
)

# from ...types import MISSING

# Input type for the user-spplied function that is passed to a render.xx
IT = TypeVar("IT")
# # Output type after the Renderer.__call__ method is called on the IT object.
# OT = TypeVar("OT")
# # Param specification for value_fn function
# P = ParamSpec("P")
# # Generic return type for a function
# R = TypeVar("R")


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


# class DefaultUIFn(Protocol):
#     def __call__(
#         self, id: str, *args: Any, **kwargs: Any
#     ) -> TagList | Tag | MetadataNode | str:
#         ...


DefaultUIFnResult = Union[TagList, Tag, MetadataNode, str]
DefaultUIFnResultOrNone = Union[DefaultUIFnResult, None]
DefaultUIFn = Callable[[str], DefaultUIFnResultOrNone]
DefaultUIFnImpl = Union[
    DefaultUIFn,
    Callable[[Dict[str, object], str], DefaultUIFnResultOrNone],
]

# A `ValueFn` function is an app-supplied function which returns an IT.
# It can be either synchronous or asynchronous
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
ValueFn = Optional[ValueFnApp[IT | None]]


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

    # TODO-barret; Could we do this with typing without putting `P` in the Generic?
    # TODO-barret; Maybe in the `Renderer` class? idk...
    _default_ui_kwargs: dict[str, Any] = dict()
    # _default_ui_args: tuple[Any, ...] = tuple()

    def _on_register(self) -> None:
        if self._auto_registered:
            # We're being explicitly registered now. Undo the auto-registration.
            # (w/ module support)
            ns_name = self.session.output._ns(self.__name__)
            self.session.output.remove(ns_name)
            self._auto_registered = False

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


class AsyncValueFn(WrapAsync[[], IT]):
    """
    App-supplied output value function which returns type `IT`.
    asynchronous.

    Type definition: `Callable[[], Awaitable[IT]]`
    """

    # VALUE_FN_TYPE = Callable[[], Awaitable[IT]]
    pass


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

    """
    App-supplied output value function which returns type `IT`. This function is always
    asyncronous as the original app-supplied function possibly wrapped to execute
    asynchonously.
    """

    # Transform function; transform value's IT -> OT
    # _transform_fn: TransformFn[IT, P, OT] | None = None

    # 0. Rename OutputRenderer to `OutputRendererLegacy` (or something)
    # 1. OutputRenderer becomes a protocol
    # Perform a runtime isinstance check on the class
    # Or runtime check for attribute callable field of `_set_metadata()`
    # 2. Don't use `P` within `OutputRenderer` base class. Instead, use `self.FOO` params within the child class / child render method
    # Only use Barret Renderer class and have users overwrite the transform or render method as they see fit.

    def __call__(self, value_fn: ValueFnApp[IT | None]) -> typing.Self:
        """
        Renderer __call__ docs here; Sets app's value function
        TODO-barret - docs
        """
        # print("Renderer - call", value_fn, value_fn.__name__)  # TODO-barret; Delete!
        if not callable(value_fn):
            raise TypeError("Value function must be callable")

        # Copy over function name as it is consistent with how Session and Output
        # retrieve function names
        self.__name__ = value_fn.__name__

        # Set value function with extra meta information
        self._value_fn = AsyncValueFn(value_fn)

        # If in Express mode, register the output
        if not self._auto_registered:
            from ...session import get_current_session

            s = get_current_session()
            if s is not None:
                s.output(self)
                # We mark the fact that we're auto-registered so that, if an explicit
                # registration now occurs, we can undo this auto-registration.
                self._auto_registered = True

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
        # print("Renderer - transform")
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
        # print("Renderer - render")
        value = await self.value_fn()
        if value is None:
            return None

        rendered = await self.transform(value)
        return rendered


# from collections.abc import Callable
# from typing import Concatenate, ParamSpec, TypeVar

# # P = ParamSpec("P")
# T = TypeVar("T")


# class text(Renderer[str]):
#     """
#     Reactively render text.

#     Returns
#     -------
#     :
#         A decorator for a function that returns a string.

#     Tip
#     ----
#     The name of the decorated function (or ``@output(id=...)``) should match the ``id``
#     of a :func:`~shiny.ui.output_text` container (see :func:`~shiny.ui.output_text` for
#     example usage).

#     See Also
#     --------
#     ~shiny.ui.output_text
#     """

#     def default_ui(self, id: str, placeholder: bool = True) -> str:
#         return "42 - UI"

#     async def transform(self, value: str) -> JSONifiable:
#         return str(value)


# # # import dominate


# # class Barret:
# class Barret(Generic[P, IT]):
#     # Same args as init
#     # def __new__(cls, *args: object, **kwargs: object) -> Barret[P, IT]:
#     #     print("Barret - new", args, kwargs)
#     #     return super().__new__(cls)

#     def __init__(self, *args: P.args, **kwargs: P.kwargs) -> None:
#         print("Barret - init", args, kwargs)
#         # super().__init__(*args, **kwargs)

#     def __call__(self, renderer: Renderer[IT]) -> typing.Self:
#         print("Barret - call", renderer.default_ui)
#         # default_ui: Callable[P, R]

#         return self


# def _decorate_renderer(
#     _renderer: RendererShim[IT, P],
#     *args: P.args,
#     **kwargs: P.kwargs,
# ) -> Callable[[RendererShim[IT, P]], RendererShim[IT, P]]:
#     # renderer: RendererShim[IT, P]

#     def _wrapper(renderer: RendererShim[IT, P]) -> RendererShim[IT, P]:
#         """Also does thing XY, but first does something else."""
#         # print(a**2)
#         print("wrapper - ", args, kwargs)
#         return renderer
#         # return f(*args, **kwargs)

#     return _wrapper

#     def get_param_spec(fn: Callable[P, object]) -> Callable[P, object]:
#         return P


# @Barret(placeholder=True)
# @text
# def _():
#     return "42"


# @_decorate_renderer(text, placeholder=True)
# @text
# def _():
#     return "42"


#     Pinner = get_param_spec(renderer.default_ui)

#     def _decorate(
#         f: Callable[Concatenate[str, P], T]
#     ) -> Callable[Concatenate[float, P], T]:
#         if f is not known_function:  # type: ignore[comparison-overlap]
#             raise RuntimeError("This is an exclusive decorator.")

#         def _wrapper(a: float, /, *args: P.args, **kwargs: P.kwargs) -> T:
#             """Also does thing XY, but first does something else."""
#             print(a**2)
#             return f(*args, **kwargs)

#         return _wrapper

#     renderer.default_ui = _decorate(renderer.default_ui)

#     return


# wrapper = _decorate(known_function)


# if __name__ == "__main__":
#     print(known_function(1, "2"))
#     print(wrapper(3.14, 10, "10"))
