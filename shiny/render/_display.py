from __future__ import annotations

import sys
from typing import Optional

from htmltools import Tag, TagAttrValue, TagFunction, TagList, wrap_displayhook_handler

from .. import ui as _ui
from .._typing_extensions import Self
from ..session._utils import require_active_session
from ..types import MISSING, MISSING_TYPE
from .renderer import AsyncValueFn, Renderer, ValueFn
from .renderer._utils import (
    JsonifiableDict,
    rendered_deps_to_jsonifiable,
    set_kwargs_value,
)


class display(Renderer[None]):
    def default_ui(
        self,
        id: str,
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
            id,
            # (possibly) contains `inline`, `container`, `fill`, and `fillable` keys!
            **kwargs,  # pyright: ignore[reportGeneralTypeIssues]
        )

    def __call__(self, fn: ValueFn[None]) -> Self:
        if fn is None:
            raise TypeError("@render.display requires a function when called")

        async_fn = AsyncValueFn(fn)
        if async_fn.is_async():
            raise TypeError(
                "@render.display does not support async functions. Use @render.ui instead."
            )

        from shiny.express.display_decorator._display_body import (
            display_body_unwrap_inplace,
        )

        fn = display_body_unwrap_inplace()(fn)

        # Call the superclass method with upgraded `fn` value
        super().__call__(fn)

        return self

    def __init__(
        self,
        _fn: ValueFn[None] = None,
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

        if self.value_fn.is_async():
            raise TypeError(
                "@render.display does not support async functions. Use @render.ui instead."
            )

        try:
            # Run synchronously
            sync_value_fn = self.value_fn.get_sync_fn()
            ret = sync_value_fn()
            if ret is not None:
                raise RuntimeError(
                    "@render.display functions should not return values. (`None` is allowed)."
                )
        finally:
            sys.displayhook = orig_displayhook
        if len(results) == 0:
            return None

        session = require_active_session(None)
        return rendered_deps_to_jsonifiable(
            session._process_ui(
                TagList(*results)  # pyright: ignore[reportGeneralTypeIssues]
            )
        )
