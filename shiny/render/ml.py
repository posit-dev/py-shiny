from __future__ import annotations

__all__ = ("classification_label",)


import typing
from typing import Awaitable, Callable, Optional, overload

from .. import _utils
from . import RenderFunction, RenderFunctionAsync

# ======================================================================================
# RenderClassificationLabel
# ======================================================================================

ClassificationData = dict[str, float]


RenderClassificationLabelFunc = Callable[[], "ClassificationData | None"]
RenderClassificationLabelFuncAsync = Callable[
    [], Awaitable["ClassificationData | None"]
]


class RenderClassificationLabel(
    RenderFunction["ClassificationData | None", "ClassificationData | None"]
):
    def __init__(self, fn: RenderClassificationLabelFunc) -> None:
        super().__init__(fn)
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderClassificationLabelFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> ClassificationData | None:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> ClassificationData | None:
        res = await self._fn()
        if res is None:
            return None
        return res


class RenderClassificationLabelAsync(
    RenderClassificationLabel, RenderFunctionAsync["str | None", "str | None"]
):
    def __init__(self, fn: RenderClassificationLabelFuncAsync) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderClassificationLabelFunc, fn))

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> ClassificationData | None:
        return await self._run()


@overload
def classification_label(
    fn: RenderClassificationLabelFunc | RenderClassificationLabelFuncAsync,
) -> RenderClassificationLabel:
    ...


@overload
def classification_label() -> (
    Callable[
        [RenderClassificationLabelFunc | RenderClassificationLabelFuncAsync],
        RenderClassificationLabel,
    ]
):
    ...


def classification_label(
    fn: Optional[
        RenderClassificationLabelFunc | RenderClassificationLabelFuncAsync
    ] = None,
) -> (
    RenderClassificationLabel
    | Callable[
        [RenderClassificationLabelFunc | RenderClassificationLabelFuncAsync],
        RenderClassificationLabel,
    ]
):
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

    def wrapper(
        fn: RenderClassificationLabelFunc | RenderClassificationLabelFuncAsync,
    ) -> RenderClassificationLabel:
        if _utils.is_async_callable(fn):
            return RenderClassificationLabelAsync(fn)
        else:
            fn = typing.cast(RenderClassificationLabelFunc, fn)
            return RenderClassificationLabel(fn)

    if fn is None:
        return wrapper
    else:
        return wrapper(fn)
