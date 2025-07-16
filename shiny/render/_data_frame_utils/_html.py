from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast, overload

from htmltools import TagNode

from ..._typing_extensions import TypeIs
from ...types import Jsonifiable
from ._types import CellHtml, Series

if TYPE_CHECKING:
    from ...session import Session
    from ...session._utils import RenderedDeps


def as_cell_html(processed_ui: RenderedDeps) -> CellHtml:
    return {"isShinyHtml": True, "obj": processed_ui}


@overload
def maybe_as_cell_html(  # pyright: ignore[reportOverlappingOverload]
    x: str, *, session: Session
) -> Jsonifiable: ...
@overload
def maybe_as_cell_html(  # pyright: ignore[reportOverlappingOverload]
    x: TagNode, *, session: Session
) -> CellHtml: ...
@overload
def maybe_as_cell_html(x: Jsonifiable, *, session: Session) -> Jsonifiable: ...
def maybe_as_cell_html(
    x: Jsonifiable | TagNode, *, session: Session
) -> Jsonifiable | CellHtml:
    if ui_must_be_processed(x):
        return as_cell_html(session._process_ui(x))
    return cast(Jsonifiable, x)


def series_contains_htmltoolslike(ser: Series) -> bool:

    for idx, val in enumerate(ser):
        # Only check the first 1k elements in the series
        # This could lead to false negatives, but it's a reasonable tradeoff of speed.
        # If the user has _that_ much missing data and wants HTML support,
        #   they can preprocess their data to turn `None` values into `htmltools.HTML("")`
        if idx > 1000:
            return False

        if val is None:
            continue

        # Q: Can we short circuit this any quicker?
        # A: Not really. We need to check every element in the series
        #    as the typical dtype is greedy does not enforce a single type.
        # Reprex:
        # pl.Series([{"y": 2}, {"x": 1}, None, HTML("<p>Hello</p>")]).dtype
        # #> Struct({'y': Int64})
        if ui_must_be_processed(val):
            return True
    return False


@overload
def ui_must_be_processed(  # pyright: ignore[reportOverlappingOverload]
    val: str,
) -> Literal[False]: ...
@overload
def ui_must_be_processed(
    val: TagNode | object,
) -> TypeIs[TagNode]: ...
def ui_must_be_processed(  # pyright: ignore[reportInconsistentOverload]
    val: object,
):
    from htmltools import is_tag_node

    if isinstance(val, str):
        return False

    return is_tag_node(val)
