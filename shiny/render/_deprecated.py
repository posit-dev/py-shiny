from __future__ import annotations

from typing import Generic

from .._deprecated import ShinyDeprecationWarning
from .transformer._transformer import IT, OT, ValueFnAsync, ValueFnSync

# ======================================================================================
# Deprecated classes
# ======================================================================================


# A RenderFunction object is given a app-supplied function which returns an `IT`. When
# the .__call__ method is invoked, it calls the app-supplied function (which returns an
# `IT`), then converts the `IT` to an `OT`. Note that in many cases but not all, `IT`
# and `OT` will be the same.
class RenderFunction(Generic[IT, OT]):
    """
    Deprecated. Please use :class:`~shiny.render.renderer.Renderer` class instead.
    """

    def __init__(self, fn: ValueFnSync[IT]) -> None:
        raise ShinyDeprecationWarning(
            "Class `"
            + str(self.__class__.__name__)
            + "` inherits from the deprecated class `shiny.render.RenderFunction`. "
            "Please update your renderer to use `shiny.render.renderer.Renderer` instead."
        )


# The reason for having a separate RenderFunctionAsync class is because the __call__
# method is marked here as async; you can't have a single class where one method could
# be either sync or async.
class RenderFunctionAsync(Generic[IT, OT]):
    """
    Deprecated. Please use :class:`~shiny.render.renderer.Renderer` class instead.
    """

    def __init__(self, fn: ValueFnAsync[IT]) -> None:
        raise ShinyDeprecationWarning(
            "Class `"
            + str(self.__class__.__name__)
            + "` inherits from the deprecated class `shiny.render.RenderFunctionAsync`. "
            "Please update your renderer to use `shiny.render.renderer.Renderer` instead."
        )
