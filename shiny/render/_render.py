# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

# TODO-barret; Revert base classes and use the original classes?
#   TODO-barret; Changelog - that RenderFunction no longer exists or deprecated


__all__ = (
    "text",
    "plot",
    "image",
    "table",
    "ui",
)

import base64
import inspect
import os
import sys
import typing
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
    overload,
    runtime_checkable,
)

from htmltools import TagChild

if TYPE_CHECKING:
    from ..session import Session
    from ..session._utils import RenderedDeps
    import pandas as pd

from .. import _utils
from .._namespaces import ResolvedId
from .._typing_extensions import Concatenate, ParamSpec, TypedDict
from ..types import ImgData
from ._try_render_plot import try_render_matplotlib, try_render_pil, try_render_plotnine

# Input type for the user-spplied function that is passed to a render.xx
IT = TypeVar("IT")
# Output type after the Renderer.__call__ method is called on the IT object.
OT = TypeVar("OT")
# Param specification for render_fn function
P = ParamSpec("P")


# ======================================================================================
# Helper classes
# ======================================================================================


# Meta information to give `hander()` some context
class RenderMeta(TypedDict):
    """
    Renderer meta information

    This class is used to hold meta information for a renderer handler function.

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


class RendererParams(Generic[P]):
    """
    Parameters for a renderer function

    This class is used to hold the parameters for a renderer function. It is used to
    enforce that the parameters are used in the correct order.

    Properties
    ----------
    *args
        No positional arguments should be supplied. Only keyword arguments should be
        supplied.
    **kwargs
        Keyword arguments for the corresponding renderer function.
    """

    # Motivation for using this class:
    # * https://peps.python.org/pep-0612/ does allow for prepending an arg (e.g.
    #   `render_fn`).
    # * However, the overload is not happy when both a positional arg (e.g.
    #   `render_fn`) is dropped and the variadic args (`*args`) are kept.
    # * The variadic args (`*args`) CAN NOT be dropped as PEP612 states that both
    #   components of the `ParamSpec` must be used in the same function signature.
    # * By making assertions on `P.args` to only allow for `*`, we _can_ make overloads
    #   that use either the single positional arg (e.g. `render_fn`) or the `P.kwargs`
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

        # `*args` must be defined with `**kwargs`
        # Make sure there no `args` when running!
        if len(args) > 0:
            raise RuntimeError("`args` should not be supplied")

        self.args = args
        self.kwargs = kwargs


# ======================================================================================
# Renderer / RendererSync / RendererAsync base class
# ======================================================================================
RenderFnSync = Callable[[], IT]
RenderFnAsync = Callable[[], Awaitable[IT]]
RenderFn = RenderFnSync[IT] | RenderFnAsync[IT]
HandlerFn = Callable[Concatenate[RenderMeta, RenderFnAsync[IT], P], Awaitable[OT]]


# A Renderer object is given a user-provided function (`handler_fn`) which returns an
# `OT`.
class Renderer(Generic[OT]):
    """
    Output Renderer

    Base class to build up :class:`~shiny.render.RendererSync` and
    :class:`~shiny.render.RendererAsync`.

    When the `.__call__` method is invoked, the handler function (typically defined by
    package authors) is called. The handler function is given `meta` information, the
    (app-supplied) render function, and any keyword arguments supplied to the render
    decorator.

    The (app-supplied) render function should return type `IT`. The handler function
    (defined by package authors) defines the parameter specification of type `P` and
    should asynchronously return an object of type `OT`. Note that in many cases but not
    all, `IT` and `OT` will be the same. `None` values must always be defined in `IT`
    and `OT`.


    See Also
    --------
    * :class:`~shiny.render.RendererRun`
    * :class:`~shiny.render.RendererSync`
    * :class:`~shiny.render.RendererAsync`
    """

    def __call__(self, *_) -> OT:
        """
        Executes the renderer as a function. Must be implemented by subclasses.
        """
        raise NotImplementedError

    def __init__(self, *, name: str, doc: str | None) -> None:
        """\
        Renderer init method

        Arguments
        ---------
        name
            Name of original output function. Ex: `my_txt`
        doc
            Documentation of the output function. Ex: `"My text output will be displayed
            verbatim".
        """
        self.__name__ = name
        self.__doc__ = doc

    def _set_metadata(self, session: Session, name: str) -> None:
        """\
        When `Renderer`s are assigned to Output object slots, this method is used to
        pass along Session and name information.
        """
        self._session: Session = session
        self._name: str = name


class RendererRun(Renderer[OT]):
    """
    Convenience class to define a `_run` method

    This class is used to define a `_run` method that is called by the `.__call__`
    method in subclasses.

    Properties
    ----------
    _is_async
        If `TRUE`, the app-supplied render function is asynchronous. Must be implemented
        in subclasses.
    meta
        A named dictionary of values: `is_async`, `session` (the :class:`~shiny.Session`
        object), and `name` (the name of the output being rendered)

    See Also
    --------
    * :class:`~shiny.render.Renderer`
    * :class:`~shiny.render.RendererSync`
    * :class:`~shiny.render.RendererAsync`
    """

    @property
    def _is_async(self) -> bool:
        raise NotImplementedError()

    @property
    def meta(self) -> RenderMeta:
        return RenderMeta(
            is_async=self._is_async,
            session=self._session,
            name=self._name,
        )

    def __init__(
        self,
        render_fn: RenderFn[IT],
        handler_fn: HandlerFn[IT, P, OT],
        params: RendererParams[P],
    ) -> None:
        if not _utils.is_async_callable(handler_fn):
            raise TypeError(
                self.__class__.__name__ + " requires an async handler function"
            )
        super().__init__(
            name=render_fn.__name__,
            doc=render_fn.__doc__,
        )

        # Given we use `_utils.run_coro_sync(self._run())` to call our method,
        # we can act as if `render_fn` and `handler_fn` are always async
        self._render_fn = _utils.wrap_async(render_fn)
        self._handler_fn = _utils.wrap_async(handler_fn)
        self._params = params

    async def _run(self) -> OT:
        """
        Executes the (async) handler function

        The handler function will receive the following arguments: `meta` of type :class:`~shiny.render.RenderMeta`, an app-defined render function of type :class:`~shiny.render.RenderFnAsync`, and `*args` and `**kwargs` of type `P`.

        Note: The app-defined render function will always be upgraded to be an async function.
        Note: `*args` will always be empty as it is an expansion of :class:`~shiny.render.RendererParams` which does not allow positional arguments.
        """
        ret = await self._handler_fn(
            # RendererMeta
            self.meta,
            # Callable[[], Awaitable[IT]]
            self._render_fn,
            # P
            *self._params.args,
            **self._params.kwargs,
        )
        return ret


# Using a second class to help clarify that it is of a particular type
class RendererSync(RendererRun[OT]):
    """
    Output Renderer (Synchronous)

    This class is used to define a synchronous renderer. The `.__call__` method is
    implemented to call the `._run` method synchronously.

    Properties
    ----------
    _is_async
        Returns `FALSE` as this is a synchronous renderer.

    See Also
    --------
    * :class:`~shiny.render.Renderer`
    * :class:`~shiny.render.RendererRun`
    * :class:`~shiny.render.RendererAsync`
    """

    @property
    def _is_async(self) -> bool:
        return False

    def __init__(
        self,
        render_fn: RenderFnSync[IT],
        handler_fn: HandlerFn[IT, P, OT],
        params: RendererParams[P],
    ) -> None:
        if _utils.is_async_callable(render_fn):
            raise TypeError(
                self.__class__.__name__ + " requires a synchronous render function"
            )
        # super == RendererRun
        super().__init__(
            render_fn,
            handler_fn,
            params,
        )

    def __call__(self, *_) -> OT:
        return _utils.run_coro_sync(self._run())


# The reason for having a separate RendererAsync class is because the __call__
# method is marked here as async; you can't have a single class where one method could
# be either sync or async.
class RendererAsync(RendererRun[OT]):
    @property
    def _is_async(self) -> bool:
        return True

    def __init__(
        self,
        render_fn: RenderFnAsync[IT],
        handler_fn: HandlerFn[IT, P, OT],
        params: RendererParams[P],
    ) -> None:
        if not _utils.is_async_callable(render_fn):
            raise TypeError(
                self.__class__.__name__ + " requires an asynchronous render function"
            )
        # super == RendererRun
        super().__init__(
            render_fn,
            handler_fn,
            params,
        )

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, *_
    ) -> OT:
        return await self._run()


# ======================================================================================
# Deprecated classes
# ======================================================================================


# A RenderFunction object is given a user-provided function which returns an IT. When
# the .__call___ method is invoked, it calls the user-provided function (which returns
# an IT), then converts the IT to an OT. Note that in many cases but not all, IT and OT
# will be the same.
class RenderFunction(Generic[IT, OT], Renderer[OT]):
    """
    Deprecated. Please use :func:`~shiny.render.renderer_components` instead.
    """

    def __init__(self, fn: Callable[[], IT]) -> None:
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__


# The reason for having a separate RenderFunctionAsync class is because the __call__
# method is marked here as async; you can't have a single class where one method could
# be either sync or async.
class RenderFunctionAsync(Generic[IT, OT], RendererAsync[OT]):
    """
    Deprecated. Please use :func:`~shiny.render.renderer_components` instead.
    """

    async def __call__(self) -> OT:  # pyright: ignore[reportIncompatibleMethodOverride]
        raise NotImplementedError


# ======================================================================================
# Restrict the value function
# ======================================================================================


# assert: No variable length positional values;
# * We need a way to distinguish between a plain function and args supplied to the next function. This is done by not allowing `*args`.
# assert: All kwargs of handler_fn should have a default value
# * This makes calling the method with both `()` and without `()` possible / consistent.
def _assert_handler_fn(handler_fn: HandlerFn[IT, P, OT]) -> None:
    params = inspect.Signature.from_callable(handler_fn).parameters

    if len(params) < 2:
        raise TypeError(
            "`handler_fn=` must have 2 positional parameters which have type `RenderMeta` and `RenderFnAsync` respectively"
        )

    for i, param in zip(range(len(params)), params.values()):
        # # Not a good test as `param.annotation` has type `str`:
        # if i == 0:
        #     assert param.annotation == "RenderMeta"
        # if i == 1:
        #     assert (param.annotation or "").startswith("RenderFnAsync")
        if i < 2 and not (
            param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            or param.kind == inspect.Parameter.POSITIONAL_ONLY
        ):
            raise TypeError(
                "`handler_fn=` must have 2 positional parameters which have type `RenderMeta` and `RenderFnAsync` respectively"
            )

        # Make sure there are no more than 2 positional args
        if i >= 2 and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            raise TypeError(
                "`handler_fn=` must not contain more than 2 positional parameters"
            )
        # Make sure there are no `*args`
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            raise TypeError(
                f"No variadic parameters (e.g. `*args`) can be supplied to `handler_fn=`. Received: `{param.name}`. Please only use `*`."
            )
        # Make sure kwargs have default values
        if (
            param.kind == inspect.Parameter.KEYWORD_ONLY
            and param.default is inspect.Parameter.empty
        ):
            raise TypeError(
                f"In `handler_fn=`, parameter `{param.name}` did not have a default value"
            )


# ======================================================================================
# Renderer decorator
# ======================================================================================


RendererDeco = Callable[[RenderFn[IT]], Renderer[OT]]
RenderImplFn = Callable[
    [
        Optional[RenderFn[IT]],
        RendererParams[P],
    ],
    # RendererSync[OT] | RendererAsync[OT] | RendererDeco[IT, OT],
    Renderer[OT] | RendererDeco[IT, OT],
]


class RendererComponents(Generic[IT, OT, P]):
    """
    Renderer Component class

    Properties
    ----------
    type_decorator
        The return type for the renderer decorator wrapper function. This should be used when the app-defined render function is `None` and extra parameters are being supplied.
    type_renderer_fn
        The (non-`None`) type for the renderer function's first argument that accepts an app-defined render function. This type should be paired with the return type: `type_renderer`.
    type_renderer
        The type for the return value of the renderer decorator function. This should be used when the app-defined render function is not `None`.
    type_impl_fn
        The type for the implementation function's first argument. This value handles both app-defined render functions and `None` and returns values appropriate for both cases. `type_impl_fn` should be paired with `type_impl`.
    type_impl
        The type for the return value of the implementation function. This value handles both app-defined render functions and `None` and returns values appropriate for both cases.

    See Also
    --------
    * :func:`~shiny.render.renderer_components`
    * :class:`~shiny.render.RendererParams`
    * :class:`~shiny.render.Renderer`
    """

    @property
    def type_decorator(self):
        return RendererDeco[IT, OT]

    @property
    def type_renderer_fn(self):
        return RenderFn[IT]

    @property
    def type_renderer(self):
        return Renderer[OT]

    @property
    def type_impl_fn(self):
        return Optional[RenderFn[IT]]

    @property
    def type_impl(self):
        return Renderer[OT] | RendererDeco[IT, OT]

    def params(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RendererParams[P]:
        return RendererParams(*args, **kwargs)

    def impl(
        self,
        render_fn: RenderFn[IT] | None,
        params: RendererParams[P] | None = None,
    ) -> Renderer[OT] | RendererDeco[IT, OT]:
        if params is None:
            params = self.params()
        if not isinstance(params, RendererParams):
            raise TypeError(
                f"Expected `params` to be of type `RendererParams` but received `{type(params)}`. Please use `.params()` to create a `RendererParams` object."
            )
        return self._fn(render_fn, params)

    def __init__(
        self,
        fn: RenderImplFn[IT, P, OT],
    ) -> None:
        self._fn = fn


def renderer_components(
    handler_fn: HandlerFn[IT, P, OT],
) -> RendererComponents[IT, OT, P]:
    """\
    Renderer components decorator

    TODO-barret; Docs go here!
    When defining overloads, if you use `**kwargs: object`, you may get a type error about incompatible signatures. To fix this, you can use `**kwargs: Any` instead or add `_fn: None = None` as a first parameter.
    """
    _assert_handler_fn(handler_fn)

    def renderer_decorator(
        render_fn: RenderFnSync[IT] | RenderFnAsync[IT] | None,
        params: RendererParams[P],
    ) -> Renderer[OT] | RendererDeco[IT, OT]:
        def as_render_fn(
            fn: RenderFnSync[IT] | RenderFnAsync[IT],
        ) -> Renderer[OT]:
            if _utils.is_async_callable(fn):
                return RendererAsync(fn, handler_fn, params)
            else:
                fn = cast(RenderFnSync[IT], fn)
                return RendererSync(fn, handler_fn, params)

        if render_fn is None:
            return as_render_fn
        val = as_render_fn(render_fn)
        return val

    ret = RendererComponents(renderer_decorator)
    # Copy over docs. Even if they do not show up in pylance
    # ret.__doc__ = handler_fn.__doc__
    return ret


# ======================================================================================
# RenderText
# ======================================================================================


@renderer_components
async def _text(
    meta: RenderMeta,
    fn: RenderFnAsync[str | None],
) -> str | None:
    value = await fn()
    if value is None:
        return None
    return str(value)


@overload
def text() -> _text.type_decorator:
    ...


@overload
def text(_fn: _text.type_renderer_fn) -> _text.type_renderer:
    ...


def text(
    _fn: _text.type_impl_fn = None,
) -> _text.type_impl:
    """
    Reactively render text.

    Returns
    -------
    :
        A decorator for a function that returns a string.

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_text` container (see :func:`~shiny.ui.output_text` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_text
    """
    return _text.impl(_fn)


# ======================================================================================
# RenderPlot
# ======================================================================================
# It would be nice to specify the return type of RenderPlotFunc to be something like:
#   Union[matplotlib.figure.Figure, PIL.Image.Image]
# However, if we did that, we'd have to import those modules at load time, which adds
# a nontrivial amount of overhead. So for now, we're just using `object`.
@renderer_components
async def _plot(
    meta: RenderMeta,
    fn: RenderFnAsync[ImgData | None],
    *,
    alt: Optional[str] = None,
    **kwargs: object,
) -> ImgData | None:
    is_userfn_async = meta["is_async"]
    name = meta["name"]
    session = meta["session"]

    ppi: float = 96

    inputs = session.root_scope().input

    # Reactively read some information about the plot.
    pixelratio: float = typing.cast(
        float, inputs[ResolvedId(".clientdata_pixelratio")]()
    )
    width: float = typing.cast(
        float, inputs[ResolvedId(f".clientdata_output_{name}_width")]()
    )
    height: float = typing.cast(
        float, inputs[ResolvedId(f".clientdata_output_{name}_height")]()
    )

    x = await fn()

    # Note that x might be None; it could be a matplotlib.pyplot

    # Try each type of renderer in turn. The reason we do it this way is to avoid
    # importing modules that aren't already loaded. That could slow things down, or
    # worse, cause an error if the module isn't installed.
    #
    # Each try_render function should indicate whether it was able to make sense of
    # the x value (or, in the case of matplotlib, possibly it decided to use the
    # global pyplot figure) by returning a tuple that starts with True. The second
    # tuple element may be None in this case, which means the try_render function
    # explicitly wants the plot to be blanked.
    #
    # If a try_render function returns a tuple that starts with False, then the next
    # try_render function should be tried. If none succeed, an error is raised.
    ok: bool
    result: ImgData | None

    if "plotnine" in sys.modules:
        ok, result = try_render_plotnine(
            x,
            width,
            height,
            pixelratio,
            ppi,
            alt,
            **kwargs,
        )
        if ok:
            return result

    if "matplotlib" in sys.modules:
        ok, result = try_render_matplotlib(
            x,
            width,
            height,
            pixelratio=pixelratio,
            ppi=ppi,
            allow_global=not is_userfn_async,
            alt=alt,
            **kwargs,
        )
        if ok:
            return result

    if "PIL" in sys.modules:
        ok, result = try_render_pil(
            x,
            width,
            height,
            pixelratio,
            ppi,
            alt,
            **kwargs,
        )
        if ok:
            return result

    # This check must happen last because
    # matplotlib might be able to plot even if x is `None`
    if x is None:
        return None

    raise Exception(
        f"@render.plot doesn't know to render objects of type '{str(type(x))}'. "
        + "Consider either requesting support for this type of plot object, and/or "
        + " explictly saving the object to a (png) file and using @render.image."
    )


@overload
def plot(
    *,
    alt: Optional[str] = None,
    **kwargs: Any,
) -> _plot.type_decorator:
    ...


@overload
def plot(_fn: _plot.type_renderer_fn) -> _plot.type_renderer:
    ...


def plot(
    _fn: _plot.type_impl_fn = None,
    *,
    alt: Optional[str] = None,
    **kwargs: Any,
) -> _plot.type_impl:
    """
    Reactively render a plot object as an HTML image.

    Parameters
    ----------
    alt
        Alternative text for the image if it cannot be displayed or viewed (i.e., the
        user uses a screen reader).
    **kwargs
        Additional keyword arguments passed to the relevant method for saving the image
        (e.g., for matplotlib, arguments to ``savefig()``; for PIL and plotnine,
        arguments to ``save()``).

    Returns
    -------
    :
        A decorator for a function that returns any of the following:

        1. A :class:`matplotlib.figure.Figure` instance.
        2. An :class:`matplotlib.artist.Artist` instance.
        3. A list/tuple of Figure/Artist instances.
        4. An object with a 'figure' attribute pointing to a
           :class:`matplotlib.figure.Figure` instance.
        5. A :class:`PIL.Image.Image` instance.

    It's also possible to use the ``matplotlib.pyplot`` interface; in that case, your
    function should just call pyplot functions and not return anything. (Note that if
    the decorated function is async, then it's not safe to use pyplot. Shiny will detect
    this case and throw an error asking you to use matplotlib's object-oriented
    interface instead.)

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of a
    :func:`~shiny.ui.output_plot` container (see :func:`~shiny.ui.output_plot` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_plot
    ~shiny.render.image
    """
    return _plot.impl(_fn, _plot.params(alt=alt, **kwargs))


# ======================================================================================
# RenderImage
# ======================================================================================
@renderer_components
async def _image(
    meta: RenderMeta,
    fn: RenderFnAsync[ImgData | None],
    *,
    delete_file: bool = False,
) -> ImgData | None:
    res = await fn()
    if res is None:
        return None

    src: str = res.get("src")
    try:
        with open(src, "rb") as f:
            data = base64.b64encode(f.read())
            data_str = data.decode("utf-8")
        content_type = _utils.guess_mime_type(src)
        res["src"] = f"data:{content_type};base64,{data_str}"
        return res
    finally:
        if delete_file:
            os.remove(src)


@overload
def image(
    *,
    delete_file: bool = False,
) -> _image.type_decorator:
    ...


@overload
def image(_fn: _image.type_renderer_fn) -> _image.type_renderer:
    ...


def image(
    _fn: _image.type_impl_fn = None,
    *,
    delete_file: bool = False,
) -> _image.type_impl:
    """
    Reactively render a image file as an HTML image.

    Parameters
    ----------
    delete_file
        If ``True``, the image file will be deleted after rendering.

    Returns
    -------
    :
        A decorator for a function that returns an `~shiny.types.ImgData` object.

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_image` container (see :func:`~shiny.ui.output_image` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_image
    ~shiny.types.ImgData
    ~shiny.render.plot
    """
    return _image.impl(_fn, _image.params(delete_file=delete_file))


# ======================================================================================
# RenderTable
# ======================================================================================


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> "pd.DataFrame":
        ...


TableResult = Union["pd.DataFrame", PandasCompatible, None]


@renderer_components
async def _table(
    meta: RenderMeta,
    fn: RenderFnAsync[TableResult | None],
    *,
    index: bool = False,
    classes: str = "table shiny-table w-auto",
    border: int = 0,
    **kwargs: object,
) -> RenderedDeps | None:
    x = await fn()

    if x is None:
        return None

    import pandas
    import pandas.io.formats.style

    html: str
    if isinstance(x, pandas.io.formats.style.Styler):
        html = cast(  # pyright: ignore[reportUnnecessaryCast]
            str,
            x.to_html(  # pyright: ignore[reportUnknownMemberType]
                **kwargs  # pyright: ignore[reportGeneralTypeIssues]
            ),
        )
    else:
        if not isinstance(x, pandas.DataFrame):
            if not isinstance(x, PandasCompatible):
                raise TypeError(
                    "@render.table doesn't know how to render objects of type "
                    f"'{str(type(x))}'. Return either a pandas.DataFrame, or an object "
                    "that has a .to_pandas() method."
                )
            x = x.to_pandas()

        html = cast(  # pyright: ignore[reportUnnecessaryCast]
            str,
            x.to_html(  # pyright: ignore[reportUnknownMemberType]
                index=index,
                classes=classes,
                border=border,
                **kwargs,  # pyright: ignore[reportGeneralTypeIssues]
            ),
        )
    return {"deps": [], "html": html}


@overload
def table(
    *,
    index: bool = False,
    classes: str = "table shiny-table w-auto",
    border: int = 0,
    **kwargs: Any,
) -> _table.type_decorator:
    ...


@overload
def table(_fn: _table.type_renderer_fn) -> _table.type_renderer:
    ...


def table(
    _fn: _table.type_impl_fn = None,
    *,
    index: bool = False,
    classes: str = "table shiny-table w-auto",
    border: int = 0,
    **kwargs: object,
) -> _table.type_impl:
    """
    Reactively render a Pandas data frame object (or similar) as a basic HTML table.

    Parameters
    ----------
    index
        Whether to print index (row) labels. (Ignored for pandas :class:`Styler`
        objects; call ``style.hide(axis="index")`` from user code instead.)
    classes
        CSS classes (space separated) to apply to the resulting table. By default, we
        use `table shiny-table w-auto` which is designed to look reasonable with Bootstrap 5.
        (Ignored for pandas :class:`Styler` objects; call
        ``style.set_table_attributes('class="dataframe table shiny-table w-auto"')``
        from user code instead.)
    **kwargs
        Additional keyword arguments passed to ``pandas.DataFrame.to_html()`` or
        ``pandas.io.formats.style.Styler.to_html()``.

    Returns
    -------
    :
        A decorator for a function that returns any of the following:

        1. A pandas :class:`DataFrame` object.
        2. A pandas :class:`Styler` object.
        3. Any object that has a `.to_pandas()` method (e.g., a Polars data frame or
           Arrow table).

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_table` container (see :func:`~shiny.ui.output_table` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_table
    """
    return _table.impl(
        _fn,
        _table.params(
            index=index,
            classes=classes,
            border=border,
            **kwargs,
        ),
    )


# ======================================================================================
# RenderUI
# ======================================================================================
@renderer_components
async def _ui(
    meta: RenderMeta,
    fn: RenderFnAsync[TagChild],
) -> RenderedDeps | None:
    ui = await fn()
    if ui is None:
        return None

    return meta["session"]._process_ui(ui)


@overload
def ui() -> _ui.type_decorator:
    ...


@overload
def ui(_fn: _ui.type_renderer_fn) -> _ui.type_renderer:
    ...


def ui(
    _fn: _ui.type_impl_fn = None,
) -> _ui.type_impl:
    """
    Reactively render HTML content.

    Returns
    -------
    :
        A decorator for a function that returns an object of type `~shiny.ui.TagChild`.

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_ui` container (see :func:`~shiny.ui.output_ui` for example
    usage).

    See Also
    --------
    ~shiny.ui.output_ui
    """
    return _ui.impl(_fn)
