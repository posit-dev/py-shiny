from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    TypeVar,
    Union,
    cast,
)

from htmltools import MetadataNode, Tag, TagList

from ..._docstring import add_example
from ..._typing_extensions import Self
from ..._utils import is_async_callable, wrap_async
from ...types import Jsonifiable

if TYPE_CHECKING:
    from ...session import Session

# TODO-barret-docs: Double check docs are rendererd
# Missing first paragraph from some classes: Example: TransformerMetadata.
# No init method for TransformerParams. This is because the `DocClass` object does not
# display methods that start with `_`. Therefore no `__init__` or `__call__` methods are
# displayed. Even if they have docs.


__all__ = (
    "Renderer",
    "Jsonifiable",
    "ValueFn",
    "Jsonifiable",
    "AsyncValueFn",
    "RendererT",
)


RendererT = TypeVar("RendererT", bound="Renderer[Any]")
"""
Generic output renderer class to pass the original Renderer subclass through a decorator
function.

When accepting and returning a `Renderer` class, utilize this TypeVar as to not reduce
the variable type to `Renderer[Any]`
"""

IT = TypeVar("IT")
"""
Return type from the user-supplied value function passed into the renderer.
"""


DefaultUIFnResult = Union[TagList, Tag, MetadataNode, str]
DefaultUIFnResultOrNone = Union[DefaultUIFnResult, None]
DefaultUIFn = Callable[[str], DefaultUIFnResultOrNone]

# Requiring `None` type throughout the value functions as `return` returns `None` type.
# This is typically paired with `req(False)` to exit quickly.
# If package authors want to NOT allow `None` type, they can capture it in a custom
#   render method with a runtime error. (Or make a new RendererThatCantBeNone class)
ValueFn = Union[
    Callable[[], Union[IT, None]],
    Callable[[], Awaitable[Union[IT, None]]],
]
"""
App-supplied output value function which returns type `IT` or `None`. This function can
be synchronous or asynchronous.
"""


