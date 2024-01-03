from __future__ import annotations

import typing
from functools import wraps

# TODO-barret; POST-merge; shinywidgets should not call `resolve_value_fn`


# TODO-future: docs; missing first paragraph from some classes: Example: TransformerMetadata.
# No init method for TransformerParams. This is because the `DocClass` object does not
# display methods that start with `_`. THerefore no `__init__` or `__call__` methods are
# displayed. Even if they have docs.

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
    "output_transformer_no_params",
    "output_transformer_simple",
    "is_async_callable",
    # "IT",
    # "OT",
    # "P",
)

import inspect
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    NamedTuple,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

from htmltools import MetadataNode, Tag, TagList

if TYPE_CHECKING:
    from ...session import Session

from ..._deprecated import warn_deprecated
from ..._docstring import add_example
from ..._typing_extensions import Concatenate, ParamSpec
from ..._utils import is_async_callable, wrap_async
from ...types import MISSING

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

    Attributes
    ----------
    session
        The :class:`~shiny.Session` object of the current output value function.
    name
        The name of the output being rendered.
    """

    session: Session
    name: str
    value_fn_is_async: bool


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


def empty_params() -> TransformerParams[P]:
    """
    Return `TransformerParams` definition with no parameters.
    """

    def inner(*args: P.args, **kwargs: P.kwargs) -> TransformerParams[P]:
        return TransformerParams[P](*args, **kwargs)

    return inner()


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
ValueFn = ValueFnAsync[IT]
"""
App-supplied output value function which returns type `IT`. This function is always
asyncronous as the original app-supplied function possibly wrapped to execute
asynchonously.
"""
ValueFnApp = Union[ValueFnSync[IT], ValueFnAsync[IT]]
"""
App-supplied output value function which returns type `IT`. This function can be
synchronous or asynchronous.
"""

# `TransformFn` is a package author function that transforms an object of type `IT` into
# type `OT`.
TransformFn = Callable[Concatenate[TransformerMetadata, ValueFn[IT], P], Awaitable[OT]]
"""
Package author function that transforms an object of type `IT` into type `OT`. It should
be defined as an asynchronous function.
"""

DefaultUIFn = Callable[[str], Union[TagList, Tag, MetadataNode, str]]
DefaultUIFnImpl = Union[
    DefaultUIFn,
    Callable[[Dict[str, object], str], Union[TagList, Tag, MetadataNode, str]],
]


class OutputRenderer(Generic[OT]):
    """
    Output Renderer

    Transforms the output (of type `IT`) of an app-supplied output value function
    (`value_fn`) into type (`OT`). This transformed value is then sent to be an
    :class:`~shiny.Outputs` output value.

    When the `.__call__` method is invoked, the transform function (`transform_fn`)
    (typically defined by package authors) is invoked.

    The transform function (`transform_fn`) is given `meta` information
    (:class:`~shiny.render.transformer.TranformerMetadata`), the (app-supplied) value
    function (`ValueFn[IT]`), and any keyword arguments supplied to the render decorator
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
    """

    async def __call__(self) -> OT:
        """
        Asynchronously executes the output renderer (both the app's output value function and transformer).

        All output renderers are asynchronous to accomodate that users can supply
        asyncronous output value functions and package authors can supply asynchronous
        transformer functions. To handle both possible situations cleanly, the
        `.__call__` method is executed as asynchronous.
        """
        return await self._run()

    def __init__(
        self,
        *,
        value_fn: ValueFnApp[IT],
        transform_fn: TransformFn[IT, P, OT],
        params: TransformerParams[P],
        default_ui: Optional[DefaultUIFnImpl] = None,
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

        # Copy over function name as it is consistent with how Session and Output
        # retrieve function names
        self.__name__ = value_fn.__name__

        if not is_async_callable(transform_fn):
            raise TypeError(
                """\
                OutputRenderer requires an async tranformer function (`transform_fn`).
                Please define your transform function as asynchronous. Ex `async def my_transformer(....`
                """
            )

        # Upgrade value function to be async;
        # Calling an async function has a ~35ns overhead (barret's machine)
        # Checking if a function is async has a 180+ns overhead (barret's machine)
        # -> It is faster to always call an async function than to always check if it is async
        # Always being async simplifies the execution
        self._value_fn_is_async = is_async_callable(value_fn)
        self._value_fn: ValueFn[IT] = wrap_async(value_fn)
        self._transformer = transform_fn
        self._params = params
        self.default_ui = default_ui
        self.default_ui_passthrough_args = default_ui_passthrough_args
        self.default_ui_args: tuple[object, ...] = tuple()
        self.default_ui_kwargs: dict[str, object] = dict()

        self._auto_registered = False

        from ...session import get_current_session

        s = get_current_session()
        if s is not None:
            s.output(self)
            # We mark the fact that we're auto-registered so that, if an explicit
            # registration now occurs, we can undo this auto-registration.
            self._auto_registered = True

    def on_register(self) -> None:
        if self._auto_registered:
            # We're being explicitly registered now. Undo the auto-registration.
            self._session.output.remove(self.__name__)
            self._auto_registered = False

    def _set_metadata(self, session: Session, name: str) -> None:
        """
        When `Renderer`s are assigned to Output object slots, this method is used to
        pass along Session and name information.
        """
        self._session: Session = session
        self._name: str = name

    def _meta(self) -> TransformerMetadata:
        """
        Returns a named tuple of values: `session` (the :class:`~shiny.Session` object),
        and `name` (the name of the output being rendered)
        """
        return TransformerMetadata(
            session=self._session,
            name=self._name,
            value_fn_is_async=self._value_fn_is_async,
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
        ret = await self._transformer(
            # TransformerMetadata
            self._meta(),
            # Callable[[], Awaitable[IT]]
            self._value_fn,
            # P
            *self._params.args,
            **self._params.kwargs,
        )
        return ret

    def _repr_html_(self) -> str | None:
        import htmltools

        if self.default_ui is None:
            return None
        return htmltools.TagList(self._render_default())._repr_html_()

    def tagify(self) -> TagList | Tag | MetadataNode | str:
        if self.default_ui is None:
            raise TypeError("No default UI exists for this type of render function")
        return self._render_default()

    def _render_default(self) -> TagList | Tag | MetadataNode | str:
        if self.default_ui is None:
            raise TypeError("No default UI exists for this type of render function")

        # Merge the kwargs from the render function passthrough, with the kwargs from
        # explicit @output_args call. The latter take priority.
        kwargs: dict[str, object] = dict()
        if self.default_ui_passthrough_args is not None:
            kwargs.update(
                {
                    k: v
                    for k, v in self._params.kwargs.items()
                    if k in self.default_ui_passthrough_args and v is not MISSING
                }
            )
        kwargs.update(
            {k: v for k, v in self.default_ui_kwargs.items() if v is not MISSING}
        )
        return cast(DefaultUIFn, self.default_ui)(
            self.__name__, *self.default_ui_args, **kwargs
        )


# # Using a second class to help clarify that it is of a particular type
# class OutputRendererSync(OutputRenderer[OT]):
#     """
#     Output Renderer (Synchronous)

#     This class is used to define a synchronous renderer. The `.__call__` method is
#     implemented to call the `._run` method synchronously.

#     See Also
#     --------
#     * :class:`~shiny.render.transformer.OutputRenderer`
#     * :class:`~shiny.render.transformer.OutputRendererAsync`
#     """

#     def __init__(
#         self,
#         value_fn: ValueFnSync[IT],
#         transform_fn: TransformFn[IT, P, OT],
#         params: TransformerParams[P],
#         default_ui: Optional[DefaultUIFnImpl] = None,
#         default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
#     ) -> None:
#         if is_async_callable(value_fn):
#             raise TypeError(
#                 self.__class__.__name__ + " requires a synchronous render function"
#             )
#         # super == Renderer
#         super().__init__(
#             value_fn=value_fn,
#             transform_fn=transform_fn,
#             params=params,
#             default_ui=default_ui,
#             default_ui_passthrough_args=default_ui_passthrough_args,
#         )


# # The reason for having a separate RendererAsync class is because the __call__
# # method is marked here as async; you can't have a single class where one method could
# # be either sync or async.
# class OutputRendererAsync(OutputRenderer[OT]):
#     """
#     Output Renderer (Asynchronous)

#     This class is used to define an asynchronous renderer. The `.__call__` method is
#     implemented to call the `._run` method asynchronously.

#     See Also
#     --------
#     * :class:`~shiny.render.transformer.OutputRenderer`
#     * :class:`~shiny.render.transformer.OutputRendererSync`
#     """

#     def __init__(
#         self,
#         value_fn: ValueFnAsync[IT],
#         transform_fn: TransformFn[IT, P, OT],
#         params: TransformerParams[P],
#         default_ui: Optional[DefaultUIFnImpl] = None,
#         default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
#     ) -> None:
#         if not is_async_callable(value_fn):
#             raise TypeError(
#                 self.__class__.__name__ + " requires an asynchronous render function"
#             )
#         # super == Renderer
#         super().__init__(
#             value_fn=value_fn,
#             transform_fn=transform_fn,
#             params=params,
#             default_ui=default_ui,
#             default_ui_passthrough_args=default_ui_passthrough_args,
#         )


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
            "`TransformerMetadata` and `ValueFn` respectively"
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
OutputRendererDecorator = Callable[[ValueFnApp[IT]], OutputRenderer[OT]]
"""
Decorator function that takes the output value function (then calls it and transforms
the value) and returns an :class:`~shiny.render.transformer.OutputRenderer`.
"""

# Signature of a decorator that can be called with and without parentheses
# With parens returns a `OutputRenderer[OT]`
# Without parens returns a `OutputRendererDeco[IT, OT]`
OutputTransformerFn = Callable[
    [
        Optional[ValueFnApp[IT]],
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

    def params(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> TransformerParams[P]:
        return TransformerParams(*args, **kwargs)

    def __call__(
        self,
        value_fn: ValueFnApp[IT] | None,
        params: TransformerParams[P] | None = None,
    ) -> OutputRenderer[OT] | OutputRendererDecorator[IT, OT]:
        if params is None:
            params = self.params()
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
        self.ValueFn = ValueFnApp[IT]
        self.OutputRenderer = OutputRenderer[OT]
        self.OutputRendererDecorator = OutputRendererDecorator[IT, OT]


@overload
def output_transformer(
    *,
    default_ui: Optional[DefaultUIFn] = None,
    default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
) -> Callable[[TransformFn[IT, P, OT]], OutputTransformer[IT, OT, P]]:
    ...


@overload
def output_transformer(
    transform_fn: TransformFn[IT, P, OT],
) -> OutputTransformer[IT, OT, P]:
    ...


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
    Output transformer decorator

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
      output value function. For example, if `_fn` has the type `ValueFn[str | None]`,
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
            value_fn: ValueFnApp[IT] | None,
            params: TransformerParams[P],
        ) -> OutputRenderer[OT] | OutputRendererDecorator[IT, OT]:
            def as_value_fn(
                fn: ValueFnApp[IT],
            ) -> OutputRenderer[OT]:
                return OutputRenderer(
                    value_fn=fn,
                    transform_fn=transform_fn,
                    params=params,
                    default_ui=default_ui,
                    default_ui_passthrough_args=default_ui_passthrough_args,
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


# # Barret

# Class needs to create an outputrenderer and call it later. Not convinced it'll work.
# Proposing that parens are required if typing is used. :-(


class BarretRenderer(Generic[IT, OT]):
    """
    BarretRenderer cls docs here
    """

    # Meta
    _session: Session
    _name: str
    # __name__: str ??

    # UI
    default_ui: DefaultUIFnImpl | None = None
    default_ui_passthrough_args: tuple[str, ...] | None = None
    # App value function
    _value_fn_original: ValueFnApp[IT]
    _value_fn: ValueFn[IT]

    # Transform function; transform value's IT -> OT
    # _transform_fn: TransformFn[IT, P, OT] | None = None

    # 0. Rename OutputRenderer to `OutputRendererLegacy` (or something)
    # 1. OutputRenderer becomes a protocol
    # PErform a runtime isinstance check on the class
    # Or runtime check for attribute callable field of `_set_metadata()`
    # 2. Don't use `P` within `OutputRenderer` base class. Instead, use `self.FOO` params within the child class / child render method
    # Only use Barret Renderer class and have users overwrite the transform or render method as they see fit.

    def __call__(self, value_fn: ValueFnApp[IT]) -> OutputRenderer[OT]:
        """
        BarretRenderer __call__ docs here; Sets app's value function
        """
        print("BarretRenderer - call", value_fn)
        if not callable(value_fn):
            raise TypeError("Value function must be callable")
        self._value_fn_original = value_fn
        self._value_fn = wrap_async(value_fn)

        async def render_wrapper(
            meta: TransformerMetadata,
            value_fn: ValueFn[IT],
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> OT:
            print("BarretRenderer - call - render_wrapper", meta, value_fn)
            rendered = await self.render()
            return rendered

        return OutputRenderer(
            value_fn=self._value_fn_original,
            transform_fn=render_wrapper,
            # params=self._params,
            params=empty_params(),
            default_ui=self.default_ui,
            default_ui_passthrough_args=self.default_ui_passthrough_args,
        )

    def __init__(
        self,
        _value_fn: ValueFnApp[IT] | None = None,
        # *init_args: P.args,
        # **init_kwargs: P.kwargs,
        # value_fn: ValueFnApp[IT],
        # transform_fn: TransformFn[IT, P, OT],
        # params: TransformerParams[P],
        # default_ui: Optional[DefaultUIFnImpl] = None,
        # default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
    ):
        """
        BarretRenderer - init docs here
        """
        print("BarretRenderer - init (no args/kwargs)")
        if callable(_value_fn):
            raise TypeError(
                "This should not be called with a callable value_fn! Only the `__call__` method should be called with a callable value_fn"
            )
        # self._params: TransformerParams[P] = TransformerParams(
        #     *init_args, **init_kwargs
        # )

    def _set_metadata(self, session: Session, name: str) -> None:
        """
        When `Renderer`s are assigned to Output object slots, this method is used to
        pass along Session and name information.
        """
        self._session: Session = session
        self._name: str = name

    async def render(self) -> OT:
        """
        BarretRenderer - render docs here
        """
        print("BarretRenderer - render")
        print("BarretRenderer - needs abc class?")
        value = await self._value_fn()
        return cast(OT, value)

    def __new__(
        _cls,
        _value_fn: ValueFnApp[IT] | None = None,
        *new_args: typing.Any,
        **new_kwargs: typing.Any,
    ) -> typing.Self:
        # """
        # Barret __new__ docs here; Intercepts the class creation,
        # possibly returning a decorator instead of a class

        # Check if bare class is being used as a decorator (called with a single callable
        # arg). If so, decorate the function and return.
        # """

        print("BarretRenderer - new", new_args, new_kwargs, _cls)
        # If only one arg is passed and it is a callable, return a decorator
        if callable(_value_fn):
            # if len(new_args) == 1 and callable(new_args[0]) and not new_kwargs:
            print("BarretRenderer - creating decorator!", _cls)
            # value_fn = new_args[0]

            out_ren = _cls()(_value_fn)
            return out_ren

            resolved_cls = _cls()
            resolved_cls._value_fn_original = value_fn
            resolved_cls._value_fn = wrap_async(value_fn)

            return resolved_cls

            new_class = super().__new__(_cls)
            return new_class(value_fn)

            # @wraps(wrapped)
            # def f(*f_args: object, **f_kwargs: object):
            #     print("BarretRenderer - new - f", f_args, f_kwargs)

            #     # with _cls() as _tag:
            #     #     return wrapped(*args, **kwargs) or _tag

            # return f

        # Return like normal. Let the other methods do the work.
        return super().__new__(_cls)


class BarretSimple(BarretRenderer[IT, OT | None]):
    # _params: TransformerParams[...]

    def __new__(
        _cls,
        _fn: ValueFnApp[IT] | None = None,
    ) -> typing.Self:
        # """
        # Barret __new__ docs here; Intercepts the class creation,
        # possibly returning a decorator instead of a class

        # Check if bare class is being used as a decorator (called with a single callable
        # arg). If so, decorate the function and return.
        # """

        print("BarretSimple - new", _cls)
        # If only one arg is passed and it is a callable, return a decorator
        if callable(_fn):
            print("BarretSimple - creating decorator!", _cls)

            out_ren = _cls()(_fn)
            return out_ren

            resolved_cls = _cls()
            resolved_cls._value_fn_original = _fn
            resolved_cls._value_fn = wrap_async(_fn)

            print("BarretSimple - exiting creating decorator!", _cls)

            return resolved_cls

            new_class = super().__new__(_cls)
            return new_class(_fn)

            # @wraps(wrapped)
            # def f(*f_args: object, **f_kwargs: object):
            #     print("BarretSimple - new - f", f_args, f_kwargs)

            #     # with _cls() as _tag:
            #     #     return wrapped(*args, **kwargs) or _tag

            # return f

        # Return like normal. Let the other methods do the work.
        return super().__new__(_cls)

    def __init__(
        self,
        _value_fn: ValueFnApp[IT] | None = None,
    ):
        """
        BarretSimple - init docs here
        """
        super().__init__()
        print("BarretSimple - init - no args, no kwargs")
        # self._params = empty_params()

    async def transform(self, value: IT) -> OT:
        """
        BarretSimple - transform docs here
        """
        print("BarretSimple - transform")
        print("BarretSimple - needs abc class?")
        return cast(OT, value)

    async def render(self) -> OT | None:
        """
        BarretSimple - render docs here
        """
        print("BarretSimple - render")
        value = await self._value_fn()
        if value is None:
            return None

        rendered = await self.transform(value)
        return rendered


# ======================================================================================
# Simple transformer
# ======================================================================================

# TODO-barret; Requirements:
# * At app rendering, both parens and no parens must both work as expected
# * Add extra class info on the outputted function (ex .OutputRendererDecorator)

# None

# TODO-barret; Document internally:
# Things that break passing through docs:
# * Returning a overloads with no type in function
# * Return type contains a union of functions (that represent overloads)
# * Returning a callable class instance
# Returning type aliases works, even if the function signature is big!

# # Simple transformer, no params
# * docs to be transferred
# * No parameters, -> no need for overloads!

# # Simple dict transformer
# * Receives value and returns a dict

R = TypeVar("R")
# # Does not work with function docs!
CallableDecoBad = Callable[P, R] | Callable[[], Callable[P, R]]
CallableDeco = Callable[[IT | None], OT | Callable[[IT], OT]]
TransformFnSimple = Callable[[TransformerMetadata, ValueFn[IT]], Awaitable[OT]]


class CallableDecoCls(Generic[IT, OT]):
    def __init__(self, fn: Callable[[IT], OT]) -> None:
        self._fn = fn

    async def __call__(self, fn: IT | None) -> OT | Callable[[IT], OT]:
        if fn is None:
            return self._fn
        else:
            return self._fn(fn)
        # return await self._fn()


class OutputRendererSimple(OutputRenderer[OT]):
    def __init__(
        self,
        *,
        value_fn: ValueFnApp[IT],
        transform_fn: TransformFnSimple[IT, OT],
        default_ui: Optional[DefaultUIFnImpl] = None,
        default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
    ) -> None:
        super().__init__(
            value_fn=value_fn,
            transform_fn=transform_fn,
            params=empty_params(),
            default_ui=default_ui,
            default_ui_passthrough_args=default_ui_passthrough_args,
        )


def output_transformer_no_params(
    # transform_fn: TransformFnSimple[IT, OT],
    # Require that all params are keyword arguments so that if a user calls `@output_transformer_no_params` (with no parens), an error is thrown
    *,
    default_ui: Optional[DefaultUIFn] = None,
    default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
    # # No docs!
    # ) -> CallableDecoBad[[ValueFnApp[IT]], OutputRendererSimple[OT]]:
    # # Ugly signature, but it works
    # ) -> Callable[
    #     [ValueFnApp[IT] | None],
    #     OutputRendererSimple[OT] | Callable[[ValueFnApp[IT]], OutputRendererSimple[OT]],
    # ]:
    #
    # No Docs
    # ) -> CallableDecoCls[ValueFnApp[IT], OutputRendererSimple[OT]]:
    # Works!
    # ) -> CallableDeco[ValueFnApp[IT], OutputRendererSimple[OT]]:
    # Works!
) -> Callable[
    [TransformFnSimple[IT, OT]], Callable[[ValueFnApp[IT]], OutputRendererSimple[OT]]
]:
    def with_transformer(
        transform_fn: TransformFnSimple[IT, OT],
    ) -> Callable[[ValueFnApp[IT]], OutputRendererSimple[OT]]:
        def with_value_fn(
            value_fn: ValueFnApp[IT],
        ) -> OutputRendererSimple[OT]:
            return OutputRendererSimple(
                value_fn=value_fn,
                transform_fn=transform_fn,
                default_ui=default_ui,
                default_ui_passthrough_args=default_ui_passthrough_args,
            )

        return with_value_fn

    return with_transformer

    # def renderer(
    #     fn: ValueFnApp[IT],
    # ) -> OutputRendererSimple[OT]:
    #     return OutputRendererSimple[OT](
    #         value_fn=fn,
    #         transform_fn=transform_fn,
    #         default_ui=default_ui,
    #         default_ui_passthrough_args=default_ui_passthrough_args,
    #     )

    # # @overload
    # # def renderer_impl() -> Callable[[ValueFnApp[IT]], OutputRendererSimple[OT]]:
    # #     ...

    # # @overload
    # # def renderer_impl(
    # #     fn: ValueFnApp[IT],
    # # ) -> OutputRendererSimple[OT]:
    # #     ...

    # def renderer_impl(
    #     fn: ValueFnApp[IT] | None = None,
    # ) -> (
    #     OutputRendererSimple[OT] | Callable[[ValueFnApp[IT]], OutputRendererSimple[OT]]
    # ):
    #     if fn is None:
    #         return renderer
    #     else:
    #         return renderer(fn)

    # return renderer_impl


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


def output_transformer_simple(
    *,
    default_ui: Optional[DefaultUIFn] = None,
    default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
) -> Callable[
    [Callable[[IT], JSONifiable] | Callable[[IT], Awaitable[JSONifiable]]],
    Callable[[ValueFnApp[IT]], OutputRendererSimple[JSONifiable]],
]:
    def simple_transformer(
        upgrade_fn: Callable[[IT], JSONifiable] | Callable[[IT], Awaitable[JSONifiable]]
    ) -> Callable[[ValueFnApp[IT]], OutputRendererSimple[JSONifiable]]:
        upgrade_fn = wrap_async(upgrade_fn)

        async def transform_fn(
            _meta: TransformerMetadata,
            _fn: ValueFn[IT | None],
        ) -> JSONifiable:
            res = await _fn()
            if res is None:
                return None

            ret = await upgrade_fn(res)
            return ret

        deco = output_transformer_no_params(
            default_ui=default_ui,
            default_ui_passthrough_args=default_ui_passthrough_args,
        )
        return deco(transform_fn)

    return simple_transformer


JOT = TypeVar("JOT", bound=JSONifiable)


def output_transformer_json(
    *,
    default_ui: Optional[DefaultUIFn] = None,
    default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
    # ) -> Callable[
    #     [Callable[[IT], JOT] | Callable[[IT], Awaitable[JOT]]],
    #     Callable[[ValueFnApp[IT]], OutputRendererSimple[JOT | None]],
    # ]:
):
    def simple_transformer(
        upgrade_fn: Callable[[IT], JOT]
        | Callable[[IT], Awaitable[JOT]]
        # ) -> Callable[[ValueFnApp[IT]], OutputRendererSimple[JOT | None]]:
    ):
        upgrade_fn = wrap_async(upgrade_fn)

        async def transform_fn(
            _meta: TransformerMetadata,
            _fn: ValueFn[IT | None],
        ) -> JOT | None:
            res = await _fn()
            if res is None:
                return None

            ret = await upgrade_fn(res)
            return ret

        with_transformer = output_transformer_params(
            default_ui=default_ui,
            default_ui_passthrough_args=default_ui_passthrough_args,
        )
        with_args = with_transformer(transform_fn)
        # def with_args2(
        #         (() -> (IT@simple_transformer | None)) | (() -> Awaitable[IT@simple_transformer | None]) | None
        #     ) -> (
        #         (((() -> (IT@simple_transformer | None)) | (() -> Awaitable[IT@simple_transformer | None])) -> OutputRenderer[JOT@simple_transformer | None]) | OutputRenderer[JOT@simple_transformer | None]
        #     )
        return with_args
        # with_value_fn = with_args()
        # return with_value_fn
        with_value_fn: BValueFn[IT, JOT] = with_args()
        return with_value_fn

    return simple_transformer


def output_transformer_json2(
    *,
    default_ui: Optional[DefaultUIFn] = None,
    default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
    # ) -> Callable[[TransformFn[IT, P, OT]], BArgsFn2[IT, P, OT]]:
):
    # _output_transform_fn = _  # Give clearer name

    def simple_transformer(
        upgrade_fn: Callable[[IT], JOT]
        | Callable[[IT], Awaitable[JOT]]
        # ) -> Callable[[ValueFnApp[IT]], OutputRendererSimple[JOT | None]]:
        # ) -> (
        #     Callable[[], Callable[[ValueFnApp[IT]], OutputRendererSimple[JOT | None]]]
        #     | Callable[[Optional[ValueFnApp[IT]], OutputRendererSimple[JOT | None]]
    ):
        upgrade_fn = wrap_async(upgrade_fn)

        async def transform_fn(
            _meta: TransformerMetadata,
            _fn: ValueFn[IT | None],
        ) -> JOT | None:
            res = await _fn()
            if res is None:
                return None

            ret = await upgrade_fn(res)
            return ret

        @typing.overload
        def output_renderer(
            _: None = None,
        ) -> Callable[[ValueFnApp[IT]], OutputRendererSimple[JOT | None]]:
            pass

        @typing.overload
        def output_renderer(
            value_fn: ValueFnApp[IT],
        ) -> OutputRendererSimple[JOT | None]:
            pass

        def output_renderer(  # pyright: ignore[reportGeneralTypeIssues]
            # def output_renderer(
            _: Optional[ValueFnApp[IT]] = None,
        ):
            _args_value_fn = _  # Give clearer name

            def with_value_fn(
                value_fn: ValueFnApp[IT],
            ) -> OutputRendererSimple[JOT | None]:
                return OutputRendererSimple(
                    value_fn=value_fn,
                    transform_fn=transform_fn,
                    default_ui=default_ui,
                    default_ui_passthrough_args=default_ui_passthrough_args,
                )

            if callable(_args_value_fn):
                # No args were given and the function was called without parens,
                # receiving an app value function. Ex:
                # @output_transformer_json2
                # def my_output():
                #     ...
                return with_value_fn(_args_value_fn)
            else:
                return with_value_fn

        return output_renderer

    return simple_transformer


# TODO-barret; Allow for no parens when creating the renderer. But discourage the pkg author.
# TODO-barret; Allow for no parens when calling the renderer in the app.
# TODO-barret; Add extra fields so that existing renderers can be used?
# TODO-barret; Replace the original `output_transformer` with this one?
# TODO-barret; Document `output_transformer_simple`
# TODO-barret; Can the return type of the output_transformer_simple be OT and not JSONifiable? (Just make sure it is a subset of JSONifiable)

# X = TypeVar("X")
# Deco = Callable[[]]

# Callable[
#     Callable[[ValueFnApp[IT]], OutputRenderer[OT]]

# BValueFnOut = OutputRenderer[OT]
BValueFnIn = ValueFnApp[IT]
BValueFn = Callable[[BValueFnIn[IT]], OutputRenderer[OT]]
BArgsFn = Callable[
    Concatenate[Optional[BValueFnIn[IT]], P],
    BValueFn[IT, OT] | OutputRenderer[OT],
]
BArgsFn2 = BValueFnIn[IT] | Callable[P, BValueFn[IT, OT]]


WithValueFn = Callable[[ValueFnApp[IT]], OutputRenderer[OT]]
WithArgsFn = WithValueFn[IT, OT] | OutputRenderer[OT]

WithTransformerFn = Callable[
    Concatenate[Optional[ValueFnApp[IT]], P],
    WithArgsFn[IT, OT],
]

# ## Barret notes:
# If we want to allow for no parens, then the return type is either
# * OutputRenderer[OT] == Callable[[], OT]
# * Callable[[ValueFnApp[IT]], OutputRenderer[OT]]

# By type definition rules, these are incompatible as one accepts a positional arg and the other does not.
# So we need to use an overload.
# However, using an overload gives the wrong function name for the no-paren call.
# * I believe this is a pylance error and could be fixed.
#
# Implementing with overloads, somehow the docs for render_caps_params are passed through!
# Current downside is that the fn name is `output_renderer` instead of the user's function name at decorator time. (This is a pylance error?)

# Using overloads does not allow for us to define the type of the function.
# Using overloads requires us to use pyright ignore statements as the overloads are not compatible with each other.


def output_transformer_params(
    # Require that all params are keyword arguments so that if a user calls `@output_transformer_no_params` (with no parens), an error is thrown
    # _: Optional[Callable[[TransformFn[IT, P, OT]], BArgsFn[IT, P, OT]]] = None,
    *,
    default_ui: Optional[DefaultUIFn] = None,
    default_ui_passthrough_args: Optional[tuple[str, ...]] = None,
    # ) -> Callable[[TransformFn[IT, P, OT]], BArgsFn2[IT, P, OT]]:
):
    """
    Output Transformer Params docs

    Explain about default ui!
    """
    # _output_transform_fn = _  # Give clearer name

    def with_transformer(
        transform_fn: TransformFn[IT, P, OT],
        # ) -> BArgsFn2[IT, P, OT]:
    ):
        @typing.overload
        def output_renderer(
            *args: P.args,
            **kwargs: P.kwargs,
            # ) -> Callable[[ValueFnApp[IT]], OutputRenderer[OT]]:
            # ) -> BValueFn[IT, OT] | OutputRenderer[OT]:
        ) -> BValueFn[IT, OT]:
            pass

        @typing.overload
        def output_renderer(  # pyright: ignore[reportOverlappingOverload]
            value_fn: BValueFnIn[IT],
            # ) -> Callable[[ValueFnApp[IT]], OutputRenderer[OT]]:
            # ) -> BValueFn[IT, OT] | OutputRenderer[OT]:
        ) -> OutputRenderer[OT]:
            pass

        def output_renderer(  # pyright: ignore[reportGeneralTypeIssues]
            _: Optional[BValueFnIn[IT]] = None,
            *args: P.args,
            **kwargs: P.kwargs,
            # ) -> Callable[[ValueFnApp[IT]], OutputRenderer[OT]]:
            # ) -> BValueFn[IT, OT] | OutputRenderer[OT]:
        ):
            async def transform_fn_with_params(
                _meta: TransformerMetadata, _fn: ValueFn[IT | None]
            ) -> OT:
                return await transform_fn(_meta, _fn, *args, **kwargs)

            _args_value_fn = _  # Give clearer name
            if len(args) > 0:
                raise RuntimeError(
                    "`*args` should not be supplied."
                    "\nDid you forget to add `()` to your render decorator?"
                )
            # params = TransformerParams[P](*args, **kwargs)

            def with_value_fn(
                value_fn: BValueFnIn[IT],
            ) -> OutputRenderer[OT]:
                return OutputRenderer(
                    value_fn=value_fn,
                    # params=params,
                    # transform_fn=transform_fn,
                    transform_fn=transform_fn_with_params,
                    params=empty_params(),
                    default_ui=default_ui,
                    default_ui_passthrough_args=default_ui_passthrough_args,
                )

            if callable(_args_value_fn):
                # No args were given and the function was called without parens,
                # receiving an app value function. Ex:
                # @output_transformer_params
                # def my_output():
                #     ...
                return with_value_fn(_args_value_fn)
            else:
                return with_value_fn

        # if callable(_fn):
        #     # No args were given and the function was called without parens,
        #     # receiving an app value function. Ex:
        #     # @output_transformer_params
        #     # def my_output():
        #     #     ...
        #     return with_value_fn(_fn)
        # else:
        #     return with_value_fn

        return output_renderer

    # # TODO-barret; Add more here
    # # with_transformer.OutputRendererDecorator = OutputRendererDecorator[]
    # # with_transformer.OutputRendererDecorator = OutputRendererDecorator[]
    # if callable(_output_transform_fn):
    #     return with_transformer(_output_transform_fn)
    # else:
    #     return with_transformer
    return with_transformer


async def resolve_value_fn(value_fn: ValueFnApp[IT]) -> IT:
    """
    Soft deprecated. Resolve the value function

    Deprecated: v0.7.0 - This function is no longer needed as all value functions are
    now async for consistency and speed.

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
    warn_deprecated(
        "`resolve_value_fn()` is unnecessary when resolving the value function in a custom render method. Now, the value function is always async. `resolve_value_fn()` will be removed in a future release."
    )
    if is_async_callable(value_fn):
        return await value_fn()
    else:
        # To avoid duplicate work just for a typeguard, we cast the function
        value_fn = cast(ValueFnSync[IT], value_fn)
        return value_fn()


# ######################################################################################


if (False):

    # # Goals
    # Simple-ish interface for component author
    # Component author only needs to implement one async function
    # For user, support parens and no parens
    # For user, support async and sync usage
    # Support docstrings with pyright for parens and no parens
    # Support docstrings for quartodoc

    # 0. Rename OutputRenderer to `OutputRendererLegacy` (or something)
    # 1. OutputRenderer becomes a protocol
    # PErform a runtime isinstance check on the class
    # Or runtime check for attribute callable field of `_set_metadata()`
    # 2. Don't use `P` within `OutputRenderer` base class. Instead, use `self.FOO` params within the child class / child render method
    # Only use Barret Renderer class and have users overwrite the transform or render method as they see fit.

    class json(BarretSimple[object, jsonifiable]):
        def __init__(self, _value_fn: Callable[[], object]):
            super().__init__(_value_fn)

        async def transform(self, value: object) -> jsonifiable:
            return json.parse(json.dumps(value))

    class json(BarretRenderer[jsonifiable, str]):
        default_ui = output_json
        """
        Docs! - no params
        """

        def __init__(self, _value_fn: Callable[[], jsonifiable], *, indent: int = 0):
            """
            Docs! - params
            """
            super().__init__(_value_fn)
            self.indent = indent

        async def render(self) -> str:
            value = await self._value_fn()
            if value is None:
                return None
            return await self.transform(value)













    # --------------------------------------------------

    class OutputRenderer2(Generic[IT], ABC):

        # Try to warn that the parameter is not being set; Later
        # @abcfield
        # default_ui

        # Called inside `_session` class when trying to retrive the value?
        async def _get_value(self) -> OT:
            return await self.render()

        def __init__(self, _value_fn: ValueFNApp[IT] | None = None):
            self._value_fn = _value_fn
            # self.default_ui = Not missing

        def __call__(self, _value_fn: ValueFNApp[IT]) -> typing.Self
            self._value_fn = _value_fn
            # TODO-barret; REturn self! Rewrite the whole base class as (almost) nothing is necessary anymore
            return LegacyOutputRenderer()


    class text(OutputRenderer2[str]):
        """Render decorator for text output"""
        default_ui = output_text
        default_ui = None

        def __init__(self, _value_fn: ValueFNApp[str] | None = None, *, to_case: str = "upper"):
            """
            Create a text renderer

            Parameters
            ----------
            _value_fn
                A function that returns the text to render
            to_case
                The case to convert the text to, by default "upper"
            """
            super().__init__(_value_fn)
            self.to_case = to_case

        def transform(self, value: str) -> JSONifiable:
            if self.to_case == "upper":
                return value.upper()
            elif self.to_case == "lower":
                return value.lower()
            else:
                return value

    class text(OutputRenderer2[str]):
        """Render decorator for text output"""
        default_ui = output_text
        default_ui = None

        def __init__(self, _value_fn: ValueFNApp[JSONIfiable] | None = None):
            """
            Create a text renderer

            Parameters
            ----------
            _value_fn
                A function that returns the text to render
            to_case
                The case to convert the text to, by default "upper"
            """
            super().__init__(_value_fn)
            # self.to_case = to_case


    @text
    def foo1():
        ...

    @text(to_case="lower")
    def foo2():
        ...
