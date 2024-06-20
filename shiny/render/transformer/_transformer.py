from __future__ import annotations

# TODO-future; When `OutputRenderer` is removed, remove `output_args()`


__all__ = (
    "TransformerMetadata",
    "TransformerParams",
    "OutputRenderer",
    "OutputTransformer",
    "ValueFn",
    # "ValueFnSync",
    # "ValueFnAsync",
    # "TransformFn",
    "output_transformer",
    "is_async_callable",
)

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    NamedTuple,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from ..renderer import Jsonifiable, Renderer
from ..renderer._renderer import DefaultUIFn, DefaultUIFnResultOrNone

if TYPE_CHECKING:
    from ...session import Session

from ..._deprecated import warn_deprecated
from ..._docstring import add_example
from ..._typing_extensions import Concatenate, ParamSpec
from ..._utils import is_async_callable
from ...types import MISSING

# Input type for the user-spplied function that is passed to a render.xx
IT = TypeVar("IT")
# Output type after the OutputRenderer._exec method has been called on the IT object.
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

    Attributes
    ----------
    session
        The :class:`~shiny.Session` object of the current output value function.
    name
        The name of the output being rendered.
    """

    session: Session
    name: str


# Motivation for using this class:
# * https://peps.python.org/pep-0612/ does allow for prepending an arg (e.g.
#   `value_fn`).
# * However, the overload is not happy when both a positional arg (e.g. `value_fn`) is
#   dropped and the variadic positional args (`*args`) are kept.
# * The variadic positional args (`*args`) CAN NOT be dropped as PEP612 states that both
#   components of the `ParamSpec` must be used in the same function signature.
# * By making assertions on `P.args` to only allow for `*`, we _can_ make overloads that
#   use either the single positional arg (e.g. `value_fn`) or the `P.kwargs` (as
#   `P.args` == `*`)
class TransformerParams(Generic[P]):
    """
    Parameters for a transformer function

    This class is used to isolate the transformer function parameters away from
    internal implementation parameters used by Shiny.

    """

    def __init__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Parameters
        ----------
        *args
            No positional arguments should be supplied. Only keyword arguments should be
            supplied. (`*args` is required when using :class:`~typing.ParamSpec` even if
            transformer is only leveraging `**kwargs`.)
        **kwargs
            Keyword arguments for the corresponding renderer function.
        """

        # Make sure there no `args` at run time!
        # This check is related to `_assert_transform_fn` not accepting any `args`
        if len(args) > 0:
            print(args)
            raise RuntimeError("`args` should not be supplied")

        # `*args` must be defined with `**kwargs` (as per PEP612)
        # (even when expanded later when calling the transform function)
        # We need to store (and later retrieve) them, even if we know they are empty
        self.args = args
        self.kwargs = kwargs


# ======================================================================================
# Renderer / RendererSync / RendererAsync base class
# ======================================================================================

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

# ValueFnAsync = ValueFnAsync[IT]
# """
# App-supplied output value function which returns type `IT`. This function is always
# asyncronous as the original app-supplied function possibly wrapped to execute
# asynchonously.
# """

ValueFn = Union[ValueFnSync[IT], ValueFnAsync[IT]]
"""
App-supplied output value function which returns type `IT`. This function can be
synchronous or asynchronous.
"""

# `TransformFn` is a package author function that transforms an object of type `IT` into
# type `OT`.
TransformFn = Callable[Concatenate[TransformerMetadata, ValueFn[IT], P], Awaitable[OT]]
"""
Package author function that transforms an object of type `IT` into type `OT`.
"""


