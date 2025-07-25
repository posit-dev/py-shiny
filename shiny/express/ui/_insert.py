"""
Shims for `ui.insert_*()`, `ui.update_*()`, etc. functions that lead to a more ergonomic
Express API.
These functions tend to have one issue in common: if they were re-exported verbatim from
Core to Express, they would want to take RecallContextManager(s) as input, which leads
to a somewhat awkward API. That's because, you'd have to know to use something like
@ui.hold() pass the UI as a value without displaying it.
"""

from typing import Literal, Optional

from htmltools import TagChild

from ..._docstring import add_example
from ...session import Session


@add_example()
def insert_nav_panel(
    id: str,
    title: str,
    *args: TagChild,
    value: Optional[str] = None,
    icon: TagChild = None,
    target: Optional[str] = None,
    position: Literal["after", "before"] = "after",
    select: bool = False,
    session: Optional[Session] = None,
) -> None:
    """
    Create a nav item pointing to some internal content.

    Parameters
    ----------
    id
        The id of the navset container to insert the item into.
    title
        A title to display. Can be a character string or UI elements (i.e., tags).
    *args
        UI elements to display when the item is active.
    value
        The value of the item. Use this value to determine whether the item is active
        (when an `id` is provided to the nav container) or to programmatically
        select the item (e.g., :func:`~shiny.ui.update_navs`). You can also
        provide the value to the `selected` argument of the navigation container
        (e.g., :func:`~shiny.ui.navset_tab`).
    icon
        An icon to appear inline with the button/link.
    target
        The `value` of an existing :func:`shiny.ui.nav` item, next to which tab will
        be added. Can also be `None`; see `position`.
    position
        The position of the new nav item relative to the target nav item. If
        `target=None`, then `"before"` means the new nav item should be inserted at
        the head of the navlist, and `"after"` is the end.
    select
        Whether the nav item should be selected upon insertion.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.
    """

    from ...ui import insert_nav_panel, nav_panel

    panel = nav_panel(
        title,
        *args,
        value=value,
        icon=icon,
    )

    insert_nav_panel(
        id=id,
        nav_panel=panel,
        target=target,
        position=position,
        select=select,
        session=session,
    )
