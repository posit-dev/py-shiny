__all__ = ("insert_nav_panel", "remove_nav_panel", "update_nav_panel")

import sys
from typing import Optional, Union

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from .._docstring import add_example, no_example
from .._namespaces import resolve_id
from ..session import Session, require_active_session
from ..types import NavSetArg
from ._navs import menu_string_as_nav


@add_example()
def insert_nav_panel(
    id: str,
    nav_panel: Union[NavSetArg, str],
    target: Optional[str] = None,
    position: Literal["after", "before"] = "after",
    select: bool = False,
    session: Optional[Session] = None,
) -> None:
    """
    Insert a new nav item into a navigation container.

    Parameters
    ----------
    id
        The `id` of the relevant navigation container (i.e., `navset_*()` object).
    nav_panel
        The navigation item to insert (typically a :func:`~shiny.ui.nav_panel` or
        :func:`~shiny.ui.nav_menu`). A :func:`~shiny.ui.nav_menu` isn't allowed when the
        `target` references an :func:`~shiny.ui.nav_menu` (or an item within it). A
        string is only allowed when the `target` references a
        :func:`~shiny.ui.nav_menu`.
    target
        The `value` of an existing :func:`shiny.ui.nav_panel`, next to which tab will
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

    See Also
    --------
    ~shiny.ui.remove_nav_panel
    ~shiny.ui.update_nav_panel
    ~shiny.ui.nav_panel
    """

    session = require_active_session(session)

    # N.B. this is only sensible if the target is a menu, but we don't know that,
    # which could cause confusion of we decide to support top-level strings at some
    # in the future.
    if isinstance(nav_panel, str):
        nav = menu_string_as_nav(nav_panel)
    else:
        nav = nav_panel

    # N.B. shiny.js' is smart enough to know how to add active classes and href/id attrs
    li_tag, div_tag = nav.resolve(
        selected=None, context=dict(tabsetid="tsid", index="id")
    )

    msg = {
        "inputId": resolve_id(id),
        "liTag": session._process_ui(li_tag),
        "divTag": session._process_ui(div_tag),
        "menuName": None,
        "target": target,
        "position": position,
        "select": select,
    }

    session._send_message_sync({"shiny-insert-tab": msg})


@no_example()
def remove_nav_panel(id: str, target: str, session: Optional[Session] = None) -> None:
    """
    Remove a nav item from a navigation container.

    Parameters
    ----------
    id
        The `id` of the relevant navigation container (i.e., `navset_*()` object).
    target
        The `value` of an existing :func:`shiny.ui.nav_panel` item to remove.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Note
    ----
    See :func:`~shiny.ui.insert_nav_panel` for an example.

    See Also
    --------
    ~shiny.ui.insert_nav_panel
    ~shiny.ui.update_nav_panel
    ~shiny.ui.nav_panel
    """

    session = require_active_session(session)
    msg = {
        "inputId": resolve_id(id),
        "target": target,
    }

    session._send_message_sync({"shiny-remove-tab": msg})


@add_example()
def update_nav_panel(
    id: str,
    target: str,
    method: Literal["show", "hide"],
    session: Optional[Session] = None,
) -> None:
    """
    Show/hide a navigation item

    Parameters
    ----------
    id
        The `id` of the relevant navigation container (i.e., `navset_*()` object).
    target
        The `value` of an existing :func:`shiny.ui.nav_panel` item to show.
    method
        The action to perform on the nav_panel (`"show"` or `"hide"`).
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Note
    ----
    On reveal, the `nav_panel` will not be the active tab. To change the active tab, use :func:`~shiny.ui.update_navset()`
    For example:
    ```python
    @reactive.effect
    @reactive.event(input.show_tab)
    def _():
        ui.update_nav_panel("tabset_id", target="Foo", method="show")
        ui.update_navset("tabset_id", selected="Foo")
    ```

    See Also
    --------
    ~shiny.ui.insert_nav_panel
    ~shiny.ui.remove_nav_panel
    ~shiny.ui.nav_panel
    ~shiny.ui.update_navset
    """

    session = require_active_session(session)

    msg = {
        "inputId": resolve_id(id),
        "target": target,
        "type": method,
    }

    session._send_message_sync({"shiny-change-tab-visibility": msg})
