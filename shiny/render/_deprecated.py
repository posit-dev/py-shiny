from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic

from .transformer._transformer import (
    IT,
    OT,
    OutputRendererAsync,
    OutputRendererSync,
    TransformerMetadata,
    ValueFn,
    ValueFnAsync,
    ValueFnSync,
    empty_params,
)

# ======================================================================================
# Deprecated classes
# ======================================================================================


# A RenderFunction object is given a app-supplied function which returns an `IT`. When
# the .__call__ method is invoked, it calls the app-supplied function (which returns an
# `IT`), then converts the `IT` to an `OT`. Note that in many cases but not all, `IT`
# and `OT` will be the same.
class RenderFunction(Generic[IT, OT], OutputRendererSync[OT], ABC):
    """
    Deprecated. Please use :func:`~shiny.render.renderer_components` instead.
    """

    @abstractmethod
    def __call__(self) -> OT:
        ...

    @abstractmethod
    async def run(self) -> OT:
        ...

    def __init__(self, fn: ValueFnSync[IT]) -> None:
        async def transformer(_meta: TransformerMetadata, _fn: ValueFn[IT]) -> OT:
            ret = await self.run()
            return ret

        super().__init__(
            value_fn=fn,
            transform_fn=transformer,
            params=empty_params(),
        )
        self._fn = fn


# The reason for having a separate RenderFunctionAsync class is because the __call__
# method is marked here as async; you can't have a single class where one method could
# be either sync or async.
class RenderFunctionAsync(Generic[IT, OT], OutputRendererAsync[OT], ABC):
    """
    Deprecated. Please use :func:`~shiny.render.renderer_components` instead.
    """

    @abstractmethod
    async def __call__(self) -> OT:  # pyright: ignore[reportIncompatibleMethodOverride]
        ...

    @abstractmethod
    async def run(self) -> OT:
        ...

    def __init__(self, fn: ValueFnAsync[IT]) -> None:
        async def transformer(_meta: TransformerMetadata, _fn: ValueFn[IT]) -> OT:
            ret = await self.run()
            return ret

        super().__init__(
            value_fn=fn,
            transform_fn=transformer,
            params=empty_params(),
        )
        self._fn = fn
