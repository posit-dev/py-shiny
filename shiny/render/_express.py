from __future__ import annotations

import sys
from typing import Optional

from htmltools import Tag, TagAttrValue, TagFunction, TagList, wrap_displayhook_handler

from .. import ui as _ui
from .._docstring import add_example
from .._typing_extensions import Self
from ..session._utils import require_active_session
from ..types import MISSING, MISSING_TYPE, JsonifiableDict
from .renderer import AsyncValueFn, Renderer, ValueFn
from .renderer._utils import rendered_deps_to_jsonifiable, set_kwargs_value


@add_example(ex_dir="../api-examples/render_express")
class express(Renderer[None]):
    """
    Reactively render HTML content with output captured as in Shiny Express

    This is similar to :class:`~shiny.render.ui`, except that :class:`~shiny.render.ui`
    uses the return value from the the decorated function, whereas this function works
    like Shiny Express: as it executes each line of the decorated function, it calls
    :func:`~sys.displayhook()` on the result. This has the effect of "capturing" the
    output of each line.

    This decorator can be thought of as a combination of :class:`~shiny.render.ui` (for
    rendering and sending the dynamic UI to the client), and `~shiny.express.expressify`
    (for capturing the output of each line).

    Returns
    -------
    :
        A decorator for a function that returns `None`.

    See Also
    --------
    * ~shiny.render.ui
    * ~shiny.ui.output_ui
    * ~shiny.express.expressify
    * ~shiny.express.ui.hold
    """

    def auto_output_ui(
        self,
        *,
        inline: bool | MISSING_TYPE = MISSING,
        container: TagFunction | MISSING_TYPE = MISSING,
        fill: bool | MISSING_TYPE = MISSING,
        fillable: bool | MISSING_TYPE = MISSING,
        **kwargs: TagAttrValue,
    ) -> Tag:
        # Only set the arg if it is available. (Prevents duplicating default values)
        set_kwargs_value(kwargs, "inline", inline, self.inline)
        set_kwargs_value(kwargs, "container", container, self.container)
        set_kwargs_value(kwargs, "fill", fill, self.fill)
        set_kwargs_value(kwargs, "fillable", fillable, self.fillable)

        return _ui.output_ui(
            self.output_id,
            # (possibly) contains `inline`, `container`, `fill`, and `fillable` keys!
            **kwargs,  # pyright: ignore[reportArgumentType]
        )

    def __call__(self, fn: ValueFn[None]) -> Self:
        if fn is None:  # pyright: ignore[reportUnnecessaryComparison]
            raise TypeError("@render.express requires a function when called")

        async_fn = AsyncValueFn(fn)
        if async_fn.is_async():
            raise TypeError(
                "@render.express does not support async functions. Use @render.ui instead."
            )

        from ..express.expressify_decorator._expressify import expressify_unwrap_inplace

        fn = expressify_unwrap_inplace()(fn)

        # Call the superclass method with upgraded `fn` value
        super().__call__(fn)

        return self

    def __init__(
        self,
        _fn: Optional[ValueFn[None]] = None,
        *,
        inline: bool = False,
        container: Optional[TagFunction] = None,
        fill: bool = False,
        fillable: bool = False,
        **kwargs: TagAttrValue,
    ):
        super().__init__(_fn)
        self.inline: bool = inline
        self.container: Optional[TagFunction] = container
        self.fill: bool = fill
        self.fillable: bool = fillable
        self.kwargs: dict[str, TagAttrValue] = kwargs

    async def render(self) -> JsonifiableDict | None:
        results: list[object] = []
        orig_displayhook = sys.displayhook
        sys.displayhook = wrap_displayhook_handler(results.append)

        if self.fn.is_async():
            raise TypeError(
                "@render.express does not support async functions. Use @render.ui instead."
            )

        try:
            # Run synchronously
            sync_value_fn = self.fn.get_sync_fn()
            ret = sync_value_fn()
            if ret is not None:
                raise RuntimeError(
                    "@render.express functions should not return values. "
                    "Instead, @render.express dynamically renders every printable line "
                    "within the function body. (`None` is a valid return value.)"
                )
        finally:
            sys.displayhook = orig_displayhook
        if len(results) == 0:
            return None

        session = require_active_session(None)
        return rendered_deps_to_jsonifiable(
            session._process_ui(
                TagList(*results)  # pyright: ignore[reportArgumentType]
            )
        )
