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