class OutputRenderer(
    # Inherit from `[Any]` to not change the type signature of `OutputRenderer[OT]` to `OuputRenderer[IT, OT]`.
    Renderer[Any],
    Generic[OT],
):
    """
    Output Renderer

    Transforms the output (of type `IT`) of an app-supplied output value function
    (`value_fn`) into type (`OT`). This transformed value is then sent to be an
    :class:`~shiny.Outputs` output value.

    When the `._run` method is invoked, the transform function (`transform_fn`)
    (typically defined by package authors) is invoked.

    The transform function (`transform_fn`) is given `meta` information
    (:class:`~shiny.render.transformer.TranformerMetadata`), the (app-supplied) value
    function (`ValueFnAsync[IT]`), and any keyword arguments supplied to the render decorator
    (`P`). For consistency, the first two parameters have been (arbitrarily) implemented
    as `_meta` and `_fn`.

    Typing
    ------
    * `IT`
        * The type returned by the app-supplied output value function (`value_fn`). This
          value should contain a `None` value to conform to the convention of app authors
          being able to return `None` to display nothing in the rendered output. Note that
          in many cases but not all, `IT` and `OT` will be the same.
    * `OT`
        * The type of the object returned by the transform function (`transform_fn`). This
          value should contain a `None` value to conform to display nothing in the
          rendered output.
    * `P`
        * The parameter specification defined by the transform function (`transform_fn`).
          It should **not** contain any `*args`. All keyword arguments should have a type
          and default value.

    See Also
    --------
    * :class:`~shiny.render.transformer.OutputRendererSync`
    * :class:`~shiny.render.transformer.OutputRendererAsync`
    """

    def __init__(
        self,
        *,
        value_fn: ValueFn[IT],
        transform_fn: TransformFn[IT, P, OT],
        params: TransformerParams[P],
        default_ui: Optional[DefaultUIFn] = None,
        default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
    ) -> None:
        """
        Parameters
        ----------
        value_fn
            App-provided output value function. It should return an object of type `IT`.
        transform_fn
            Package author function that transforms an object of type `IT` into type
            `OT`. The `params` will used as variadic keyword arguments.
        params
            App-provided parameters for the transform function (`transform_fn`).
        default_ui
            Optional function that takes an `output_id` string and returns a Shiny UI
            object that can be used to display the output. This allows render functions
            to respond to `_repr_html_` method calls in environments like Jupyter.
        """
        super().__init__()

        warn_deprecated(
            "`shiny.render.transformer.output_transformer()` and `shiny.render.transformer.OutputRenderer()` output render function utilities have been superseded by `shiny.render.renderer.Renderer` and will be removed in the near future."
        )

        if not is_async_callable(transform_fn):
            raise TypeError(
                self.__class__.__name__
                + " requires an async tranformer function (`transform_fn`)."
                " Please define your transform function as asynchronous."
                " Ex `async def my_transformer(....`"
            )

        self._value_fn = value_fn
        self._value_fn_is_async = is_async_callable(value_fn)  # legacy key
        # Copy over function name as it is consistent with how Session and Output
        # retrieve function names
        self.__name__ = value_fn.__name__
        # Initial value for output_id until it is set by the Session
        self.output_id = value_fn.__name__

        self._transformer = transform_fn
        self._params = params
        self._default_ui = default_ui
        self._default_ui_passthrough_args = default_ui_passthrough_args

        self._default_ui_args: tuple[object, ...] = tuple()
        self._default_ui_kwargs: dict[str, object] = dict()

        # Register the value function with the parent Renderer class
        self(value_fn)

    def _meta(self) -> TransformerMetadata:
        """
        Returns a named tuple of values: `session` (the :class:`~shiny.Session` object),
        and `name` (the name of the output being rendered)
        """
        from ...session import require_active_session

        session = require_active_session(None)
        return TransformerMetadata(
            session=session,
            name=self.output_id,
        )

    async def _run(self) -> OT:
        """
        Executes the (async) tranform function

        The transform function will receive the following arguments: meta information of
        type :class:`~shiny.render.transformer.TransformerMetadata`, an app-defined
        render function of type :class:`~shiny.render.RenderFnAsync`, and `*args` and
        `**kwargs` of type `P`.

        Note: `*args` will always be empty as it is an expansion of
        :class:`~shiny.render.transformer.TransformerParams` which does not allow positional arguments.
        `*args` is required to use with `**kwargs` when using
        `typing.ParamSpec`.
        """
        ret = await self._transformer(  # pyright: ignore
            # TransformerMetadata
            self._meta(),
            # Callable[[], IT] | Callable[[], Awaitable[IT]]
            self._value_fn,
            # P
            *self._params.args,
            **self._params.kwargs,
        )
        return ret

    # # Shims for Renderer class #############################

    def auto_output_ui(
        self,
        **kwargs: object,
    ) -> DefaultUIFnResultOrNone:
        if self._default_ui is None:
            return None

        if self._default_ui_passthrough_args is not None:
            kwargs.update(
                {
                    k: v
                    for k, v in self._params.kwargs.items()
                    if k in self._default_ui_passthrough_args and v is not MISSING
                }
            )

        return self._default_ui(self.output_id, *self._default_ui_args, **kwargs)

    async def render(self) -> Jsonifiable:
        ret = await self._run()
        # Really, OT should be bound by Jsonifiable.
        # But we can't do that now as types like TypedDict break on Jsonifiable
        # (We also don't really care as we're moving to `Renderer` class)
        jsonifiable_ret = cast(Jsonifiable, ret)
        return jsonifiable_ret


