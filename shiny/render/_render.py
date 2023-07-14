# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

__all__ = (
    # "renderer_gen",
    # "RendererMeta",
    # "RenderFunction",
    # "RenderFunctionSync",
    # "RenderFunctionAsync",
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

# import random
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Concatenate,
    Generic,
    Optional,
    ParamSpec,
    Protocol,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
    runtime_checkable,
)

# # These aren't used directly in this file, but they seem necessary for Sphinx to work
# # cleanly.
# from htmltools import Tag  # pyright: ignore[reportUnusedImport] # noqa: F401
# from htmltools import Tagifiable  # pyright: ignore[reportUnusedImport] # noqa: F401
# from htmltools import TagList  # pyright: ignore[reportUnusedImport] # noqa: F401
from htmltools import TagChild

if TYPE_CHECKING:
    from ..session import Session
    from ..session._utils import RenderedDeps
    import pandas as pd

from .. import _utils
from .._namespaces import ResolvedId
from .._typing_extensions import TypedDict
from ..types import ImgData
from ._try_render_plot import try_render_matplotlib, try_render_pil, try_render_plotnine

# Input type for the user-spplied function that is passed to a render.xx
IT = TypeVar("IT")
# Output type after the RenderFunction.__call__ method is called on the IT object.
OT = TypeVar("OT")
# Param specification for value function
P = ParamSpec("P")
# Generic type var
T = TypeVar("T")


# Meta informatoin to give `value_fn()` some context
class RendererMeta(TypedDict):
    is_async: bool
    session: Session
    name: str


# ======================================================================================
# RenderFunction / RenderFunctionSync / RenderFunctionAsync base class
# ======================================================================================


# A RenderFunction object is given a user-provided function (`value_fn`) which returns
# an `IT`. When the .__call___ method is invoked, it calls the user-provided function
# (which returns an `IT`), then converts the `IT` to an `OT`. Note that in many cases
# but not all, `IT` and `OT` will be the same.
class RenderFunction(Generic[IT, OT]):
    @property
    def is_async(self) -> bool:
        raise NotImplementedError()

    def __init__(self, render_fn: UserFunc[IT]) -> None:
        self.__name__ = render_fn.__name__  # TODO-barret; Set name of async function
        self.__doc__ = render_fn.__doc__

        # Given we use `_utils.run_coro_sync(self._run())` to call our method,
        # we can act as if `render_fn` is always async
        self._fn = _utils.wrap_async(render_fn)

    def __call__(self) -> OT:
        raise NotImplementedError

    def _set_metadata(self, session: Session, name: str) -> None:
        """When RenderFunctions are assigned to Output object slots, this method
        is used to pass along session and name information.
        """
        self._session: Session = session
        self._name: str = name

    @property
    def meta(self) -> RendererMeta:
        return RendererMeta(
            is_async=self.is_async,
            session=self._session,
            name=self._name,
        )


