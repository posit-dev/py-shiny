from __future__ import annotations

from typing import (
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

# TODO-barret; POST-merge; Update shinywidgets


# TODO-future: docs; missing first paragraph from some classes: Example: TransformerMetadata.
# No init method for TransformerParams. This is because the `DocClass` object does not
# display methods that start with `_`. THerefore no `__init__` or `__call__` methods are
# displayed. Even if they have docs.


__all__ = (
    "Renderer",
    "Jsonifiable",
    "ValueFn",
    "AsyncValueFn",
    "RendererT",
)

RendererT = TypeVar("RendererT", bound="Renderer[Any]")
"""
Generic class to pass the Renderer class through a decorator.

When accepting and returning a `Renderer` class, utilize this TypeVar as to not reduce the variable type to `Renderer[Any]`
"""

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
Jsonifiable = Union[
    str,
    int,
    float,
    bool,
    None,
    List["Jsonifiable"],
    Tuple["Jsonifiable"],
    Dict[str, "Jsonifiable"],
]


DefaultUIFnResult = Union[TagList, Tag, MetadataNode, str]
DefaultUIFnResultOrNone = Union[DefaultUIFnResult, None]
DefaultUIFn = Callable[[str], DefaultUIFnResultOrNone]

# Requiring `None` type throughout the value functions as `return` returns `None` type.
# This is typically paired with `req(False)` to exit quickly.
# If package authors want to NOT allow `None` type, they can capture it in a custom render method with a runtime error. (Or make a new RendererThatCantBeNone class)
ValueFn = Union[
    Callable[[], Union[IT, None]],
    Callable[[], Awaitable[Union[IT, None]]],
]
"""
App-supplied output value function which returns type `IT`. This function can be
synchronous or asynchronous.
"""


class Renderer(Generic[IT]):
    """
    Output renderer class

    TODO-barret-docs
    """

    # Q: Could we do this with typing without putting `P` in the Generic?
    # A: No. Even if we had a `P` in the Generic, the calling decorator would not have access to it.
    # Idea: Possibly use a chained method of `.ui_kwargs()`? https://github.com/posit-dev/py-shiny/issues/971
    _auto_output_ui_kwargs: dict[str, Any] = dict()

    __name__: str
    """
    Name of output function supplied. (The value will not contain any module prefix.)

    Set within `.__call__()` method.
    """

    output_id: str
    """
    Output function name or ID (provided to `@output(id=)`).

    This value **will not** contain a module prefix (or session name-spacing). To get
    the fully resolved ID, call
    `shiny.session.require_active_session(None).ns(self.output_id)`.

    An initial value of `.__name__` (set within `Renderer.__call__(_fn)`) will be used until the
    output renderer is registered within the session.
    """

    fn: AsyncValueFn[IT]
    """
    App-supplied output value function which returns type `IT`. This function is always
    asyncronous as the original app-supplied function possibly wrapped to execute
    asynchonously.
    """

    def __call__(self, _fn: ValueFn[IT]) -> Self:
        """
        Renderer __call__ docs here; Sets app's value function

        TODO-barret-docs
        """

        if not callable(_fn):
            raise TypeError("Value function must be callable")

        # Set value function with extra meta information
        self.fn = AsyncValueFn(_fn)

        # Copy over function name as it is consistent with how Session and Output
        # retrieve function names
        self.__name__ = _fn.__name__

        # Set the value of `output_id` to the function name.
        # This helps with testing and other situations where no session is present
        # for auto-registration to occur.
        self.output_id = self.__name__

        # Allow for App authors to not require `@output`
        self._auto_register()

        # Return self for possible chaining of methods!
        return self

    def _set_output_metadata(
        self,
        *,
        output_id: str,
    ) -> None:
        """
        Method to be called within `@output` to set the renderer's metadata.

        Parameters
        ----------
        output_id : str
            Output function name or ID (provided to `@output(id=)`). This value **will
            not** contain a module prefix (or session name-spacing).
        """
        self.output_id = output_id

    def auto_output_ui(
        self,
        # *
        # **kwargs: object,
    ) -> DefaultUIFnResultOrNone:
        return None

    def __init__(
        self,
        _fn: Optional[ValueFn[IT]] = None,
    ) -> None:
        # Do not display docs here. If docs are present, it could highjack the docs of
        # the subclass's `__init__` method.
        # """
        # Renderer - init docs here
        # """
        super().__init__()

        self._auto_registered: bool = False

        # Must be done last
        if callable(_fn):
            # Register the value function
            self(_fn)

    async def transform(self, value: IT) -> Jsonifiable:
        """
        Renderer - transform docs here

        TODO-barret-docs
        """
        raise NotImplementedError(
            "Please implement either the `transform(self, value: IT)` or `render(self)` method.\n"
            "* `transform(self, value: IT)` should transform the `value` (of type `IT`) into Jsonifiable object. Ex: `dict`, `None`, `str`. (standard)\n"
            "* `render(self)` method has full control of how an App author's value is retrieved (`self._fn()`) and utilized. (rare)\n"
            "By default, the `render` retrieves the value and then calls `transform` method on non-`None` values."
        )

    async def render(self) -> Jsonifiable:
        """
        Renderer - render docs here

        TODO-barret-docs
        """
        value = await self.fn()
        if value is None:
            return None

        rendered = await self.transform(value)
        return rendered

    # ######
    # Tagify-like methods
    # ######
    def _repr_html_(self) -> str | None:
        rendered_ui = self._render_auto_output_ui()
        if rendered_ui is None:
            return None
        return TagList(rendered_ui)._repr_html_()

    def tagify(self) -> DefaultUIFnResult:
        rendered_ui = self._render_auto_output_ui()
        if rendered_ui is None:
            raise TypeError(
                "No default UI exists for this type of render function: ",
                self.__class__.__name__,
            )
        return rendered_ui

    def _render_auto_output_ui(self) -> DefaultUIFnResultOrNone:
        return self.auto_output_ui(
            # Pass the `@output_args(foo="bar")` kwargs through to the auto_output_ui function.
            **self._auto_output_ui_kwargs,
        )

    # ######
    # Auto registering output
    # ######
    """
    Auto registers the rendering method then the renderer is called.

    When `@output` is called on the renderer, the renderer is automatically un-registered via `._on_register()`.
    """

    def _on_register(self) -> None:
        if self._auto_registered:
            # We're being explicitly registered now. Undo the auto-registration.
            # (w/ module support)
            from ...session import require_active_session

            session = require_active_session(None)
            ns_name = session.output._ns(self.__name__)
            session.output.remove(ns_name)
            self._auto_registered = False

    def _auto_register(self) -> None:
        # If in Express mode, register the output
        if not self._auto_registered:
            from ...session import get_current_session

            s = get_current_session()
            if s is not None:
                # Register output on reactive graph
                s.output(self)
                # We mark the fact that we're auto-registered so that, if an explicit
                # registration now occurs, we can undo this auto-registration.
                self._auto_registered = True


# Not inheriting from `WrapAsync[[], IT]` as python 3.8 needs typing extensions that doesn't support `[]` for a ParamSpec definition. :-(
# Would be minimal/clean if we could do `class AsyncValueFn(WrapAsync[[], IT]):`
class AsyncValueFn(Generic[IT]):
    """
    App-supplied output value function which returns type `IT`.
    asynchronous.

    Type definition: `Callable[[], Awaitable[IT]]`
    """

    def __init__(
        self,
        fn: Callable[[], IT | None] | Callable[[], Awaitable[IT | None]],
    ):
        if isinstance(fn, AsyncValueFn):
            raise TypeError(
                "Must not call `AsyncValueFn.__init__` with an object of class `AsyncValueFn`"
            )
        self._is_async = is_async_callable(fn)
        self._fn = wrap_async(fn)
        self._orig_fn = fn

    async def __call__(self) -> IT | None:
        """
        Call the asynchronous function.
        """
        return await self._fn()

    def is_async(self) -> bool:
        """
        Was the original function asynchronous?

        Returns
        -------
        :
            Whether the original function is asynchronous.
        """
        return self._is_async

    def get_async_fn(self) -> Callable[[], Awaitable[IT | None]]:
        """
        Return the async value function.

        Returns
        -------
        :
            Async wrapped value function supplied to the `AsyncValueFn` constructor.
        """
        return self._fn

    def get_sync_fn(self) -> Callable[[], IT | None]:
        """
        Retrieve the original, synchronous value function function.

        If the original function was asynchronous, a runtime error will be thrown.

        Returns
        -------
        :
            Original, synchronous function supplied to the `AsyncValueFn` constructor.
        """
        if self._is_async:
            raise RuntimeError(
                "The original function was asynchronous. Use `async_fn` instead."
            )
        sync_fn = cast(Callable[[], IT], self._orig_fn)
        return sync_fn