@add_example()
class Renderer(Generic[IT]):
    """
    Output renderer class

    An output renderer is a class that will take in a callable function (value
    function), transform the returned value into a JSON-serializable object, and send
    the result to the browser.

    When the value function is received, the renderer will be auto registered with
    the current session's `Output` class, hooking it into Shiny's reactive graph. By
    auto registering as an `Output`, it allows for App authors to skip adding `@output`
    above the renderer. (If programmatic `id` is needed, `@output(id="foo")` can still be
    used!)

    There are two methods that must be implemented by the subclasses:
    `.auto_output_ui(self)` and either `.transform(self, value: IT)` or `.render(self)`.

    * In Express mode, the output renderer will automatically render its UI via
      `.auto_output_ui(self)`. This helper method allows App authors to skip adding a
      `ui.output_*` function to their UI, making Express mode even more concise. If more
      control is needed over the UI, `@ui.hold` can be used to suppress the auto
      rendering of the UI. When using `@ui.hold` on a renderer, the renderer's UI will
      need to be added to the app to connect the rendered output to Shiny's reactive
      graph.
    * The `render` method is responsible for executing the value function and performing
      any transformations for the output value to be JSON-serializable (`None` is a
      valid value!). To avoid the boilerplate of resolving the value function and
      returning early if `None` is received, package authors may implement the
      `.transform(self, value: IT)` method. The `transform` method's sole job is to
      _transform_ non-`None` values into an object that is JSON-serializable.
    """

    # Q: Could we do this with typing without putting `P` in the Generic?
    # A: No. Even if we had a `P` in the Generic, the calling decorator would not have access to it.
    # Idea: Possibly use a chained method of `.ui_kwargs()`? https://github.com/posit-dev/py-shiny/issues/971
    _auto_output_ui_kwargs: dict[str, Any] = dict()

    __name__: str
    """
    Name of output function supplied. (The value **will not** contain a module prefix.)

    Set within `.__call__()` method.
    """

    output_id: str
    """
    Output function name or ID (provided to `@output(id=)`).

    This value **will not** contain a module prefix (or session name-spacing). To get
    the fully resolved ID, call
    `shiny.session.require_active_session(None).ns(self.output_id)`.

    An initial value of `.__name__` (set within `Renderer.__call__(_fn)`) will be used
    until the output renderer is registered within the session.
    """

    fn: AsyncValueFn[IT]
    """
    App-supplied output value function which returns type `IT`. This function is always
    asyncronous as the original app-supplied function possibly wrapped to execute
    asynchonously.
    """

    def __call__(self, _fn: ValueFn[IT]) -> Self:
        """
        Add the value function to the renderer.

        Addition actions performed:
        * Store the value function name.
        * Set the Renderer's `output_id` to the function name.
        * Auto register (given a `Session` exists) the Renderer

        Parameters
        ----------
        _fn
            Value function supplied by the App author. This function can be synchronous
            or asynchronous.

        Returns
        -------
        :
            Original renderer instance.
        """
        from ...session import get_current_session

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

        self._session = get_current_session()

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
        """
        Express mode method that automatically generates the output's UI.
        """
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
        self._session: Session | None = None
        super().__init__()

        self._auto_registered: bool = False

        # Must be done last
        if callable(_fn):
            # Register the value function
            self(_fn)

    async def transform(self, value: IT) -> Jsonifiable:
        """
        Transform an output value into a JSON-serializable object.

        When subclassing `Renderer`, this method can be implemented to transform
        non-`None` values into a JSON-serializable object.

        If a `.render()` method is not implemented, this method **must** be implemented.
        When the output is requested, the `Renderer`'s `.render()` method will execute
        the output value function, return `None` if the value is `None`, and call this
        method to transform the value into a JSON-serializable object.

        Note, only one of `.transform()` or `.render()` should be implemented.
        """
        raise NotImplementedError(
            "Please implement either the `transform(self, value: IT)`"
            " or `render(self)` method.\n"
            "* `transform(self, value: IT)` should transform the non-`None` `value`"
            " (of type `IT`) into a JSON-serializable object."
            " Ex: `dict`, `None`, `str`. (common)\n"
            "* `render(self)` method has full control of how an App author's value is"
            " retrieved (`self._fn()`) and processed. (rare)"
        )

    async def render(self) -> Jsonifiable:
        """
        Renders the output value function.

        This method is called when the renderer is requested to render its output.

        The `Renderer`'s `render()` implementation goes as follows:

        * Execute the value function supplied to the renderer.
        * If the output value is `None`, `None` will be returned.
        * If the output value is not `None`, the `.transform()` method will be called to
          transform the value into a JSON-serializable object.

        When overwriting this method in a subclass, the implementation should execute
        the value function `.fn` and return the transformed value (which is
        JSON-serializable).
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
                "No output UI exists for this type of render function: ",
                self.__class__.__name__,
            )
        return rendered_ui

    def _render_auto_output_ui(self) -> DefaultUIFnResultOrNone:
        from ...session import session_context

        with session_context(self._session):
            return self.auto_output_ui(
                # Pass the `@output_args(foo="bar")` kwargs through to the auto_output_ui function.
                **self._auto_output_ui_kwargs,
            )

    # ######
    # Auto registering output
    # ######

    def _on_register(self) -> None:
        if self._auto_registered:
            # We're being explicitly registered now. Undo the auto-registration.
            # (w/ module support)
            from ...session import require_active_session

            session = require_active_session(None)
            ns_name = session.output._ns(self.__name__)
            session.output.remove(ns_name)
            self._auto_registered = False
            self._session = session

    def _auto_register(self) -> None:
        """
        Auto registers the rendering method to the session output then the renderer is
        called.

        When `@output` is called on the renderer, the renderer is automatically
        un-registered via `._on_register()`.
        """
        # If in Express mode, register the output
        if not self._auto_registered:
            if self._session is not None:
                # Register output on reactive graph
                self._session.output(self)
                # We mark the fact that we're auto-registered so that, if an explicit
                # registration now occurs, we can undo this auto-registration.
                self._auto_registered = True


# Not inheriting from `WrapAsync[[], IT]` as python 3.8 needs typing extensions that
# doesn't support `[]` for a ParamSpec definition. :-( Would be minimal/clean if we
# could do `class AsyncValueFn(WrapAsync[[], IT]):`
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