# Using a second class to help clarify that it is of a particular type
class RenderFunctionSync(Generic[IT, OT, P], RenderFunction[IT, OT]):
    @property
    def is_async(self) -> bool:
        return False

    def __init__(
        self,
        # Use single arg to minimize overlap with P.kwargs
        _render_args: _RenderArgsSync[IT, P, OT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        # `*args` must be in the `__init__` signature
        # Make sure there no `args`!
        _assert_no_args(args)

        # Unpack args
        _fn, _value_fn = _render_args
        super().__init__(_fn)

        self._value_fn = _utils.wrap_async(_value_fn)
        self._args = args
        self._kwargs = kwargs

    def __call__(self) -> OT:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> OT:
        fn_val = await self._fn()
        ret = await self._value_fn(
            # RendererMeta
            self.meta,
            # IT
            fn_val,
            # P
            *self._args,
            **self._kwargs,
        )
        return ret


# The reason for having a separate RenderFunctionAsync class is because the __call__
# method is marked here as async; you can't have a single class where one method could
# be either sync or async.
class RenderFunctionAsync(Generic[IT, OT, P], RenderFunction[IT, OT]):
    @property
    def is_async(self) -> bool:
        return True

    def __init__(
        self,
        # Use single arg to minimize overlap with P.kwargs
        _render_args: _RenderArgsAsync[IT, P, OT],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        # `*args` must be in the `__init__` signature
        # Make sure there no `args`!
        _assert_no_args(args)

        # Unpack args
        _fn, _value_fn = _render_args

        if not _utils.is_async_callable(_fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        # super == RenderFunctionAsync, RenderFunction
        super().__init__(_fn)

        self._fn = _fn
        self._value_fn = _utils.wrap_async(_value_fn)
        self._args = args
        self._kwargs = kwargs

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> OT:
        return await self._run()

    async def _run(self) -> OT:
        fn_val = await self._fn()
        ret = await self._value_fn(
            # RendererMeta
            self.meta,
            # IT
            fn_val,
            # P
            *self._args,
            **self._kwargs,
        )
        return ret


# ======================================================================================
# Type definitions
# ======================================================================================

UserFuncSync = Callable[[], IT]
UserFuncAsync = Callable[[], Awaitable[IT]]
UserFunc = UserFuncSync[IT] | UserFuncAsync[IT]
ValueFunc = (
    Callable[Concatenate[RendererMeta, IT, P], OT]
    | Callable[Concatenate[RendererMeta, IT, P], Awaitable[OT]]
)
RenderDecoSync = Callable[[UserFuncSync[IT]], RenderFunctionSync[IT, OT, P]]
RenderDecoAsync = Callable[[UserFuncAsync[IT]], RenderFunctionAsync[IT, OT, P]]
RenderDeco = Callable[
    [UserFuncSync[IT] | UserFuncAsync[IT]],
    RenderFunctionSync[IT, OT, P] | RenderFunctionAsync[IT, OT, P],
]


_RenderArgsSync = Tuple[UserFuncSync[IT], ValueFunc[IT, P, OT]]
_RenderArgsAsync = Tuple[UserFuncAsync[IT], ValueFunc[IT, P, OT]]


# ======================================================================================
# Restrict the value function
# ======================================================================================


def _assert_no_args(args: tuple[object]) -> None:
    if len(args) > 0:
        raise RuntimeError("`args` should not be supplied")


# assert: No variable length positional values;
# * We need a way to distinguish between a plain function and args supplied to the next function. This is done by not allowing `*args`.
# assert: All kwargs of value_fn should have a default value
# * This makes calling the method with both `()` and without `()` possible / consistent.
def _assert_value_fn(value_fn: ValueFunc[IT, P, OT]) -> None:
    params = inspect.Signature.from_callable(value_fn).parameters

    for i, param in zip(range(len(params)), params.values()):
        # # Not a good test as `param.annotation` has type `str`:
        # if i == 0:
        #   print(type(param.annotation))
        #   assert isinstance(param.annotation, RendererMeta)

        # Make sure there are no more than 2 positional args
        if i >= 2 and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            raise TypeError(
                "`value_fn=` must not contain more than 2 positional parameters"
            )
        # Make sure there are no `*args`
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            raise TypeError(
                f"No variadic parameters (e.g. `*args`) can be supplied to `value_fn=`. Received: `{param.name}`"
            )
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            # Do not allow for a kwarg to be named `_render_fn`
            if param.name == "_render_fn":
                raise ValueError(
                    "In `value_fn=`, parameters can not be named `_render_fn`"
                )
            # Make sure kwargs have default values
            if param.default is inspect.Parameter.empty:
                raise TypeError(
                    f"In `value_fn=`, parameter `{param.name}` did not have a default value"
                )


def renderer_gen(
    value_fn: ValueFunc[IT, P, OT],
):
    """\
    Renderer generator

    TODO-barret; Docs go here!
    """
    _assert_value_fn(value_fn)

    @overload
    # RenderDecoSync[IT, OT, P]
    def renderer_decorator(
        _render_fn: UserFuncSync[IT],
    ) -> RenderFunctionSync[IT, OT, P]:
        ...

    @overload
    # RenderDecoAsync[IT, OT, P]
    def renderer_decorator(
        _render_fn: UserFuncAsync[IT],
    ) -> RenderFunctionAsync[IT, OT, P]:
        ...

    @overload
    def renderer_decorator(*args: P.args, **kwargs: P.kwargs) -> RenderDeco[IT, OT, P]:
        ...

    # # If we use `wraps()`, the overloads are lost.
    # @functools.wraps(value_fn)

    # Ignoring the type issue on the next line of code as the overloads for
    # `renderer_deco` are not consistent with the function definition.
    # Motivation:
    # * https://peps.python.org/pep-0612/ does allow for prepending an arg
    #   (`_render_fn`).
    # * However, the overload is not happy when both a positional arg (`_render_fn`) is
    #   dropped and the variadic args (`*args`) are kept.
    # * The variadic args CAN NOT be dropped as PEP612 states that both components of
    #   the `ParamSpec` must be used in the same function signature.
    # * By making assertions on `P.args` to only allow for `*`, we _can_ make overloads
    #   that use either the single positional arg (`_render_fn`) or
    #   the `P.kwargs` (as `P.args` == `*`)
    def renderer_decorator(  # type: ignore[reportGeneralTypeIssues]
        _render_fn: Optional[UserFuncSync[IT] | UserFuncAsync[IT]] = None,
        *args: P.args,  # Equivalent to `*` after assertions in `_assert_value_fn()`
        **kwargs: P.kwargs,
    ) -> (
        RenderDecoSync[IT, OT, P]
        | RenderDecoAsync[IT, OT, P]
        | RenderFunctionSync[IT, OT, P]
        | RenderFunctionAsync[IT, OT, P]
    ):
        # `args` **must** be in `renderer_decorator` definition.
        # Make sure there no `args`!
        _assert_no_args(args)

        def render_fn_sync(
            fn_sync: UserFuncSync[IT],
        ) -> RenderFunctionSync[IT, OT, P]:
            return RenderFunctionSync(
                (fn_sync, value_fn),
                *args,
                **kwargs,
            )

        def render_fn_async(
            fn_async: UserFuncAsync[IT],
        ) -> RenderFunctionAsync[IT, OT, P]:
            return RenderFunctionAsync(
                (fn_async, value_fn),
                *args,
                **kwargs,
            )

        @overload
        def as_render_fn(
            fn: UserFuncSync[IT],
        ) -> RenderFunctionSync[IT, OT, P]:
            ...

        @overload
        def as_render_fn(
            fn: UserFuncAsync[IT],
        ) -> RenderFunctionAsync[IT, OT, P]:
            ...

        def as_render_fn(
            fn: UserFuncSync[IT] | UserFuncAsync[IT],
        ) -> RenderFunctionSync[IT, OT, P] | RenderFunctionAsync[IT, OT, P]:
            if _utils.is_async_callable(fn):
                return render_fn_async(fn)
            else:
                # Is not not `UserFuncAsync[IT]`. Cast `wrapper_fn`
                fn = cast(UserFuncSync[IT], fn)
                return render_fn_sync(fn)

        if _render_fn is None:
            return as_render_fn
        return as_render_fn(_render_fn)

    # Copy over name an docs
    renderer_decorator.__doc__ = value_fn.__doc__
    renderer_decorator.__name__ = value_fn.__name__
    # # TODO-barret; Fix name of decorated function. Hovering over method name does not work
    # ren_func = getattr(renderer_decorator, "__func__", renderer_decorator)
    # ren_func.__name__ = value_fn.__name__

    return renderer_decorator


# ======================================================================================
# RenderText
# ======================================================================================
@renderer_gen
def text(
    meta: RendererMeta,
    value: str | None,
) -> str | None:
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
    if value is None:
        return None
    return str(value)


# ======================================================================================
# RenderPlot
# ======================================================================================
# It would be nice to specify the return type of RenderPlotFunc to be something like:
#   Union[matplotlib.figure.Figure, PIL.Image.Image]
# However, if we did that, we'd have to import those modules at load time, which adds
# a nontrivial amount of overhead. So for now, we're just using `object`.
@renderer_gen
def plot(
    meta: RendererMeta,
    x: ImgData | None,
    *,
    alt: Optional[str] = None,
    **kwargs: object,
) -> ImgData | None:
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
    is_userfn_async = meta["is_async"]
    name = meta["name"]
    session = meta["session"]

    ppi: float = 96

    # TODO-barret; Q: These variable calls are **after** `self._fn()`. Is this ok?
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

    # !! Normal position for `x = await self._fn()`

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


# ======================================================================================
# RenderImage
# ======================================================================================
@renderer_gen
def image(
    meta: RendererMeta,
    res: ImgData | None,
    *,
    delete_file: bool = False,
) -> ImgData | None:
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


# ======================================================================================
# RenderTable
# ======================================================================================


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> "pd.DataFrame":
        ...


TableResult = Union["pd.DataFrame", PandasCompatible, None]


@renderer_gen
def table(
    meta: RendererMeta,
    x: TableResult | None,
    *,
    index: bool = False,
    classes: str = "table shiny-table w-auto",
    border: int = 0,
    **kwargs: object,
) -> RenderedDeps | None:
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


# ======================================================================================
# RenderUI
# ======================================================================================
@renderer_gen
def ui(
    meta: RendererMeta,
    ui: TagChild,
) -> RenderedDeps | None:
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
    if ui is None:
        return None

    return meta["session"]._process_ui(ui)
