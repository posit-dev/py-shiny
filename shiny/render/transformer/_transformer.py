# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

__all__ = (
    "TransformerMetadata",
    "TransformerParams",
    "OutputRenderer",
    "OutputTransformer",
    "ValueFnAsync",
    "output_transformer",
)

import inspect
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Generic,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
    cast,
)

if TYPE_CHECKING:
    from ...session import Session

from ... import _utils
from ..._docstring import add_example
from ..._typing_extensions import Concatenate, ParamSpec

# Input type for the user-spplied function that is passed to a render.xx
IT = TypeVar("IT")
# Output type after the Renderer.__call__ method is called on the IT object.
OT = TypeVar("OT")
# Param specification for value_fn function
P = ParamSpec("P")


# ======================================================================================
# Helper classes
# ======================================================================================


# Meta information to give `hander()` some context
class TransformerMetadata(NamedTuple):
    """
    Transformer metadata

    This class is used to hold meta information for a transformer function.

    Properties
    ----------
    is_async
        If `TRUE`, the app-supplied render function is asynchronous.
    session
        The :class:`~shiny.Session` object of the current render function.
    name
        The name of the output being rendered.
    """

    is_async: bool
    session: Session
    name: str


class TransformerParams(Generic[P]):
    """
    Parameters for a transformer function

    This class is used to hold the parameters for a transformer function. It is used to
    enforce that the parameters are used in the correct order.

    Properties
    ----------
    *args
        No positional arguments should be supplied. Only keyword arguments should be
        supplied.
    **kwargs
        Keyword arguments for the corresponding transformer function.
    """

    # Motivation for using this class:
    # * https://peps.python.org/pep-0612/ does allow for prepending an arg (e.g.
    #   `value_fn`).
    # * However, the overload is not happy when both a positional arg (e.g. `value_fn`)
    #   is dropped and the variadic positional args (`*args`) are kept.
    # * The variadic positional args (`*args`) CAN NOT be dropped as PEP612 states that
    #   both components of the `ParamSpec` must be used in the same function signature.
    # * By making assertions on `P.args` to only allow for `*`, we _can_ make overloads
    #   that use either the single positional arg (e.g. `value_fn`) or the `P.kwargs`
    #   (as `P.args` == `*`)
    def __init__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Properties
        ----------
        *args
            No positional arguments should be supplied. Only keyword arguments should be
            supplied.
        **kwargs
            Keyword arguments for the corresponding renderer function.
        """

        # Make sure there no `args` when running!
        # This check is related to `_assert_transform_fn` not accepting any `args`
        if len(args) > 0:
            raise RuntimeError("`args` should not be supplied")

        # `*args` must be defined with `**kwargs` (as per PEP612)
        # (even when expanded later when calling the handler function)
        # So we store them, even if we know they are empty
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def empty_params() -> TransformerParams[P]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> TransformerParams[P]:
            return TransformerParams[P](*args, **kwargs)

        return inner()


# ======================================================================================
# Renderer / RendererSync / RendererAsync base class
# ======================================================================================

# A `ValueFn` function is an app-supplied function which returns an IT.
# It can be either synchronous or asynchronous
ValueFnSync = Callable[[], IT]
ValueFnAsync = Callable[[], Awaitable[IT]]
ValueFn = Union[ValueFnSync[IT], ValueFnAsync[IT]]

# `TransformFn` is a package author function that transforms an object of type `IT` into type `OT`.
TransformFn = Callable[
    Concatenate[TransformerMetadata, ValueFnAsync[IT], P], Awaitable[OT]
]


class OutputRenderer(Generic[OT], ABC):
    """
    Output Renderer

    Base class for classes :class:`~shiny.render.RendererSync` and
    :class:`~shiny.render.RendererAsync`.

    When the `.__call__` method is invoked, the handler function (`transform_fn`)
    (typically defined by package authors) is asynchronously called. The handler
    function is given `meta` information, the (app-supplied) render function, and any
    keyword arguments supplied to the render decorator. For consistency, the first two
    parameters have been (arbitrarily) implemented as `_meta` and `_fn`.

    The (app-supplied) value function (`value_fn`) returns type `IT`. The handler
    function (defined by package authors) defines the parameter specification of type
    `P` and asynchronously returns an object of type `OT`. Note that in many cases but
    not all, `IT` and `OT` will be the same. `None` values should always be defined in
    `IT` and `OT`.


    Methods
    -------
    _is_async
        If `TRUE`, the app-supplied render function is asynchronous. Must be implemented
        in subclasses.
    _meta
        A named tuple of values: `is_async`, `session` (the :class:`~shiny.Session`
        object), and `name` (the name of the output being rendered)

    See Also
    --------
    * :class:`~shiny.render.RendererSync`
    * :class:`~shiny.render.RendererAsync`
    """

    @abstractmethod
    def __call__(self) -> OT:
        """
        Executes the renderer as a function. Must be implemented by subclasses.
        """
        ...

    def __init__(
        self,
        *,
        value_fn: ValueFn[IT],
        transform_fn: TransformFn[IT, P, OT],
        params: TransformerParams[P],
    ) -> None:
        """
        Renderer init method

        TODO-barret: docs
        Parameters
        ----------
        name
            Name of original output function. Ex: `my_txt`
        doc
            Documentation of the output function. Ex: `"My text output will be displayed
            verbatim".
        """
        # Copy over function name as it is consistent with how Session and Output
        # retrieve function names
        self.__name__ = value_fn.__name__

        if not _utils.is_async_callable(transform_fn):
            raise TypeError(
                self.__class__.__name__ + " requires an async handler function"
            )

        # `value_fn` is not required to be async. For consistency, we wrapped in an
        # async function so that when it's passed in to `transform_fn`, `value_fn` is
        # **always** an async function.
        self._value_fn = _utils.wrap_async(value_fn)
        self._transformer = transform_fn
        self._params = params

    def _set_metadata(self, session: Session, name: str) -> None:
        """
        When `Renderer`s are assigned to Output object slots, this method is used to
        pass along Session and name information.
        """
        self._session: Session = session
        self._name: str = name

    def _meta(self) -> TransformerMetadata:
        return TransformerMetadata(
            is_async=self._is_async(),
            session=self._session,
            name=self._name,
        )

    @abstractmethod
    def _is_async(self) -> bool:
        ...

    async def _run(self) -> OT:
        """
        Executes the (async) handler function

        The handler function will receive the following arguments: meta information of
        type :class:`~shiny.render.RenderMeta`, an app-defined render function of type
        :class:`~shiny.render.RenderFnAsync`, and `*args` and `**kwargs` of type `P`.

        Notes:
        * The app-defined render function will always be upgraded to be an async
          function.
        * `*args` will always be empty as it is an expansion of
          :class:`~shiny.render.RendererParams` which does not allow positional
          arguments.
        """
        ret = await self._transformer(
            # RenderMeta
            self._meta(),
            # Callable[[], Awaitable[IT]]
            self._value_fn,
            # P
            *self._params.args,
            **self._params.kwargs,
        )
        return ret


# Using a second class to help clarify that it is of a particular type
class OutputRendererSync(OutputRenderer[OT]):
    """
    Output Renderer (Synchronous)

    This class is used to define a synchronous renderer. The `.__call__` method is
    implemented to call the `._run` method synchronously.

    See Also
    --------
    * :class:`~shiny.render.Renderer`
    * :class:`~shiny.render.RendererAsync`
    """

    def _is_async(self) -> bool:
        """
        Meta information about the renderer being asynchronous or not.

        Returns
        -------
        :
            Returns `FALSE` as this is a synchronous renderer.
        """
        return False

    def __init__(
        self,
        value_fn: ValueFnSync[IT],
        transform_fn: TransformFn[IT, P, OT],
        params: TransformerParams[P],
    ) -> None:
        if _utils.is_async_callable(value_fn):
            raise TypeError(
                self.__class__.__name__ + " requires a synchronous render function"
            )
        # super == Renderer
        super().__init__(
            value_fn=value_fn,
            transform_fn=transform_fn,
            params=params,
        )

    def __call__(self) -> OT:
        return _utils.run_coro_sync(self._run())


# The reason for having a separate RendererAsync class is because the __call__
# method is marked here as async; you can't have a single class where one method could
# be either sync or async.
class OutputRendererAsync(OutputRenderer[OT]):
    """
    Output Renderer (Asynchronous)

    This class is used to define an asynchronous renderer. The `.__call__` method is
    implemented to call the `._run` method asynchronously.

    See Also
    --------
    * :class:`~shiny.render.Renderer`
    * :class:`~shiny.render.RendererSync`
    """

    def _is_async(self) -> bool:
        """
        Meta information about the renderer being asynchronous or not.

        Returns
        -------
        :
            Returns `TRUE` as this is an asynchronous renderer.
        """
        return True

    def __init__(
        self,
        value_fn: ValueFnAsync[IT],
        transform_fn: TransformFn[IT, P, OT],
        params: TransformerParams[P],
    ) -> None:
        if not _utils.is_async_callable(value_fn):
            raise TypeError(
                self.__class__.__name__ + " requires an asynchronous render function"
            )
        # super == Renderer
        super().__init__(
            value_fn=value_fn,
            transform_fn=transform_fn,
            params=params,
        )

    async def __call__(self) -> OT:  # pyright: ignore[reportIncompatibleMethodOverride]
        return await self._run()


# ======================================================================================
# Restrict the value function
# ======================================================================================


# assert: No variable length positional values;
# * We need a way to distinguish between a plain function and args supplied to the next
#   function. This is done by not allowing `*args`.
# assert: All kwargs of transformer should have a default value
# * This makes calling the method with both `()` and without `()` possible / consistent.
def _assert_transformer(transform_fn: TransformFn[IT, P, OT]) -> None:
    params = inspect.Signature.from_callable(transform_fn).parameters

    if len(params) < 2:
        raise TypeError(
            "`transformer=` must have 2 positional parameters which have type "
            "`RenderMeta` and `RenderFnAsync` respectively"
        )

    for i, param in zip(range(len(params)), params.values()):
        # # Not a good test as `param.annotation` has type `str` and the type could
        # # have been renamed. We need to do an `isinstance` check but do not have
        # # access to the objects
        # if i == 0:
        #     assert param.annotation == "RenderMeta"
        # if i == 1:
        #     assert (param.annotation or "").startswith("RenderFnAsync")
        if i < 2 and not (
            param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            or param.kind == inspect.Parameter.POSITIONAL_ONLY
        ):
            raise TypeError(
                "`transformer=` must have 2 positional parameters which have type "
                "`RenderMeta` and `RenderFnAsync` respectively"
            )

        # Make sure there are no more than 2 positional args
        if i >= 2 and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            raise TypeError(
                "`transformer=` must not contain more than 2 positional parameters"
            )
        # Make sure there are no `*args`
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            raise TypeError(
                "No variadic positional parameters (e.g. `*args`) can be supplied to "
                f"`transformer=`. Received: `{param.name}`. Please only use `*`."
            )
        # Make sure kwargs have default values
        if (
            param.kind == inspect.Parameter.KEYWORD_ONLY
            and param.default is inspect.Parameter.empty
        ):
            raise TypeError(
                f"In `transformer=`, parameter `{param.name}` did not have a default value"
            )


# ======================================================================================
# Renderer decorator
# ======================================================================================


# Signature of a renderer decorator function
OutputRendererDecorator = Callable[[ValueFn[IT]], OutputRenderer[OT]]
# Signature of a decorator that can be called with and without parentheses
# With parens returns a `Renderer[OT]`
# Without parens returns a `RendererDeco[IT, OT]`
OutputRendererImplFn = Callable[
    [
        Optional[ValueFn[IT]],
        TransformerParams[P],
    ],
    Union[OutputRenderer[OT], OutputRendererDecorator[IT, OT]],
]


class OutputTransformer(Generic[IT, OT, P]):
    """
    Output Transformer class

    A Transfomer takes the value returned from the user's render function, passes it
    through the component author's transformer function, and returns the result. TODO-barret: cleanup docs

    Properties
    ----------
    type_decorator
        The return type for the renderer decorator wrapper function. This should be used
        when the app-defined render function is `None` and extra parameters are being
        supplied.
    type_renderer_fn
        The (non-`None`) type for the renderer function's first argument that accepts an
        app-defined render function. This type should be paired with the return type:
        `type_renderer`.
    type_renderer
        The type for the return value of the renderer decorator function. This should be
        used when the app-defined render function is not `None`.
    type_impl_fn
        The type for the implementation function's first argument. This value handles
        both app-defined render functions and `None` and returns values appropriate for
        both cases. `type_impl_fn` should be paired with `type_impl`.
    type_impl
        The type for the return value of the implementation function. This value handles
        both app-defined render functions and `None` and returns values appropriate for
        both cases.

    See Also
    --------
    * :func:`~shiny.render.renderer_components`
    * :class:`~shiny.render.RendererParams`
    * :class:`~shiny.render.Renderer`
    """

    def params(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> TransformerParams[P]:
        return TransformerParams(*args, **kwargs)

    def __call__(
        self,
        value_fn: ValueFn[IT] | None,
        params: TransformerParams[P] | None = None,
    ) -> OutputRenderer[OT] | OutputRendererDecorator[IT, OT]:
        if params is None:
            params = self.params()
        if not isinstance(params, TransformerParams):
            raise TypeError(
                f"Expected `params` to be of type `RendererParams` but received `{type(params)}`. Please use `.params()` to create a `RendererParams` object."
            )
        return self._fn(value_fn, params)

    def __init__(
        self,
        fn: OutputRendererImplFn[IT, P, OT],
    ) -> None:
        self._fn = fn
        self.ValueFn = ValueFn[IT]
        self.OutputRenderer = OutputRenderer[OT]
        self.OutputRendererDecorator = OutputRendererDecorator[IT, OT]


@add_example()
def output_transformer(
    transform_fn: TransformFn[IT, P, OT],
) -> OutputTransformer[IT, OT, P]:
    """
    Renderer components decorator

    This decorator method is a convenience method to generate the appropriate types and
    internal implementation for an overloaded renderer method. This method will provide
    you with all the necessary types to define two different overloads: one for when the
    decorator is called without parentheses and another for when it is called with
    parentheses where app authors can pass in parameters to the renderer.

    ## Handler function

    The renderer's asynchronous handler function (`transform_fn`) is the key building
    block for `renderer_components`.

    The handler function is supplied meta renderer information, the (app-supplied)
    render function, and any keyword arguments supplied to the renderer decorator:
    * The first parameter to the handler function has the class
      :class:`~shiny.render.RenderMeta` and is typically called (e.g. `_meta`). This
      information gives context the to the handler while trying to resolve the
      app-supplied render function (e.g. `_fn`).
    * The second parameter is the app-defined render function (e.g. `_fn`). It's return
      type (`IT`) determines what types can be returned by the app-supplied render
      function. For example, if `_fn` has the type `RenderFnAsync[str | None]`, both the
      `str` and `None` types are allowed to be returned from the app-supplied render
      function.
    * The remaining parameters are the keyword arguments (e.g. `alt:Optional[str] =
      None` or `**kwargs: Any`) that app authors may supply to the renderer (when the
      renderer decorator is called with parentheses). Variadic positional parameters
      (e.g. `*args`) are not allowed. All keyword arguments should have a type and
      default value (except for `**kwargs: Any`).

    The handler's return type (`OT`) determines the output type of the renderer. Note
    that in many cases (but not all!) `IT` and `OT` will be the same. The `None` type
    should typically be defined in both `IT` and `OT`. If `IT` allows for `None` values,
    it (typically) signals that nothing should be rendered. If `OT` allows for `None`
    and returns a `None` value, shiny will not render the output.


    Notes
    -----

    When defining the renderer decorator overloads, if you have extra parameters of
    `**kwargs: object`, you may get a type error about incompatible signatures. To fix
    this, you can use `**kwargs: Any` instead or add `_fn: None = None` as the first
    parameter in the overload containing the `**kwargs: object`.

    Parameters
    ----------
    transform_fn
        Asynchronous function used to determine the app-supplied value type (`IT`), the
        rendered type (`OT`), and the parameters (`P`) app authors can supply to the
        renderer.

    Returns
    -------
    :
        A :class:`~shiny.render.RendererComponents` object that can be used to define
        two overloads for your renderer function. One overload is for when the renderer
        is called without parentheses and the other is for when the renderer is called
        with parentheses.
    """
    _assert_transformer(transform_fn)

    def renderer_decorator(
        value_fn: ValueFnSync[IT] | ValueFnAsync[IT] | None,
        params: TransformerParams[P],
    ) -> OutputRenderer[OT] | OutputRendererDecorator[IT, OT]:
        def as_value_fn(
            fn: ValueFnSync[IT] | ValueFnAsync[IT],
        ) -> OutputRenderer[OT]:
            if _utils.is_async_callable(fn):
                return OutputRendererAsync(fn, transform_fn, params)
            else:
                fn = cast(ValueFnSync[IT], fn)
                return OutputRendererSync(fn, transform_fn, params)

        if value_fn is None:
            return as_value_fn
        val = as_value_fn(value_fn)
        return val

    return OutputTransformer(renderer_decorator)