# Using a second class to help clarify that it is of a particular type
class OutputRendererSync(OutputRenderer[OT]):
    """
    Output Renderer (Synchronous)

    See Also
    --------
    * :class:`~shiny.render.transformer.OutputRenderer`
    * :class:`~shiny.render.transformer.OutputRendererAsync`
    """

    def __init__(
        self,
        value_fn: ValueFnSync[IT],
        transform_fn: TransformFn[IT, P, OT],
        params: TransformerParams[P],
        default_ui: Optional[DefaultUIFn] = None,
        default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
    ) -> None:
        if is_async_callable(value_fn):
            raise TypeError(
                self.__class__.__name__ + " requires a synchronous render function"
            )
        # super == OutputRenderer[OT]
        super().__init__(
            value_fn=value_fn,
            transform_fn=transform_fn,
            params=params,
            default_ui=default_ui,
            default_ui_passthrough_args=default_ui_passthrough_args,
        )


# The reason for having a separate RendererAsync class is because the _run
# method is marked here as async; you can't have a single class where one method could
# be either sync or async.
class OutputRendererAsync(OutputRenderer[OT]):
    """
    Output Renderer (Asynchronous)

    See Also
    --------
    * :class:`~shiny.render.transformer.OutputRenderer`
    * :class:`~shiny.render.transformer.OutputRendererSync`
    """

    def __init__(
        self,
        value_fn: ValueFnAsync[IT],
        transform_fn: TransformFn[IT, P, OT],
        params: TransformerParams[P],
        default_ui: Optional[DefaultUIFn] = None,
        default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
    ) -> None:
        if not is_async_callable(value_fn):
            raise TypeError(
                self.__class__.__name__ + " requires an asynchronous render function"
            )

        # super == OutputRenderer[OT]
        super().__init__(
            value_fn=value_fn,
            transform_fn=transform_fn,
            params=params,
            default_ui=default_ui,
            default_ui_passthrough_args=default_ui_passthrough_args,
        )


# ======================================================================================
# Restrict the transformer function
# ======================================================================================


