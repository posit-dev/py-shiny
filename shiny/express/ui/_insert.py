"""
Shims for `ui.insert_*()`, `ui.update_*()`, etc. functions that lead to a more ergonomic
Express API.
These functions tend to have one issue in common: if they were re-exported verbatim from
Core to Express, they would want to take RecallContextManager(s) as input, which leads
to a somewhat awkward API. That's because, you'd have to know to use something like
@ui.hold() pass the UI as a value without displaying it.
"""

from typing import Literal, Optional, Union

from htmltools import TagAttrs, TagChild

from ..._docstring import add_example
from ...session import Session
from ...types import MISSING, MISSING_TYPE


@add_example()
def insert_accordion_panel(
    id: str,
    panel_title: str,
    *panel_contents: Union[TagChild, TagAttrs],
    panel_value: Union[str, MISSING_TYPE, None] = MISSING,
    panel_icon: TagChild = None,
    target: Optional[str] = None,
    position: Literal["after", "before"] = "after",
    session: Optional[Session] = None,
) -> None:
    """
    Insert an accordion panel into an existing accordion.

    Parameters
    ----------
    id
        A string that matches an existing :func:`~shiny.ui.express.accordion`'s `id`.
    panel_title
        The title to appear in the panel header.
    panel_contents
        UI elements for the panel's body. Can also be a dict of tag attributes for the
        body's HTML container.
    panel_value
        A character string that uniquely identifies this panel. If `MISSING`, the
        `title` will be used.
    panel_icon
        A :class:`~htmltools.TagChild` which is positioned just before the `title`.
    target
        The `value` of an existing panel to insert next to.
    position
        Should `panel` be added before or after the target? When `target=None`,
        `"after"` will append after the last panel and `"before"` will prepend before
        the first panel.
    session
        A Shiny session object (the default should almost always be used).

    References
    ----------
    [Bootstrap Accordion](https://getbootstrap.com/docs/5.3/components/accordion/)

    See Also
    --------
    * :func:`~shiny.ui.express.accordion`
    * :func:`~shiny.ui.express.accordion_panel`
    * :func:`~shiny.ui.express.update_accordion`
    """

    from ...ui import AccordionPanel, accordion_panel, insert_accordion_panel

    if isinstance(panel_title, AccordionPanel):
        # If the user passed an AccordionPanel, we can just use it as is.
        # This isn't recommended, but we support it for backwards compatibility
        # with the old API.
        panel = panel_title
    else:
        panel = accordion_panel(
            panel_title, *panel_contents, value=panel_value, icon=panel_icon
        )

    insert_accordion_panel(
        id=id,
        panel=panel,
        target=target,
        position=position,
        session=session,
    )


@add_example()
def insert_nav_panel(
    id: str,
    title: TagChild,
    *args: TagChild,
    value: Optional[str] = None,
    icon: TagChild = None,
    target: Optional[str] = None,
    position: Literal["after", "before"] = "after",
    select: bool = False,
    session: Optional[Session] = None,
) -> None:
    """
    Create a new nav panel in an existing navset.

    Parameters
    ----------
    id
        The id of the navset container to insert into.
    title
        A title for the inserted nav panel. Can be a character string or UI elements (i.e., tags).
    *args
        UI elements for the inserted nav panel.
    value
        The value of the panel. Use this value to determine whether the panel is active
        (when an `id` is provided to the nav container) or to programmatically
        select the item (e.g., :func:`~shiny.ui.update_navset`). You can also
        provide the value to the `selected` argument of the navigation container
        (e.g., :func:`~shiny.ui.navset_tab`).
    icon
        An icon to appear inline with the title.
    target
        The `value` of an existing :func:`shiny.ui.nav_panel`, next to which tab will
        be added. Can also be `None`; see `position`.
    position
        The position of the new nav panel relative to the target. If
        `target=None`, then `"before"` means the new panel should be inserted at
        the head of the navlist, and `"after"` is the end.
    select
        Whether the nav panel should be selected upon insertion.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Note
    ----
    Unlike :func:`~shiny.ui.insert_nav_panel`, this function does not support inserting
    of a heading/divider into an existing :func:`~shiny.ui.nav_menu`. To do so, use
    :func:`~shiny.ui.insert_nav_panel` instead of this Express variant (i.e.,
    `shiny.ui.insert_nav_panel("id", "Header")`).
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
