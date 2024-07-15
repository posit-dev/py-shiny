from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, overload

from htmltools import HTML, MetadataNode, Tagifiable, TagNode

from ..._typing_extensions import TypeGuard
from ...types import Jsonifiable
from ._types import CellHtml, ReprHtml, SeriesLike

if TYPE_CHECKING:
    from ...session import Session


def as_cell_html(x: TagNode, *, session: Session) -> CellHtml:
    return {"isShinyHtml": True, "obj": session._process_ui(x)}


# def is_cell_html(val: Any) -> TypeGuard[CellHtml]:
#     return isinstance(val, dict) and (
#         val.get("isShinyHtml", False)  # pyright: ignore[reportUnknownMemberType]
#         is True
#     )


@overload
def maybe_as_cell_html(  # pyright: ignore[reportOverlappingOverload]
    x: TagNode, *, session: Session
) -> CellHtml: ...
@overload
def maybe_as_cell_html(  # pyright: ignore[reportOverlappingOverload]
    x: TagNode, *, session: Session
) -> CellHtml: ...
@overload
def maybe_as_cell_html(x: Jsonifiable, *, session: Session) -> Jsonifiable: ...
def maybe_as_cell_html(
    x: Jsonifiable | TagNode, *, session: Session
) -> Jsonifiable | CellHtml:
    if is_shiny_html(x):
        return as_cell_html(x, session=session)
    return cast(Jsonifiable, x)


def col_contains_shiny_html(col: SeriesLike) -> bool:
    return any(is_shiny_html(val) for _, val in enumerate(col))


# TODO-barret-test; Add test to assert the union type of `TagNode` contains `str` and (HTML | Tagifiable | MetadataNode | ReprHtml). Until a `is tag renderable` method is available in htmltools, we need to check for these types manually and must stay in sync with the `TagNode` union type.
# TODO-barret-future; Use `TypeIs[HTML | Tagifiable | MetadataNode | ReprHtml]` when it is available from typing_extensions
def is_shiny_html(val: Any) -> TypeGuard[HTML | Tagifiable | MetadataNode | ReprHtml]:
    return isinstance(val, (HTML, Tagifiable, MetadataNode, ReprHtml))