# assert: No variable length positional values;
# * We need a way to distinguish between a plain function and args supplied to the next
#   function. This is done by not allowing `*args`.
# assert: All `**kwargs` of transformer should have a default value
# * This makes calling the method with both `()` and without `()` possible / consistent.
def _assert_transformer(transform_fn: TransformFn[IT, P, OT]) -> None:
    params = inspect.Signature.from_callable(transform_fn).parameters

    if len(params) < 2:
        raise TypeError(
            "`transformer=` must have 2 positional parameters which have type "
            "`TransformerMetadata` and `ValueFnAsync` respectively"
        )

    for i, param in zip(range(len(params)), params.values()):
        # # Not a good test as `param.annotation` has type `str` and the type could
        # # have been renamed. We need to do an `isinstance` check but do not have
        # # access to the objects
        # if i == 0:
        #     assert param.annotation == "TransformerMetadata"
        # if i == 1:
        #     assert (param.annotation or "").startswith("RenderFnAsync")
        if i < 2 and not (
            param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            or param.kind == inspect.Parameter.POSITIONAL_ONLY
        ):
            raise TypeError(
                "`transformer=` must have 2 positional parameters which have type "
                "`TransformerMetadata` and `RenderFnAsync` respectively"
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
# OutputTransformer
# ======================================================================================


# Signature of a renderer decorator function
OutputRendererDecorator = Callable[[ValueFn[IT]], OutputRenderer[OT]]
"""
Decorator function that takes the output value function (then calls it and transforms
the value) and returns an :class:`~shiny.render.transformer.OutputRenderer`.
"""

# Signature of a decorator that can be called with and without parentheses
# With parens returns a `OutputRenderer[OT]`
# Without parens returns a `OutputRendererDeco[IT, OT]`
OutputTransformerFn = Callable[
    [
        Optional[ValueFn[IT]],
        TransformerParams[P],
    ],
    Union[OutputRenderer[OT], OutputRendererDecorator[IT, OT]],
]
"""
Generic overload definition for a decorator that can be called with and without
parentheses. If called with parentheses, it returns an decorator which returns an
:class:`~shiny.render.transformer.OutputRenderer`. If called without parentheses, it
returns an :class:`~shiny.render.transformer.OutputRenderer`.
"""


class OutputTransformer(Generic[IT, OT, P]):
    """
    Output Transformer class

    This class creates helper types and methods for defining an overloaded renderer
    decorator. By manually defining the overloads locally, the function signatures are
    as clean as possible (and therefore easier to read and understand).

    When called, an `OutputTransfomer` takes the value returned from the app-supplied
    output value function and any app-supplied paramters and passes them through the
    component author's transformer function, and returns the transformed result.

    Attributes
    ----------
    ValueFn
        The function type for the app-supplied output value function. This function may
        be both synchronous or asynchronous.
    OutputRenderer
        The return type for the overload that accepts the app-supplied output value
        function and returns an object of
        :class:`~shiny.render.transformer.OutputRenderer`.
    OutputRendererDecorator
        The return type for the overload that accepts app-supplied parameters for the
        transform function. The return value is a decorator that accepts the
        app-supplied output value function and returns an object of
        :class:`~shiny.render.transformer.OutputRenderer`.

    See Also
    --------
    * :func:`~shiny.render.transformer.output_transformer`
    * :class:`~shiny.render.transformer.TransformerParams`
    * :class:`~shiny.render.transformer.OutputRenderer`
    """

    fn: OutputTransformerFn[IT, P, OT]
    ValueFn: Type[ValueFn[IT]]
    OutputRenderer: Type[OutputRenderer[OT]]
    OutputRendererDecorator: Type[OutputRendererDecorator[IT, OT]]

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
            params = (
                self.params()
            )  # pyright: ignore[reportCallIssue] ; Missing param spec args; False positive error as we know there should be no args.
        if not isinstance(params, TransformerParams):
            raise TypeError(
                "Expected `params` to be of type `TransformerParams` but received "
                f"`{type(params)}`. Please use `.params()` to create a "
                "`TransformerParams` object."
            )
        return self._fn(value_fn, params)

    def __init__(
        self,
        fn: OutputTransformerFn[IT, P, OT],
    ) -> None:
        self._fn = fn
        self.ValueFn = ValueFn[IT]
        self.OutputRenderer = OutputRenderer[OT]

        self.OutputRendererDecorator = OutputRendererDecorator[
            IT, OT
        ]  # pyright: ignore[reportAttributeAccessIssue] ; False positive error as the types should match the class definition. Not worrying about it as this code is deprecated.


@overload
def output_transformer(
    *,
    default_ui: Optional[DefaultUIFn] = None,
    default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
) -> Callable[[TransformFn[IT, P, OT]], OutputTransformer[IT, OT, P]]: ...


@overload
def output_transformer(
    transform_fn: TransformFn[IT, P, OT],
) -> OutputTransformer[IT, OT, P]: ...


@add_example()
def output_transformer(
    transform_fn: TransformFn[IT, P, OT] | None = None,
    *,
    default_ui: Optional[DefaultUIFn] = None,
    default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
) -> (
    OutputTransformer[IT, OT, P]
    | Callable[[TransformFn[IT, P, OT]], OutputTransformer[IT, OT, P]]
):
    """
    Deprecated. Please use :class:`~shiny.render.renderer.Renderer` instead.

    Output transformer decorator.

    This decorator method is a convenience method to generate the appropriate types and
    internal implementation for an overloaded renderer method. This method will provide
    you with all the necessary types to define two different overloads: one for when the
    decorator is called without parentheses and another for when it is called with
    parentheses where app authors can pass in parameters to the renderer.

    Transform function
    ------------------

    The output renderer's transform function (`transform_fn`) is the key building block
    for `output_transformer`. It is a package author function that calls the app-defined
    output value function (`value_fn`) transforms the result of type `IT` into type
    `OT`.

    The transform function is supplied meta output information, the (app-supplied) value
    function, and any keyword arguments supplied to the output tranformer decorator:

    * The first parameter to the handler function has the class
      :class:`~shiny.render.transformer.TransformerMetadata` and is typically called
      `_meta`. This information gives context to the handler while trying to
      resolve the app-supplied value function (typically called `_fn`).
    * The second parameter is the app-defined output value function (e.g. `_fn`). It's
      return type (`IT`) determines what types can be returned by the app-supplied
      output value function. For example, if `_fn` has the type `ValueFnAsync[str | None]`,
      both the `str` and `None` types are allowed to be returned from the app-supplied
      output value function.
    * The remaining parameters are the keyword arguments (e.g. `alt:Optional[str] =
      None` or `**kwargs: object`) that app authors may supply to the renderer (when the
      renderer decorator is called with parentheses). Variadic positional parameters
      (e.g. `*args`) are not allowed. All keyword arguments should have a type and
      default value. No default value is needed for keyword arguments that are passed
      through (e.g. `**kwargs: Any`).

    The transform function's return type (`OT`) determines the output type of the
    :class:`~shiny.render.transformer.OutputRenderer`. Note that in many cases (but not
    all!) `IT` and `OT` will be the same. The `None` type should typically be defined in
    both `IT` and `OT`. If `IT` allows for `None` values, it (typically) signals that
    nothing should be rendered. If `OT` allows for `None` and returns a `None` value,
    shiny will not render the output.

    Notes
    -----

    * When defining the renderer decorator overloads, if you have extra parameters of
      `**kwargs: object`, you may get a type error about incompatible signatures. To fix
      this, you can use `**kwargs: Any` instead or add `_fn: None = None` as the first
      parameter in the overload containing the `**kwargs: object`.

    * The `transform_fn` should be defined as an asynchronous function but should only
      asynchronously yield (i.e. use `await` syntax) when the value function (the second
      parameter of type `ValueFn[IT]`) is awaitable. If the value function is not
      awaitable (i.e. it is a _synchronous_ function), then the execution of the
      transform function should also be synchronous.

    Parameters
    ----------
    transform_fn
        Asynchronous function used to determine the app-supplied output value function
        return type (`IT`), the transformed type (`OT`), and the keyword arguments (`P`)
        app authors can supply to the renderer decorator.
    default_ui
        Optional function that takes an `output_id` string and returns a Shiny UI object
        that can be used to display the output. This allows render functions to respond
        to `_repr_html_` method calls in environments like Jupyter.

    Returns
    -------
    :
        An :class:`~shiny.render.transformer.OutputTransformer` object that can be used to
        define two overloads for your renderer function. One overload is for when the
        renderer is called without parentheses and the other is for when the renderer is
        called with parentheses.
    """

    # If default_ui_passthrough_args was used, modify the default_ui function so it is
    # ready to mix in extra arguments from the decorator.
    def output_transformer_impl(
        transform_fn: TransformFn[IT, P, OT],
    ) -> OutputTransformer[IT, OT, P]:
        _assert_transformer(transform_fn)

        def renderer_decorator(
            value_fn: ValueFn[IT] | None,
            params: TransformerParams[P],
        ) -> OutputRenderer[OT] | OutputRendererDecorator[IT, OT]:
            def as_value_fn(
                fn: ValueFn[IT],
            ) -> OutputRenderer[OT]:
                if is_async_callable(fn):
                    return OutputRendererAsync(
                        fn,
                        transform_fn,
                        params,
                        default_ui,
                        default_ui_passthrough_args,
                    )
                else:
                    # To avoid duplicate work just for a typeguard, we cast the function
                    fn = cast(ValueFnSync[IT], fn)
                    return OutputRendererSync(
                        fn,
                        transform_fn,
                        params,
                        default_ui,
                        default_ui_passthrough_args,
                    )

            if value_fn is None:
                return as_value_fn
            val = as_value_fn(value_fn)
            return val

        return OutputTransformer(renderer_decorator)

    if transform_fn is not None:
        return output_transformer_impl(transform_fn)
    else:
        return output_transformer_impl


async def resolve_value_fn(value_fn: ValueFn[IT]) -> IT:
    """
    Resolve the value function

    This function is used to resolve the value function (`value_fn`) to an object of
    type `IT`. If the value function is asynchronous, it will be awaited. If the value
    function is synchronous, it will be called.

    While always using an async method within an output transform function is not
    appropriate, this method may be safely used to avoid boilerplate.

    Replace this:
    ```python
    if is_async_callable(_fn):
        x = await _fn()
    else:
        x = cast(ValueFnSync[IT], _fn)()
    ```

    With this:
    ```python
    x = await resolve_value_fn(_fn)
    ```

    Parameters
    ----------
    value_fn
        App-supplied output value function which returns type `IT`. This function can be
        synchronous or asynchronous.

    Returns
    -------
    :
        The resolved value from `value_fn`.
    """
    if is_async_callable(value_fn):
        return await value_fn()
    else:
        # To avoid duplicate work just for a typeguard, we cast the function
        value_fn = cast(ValueFnSync[IT], value_fn)
        return value_fn()
