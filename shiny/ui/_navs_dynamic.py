__all__ = (
    "nav_insert",
    "nav_remove",
    "nav_hide",
    "nav_show",
)

import sys
from typing import Optional, Union

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from .._docstring import add_example
from .._namespaces import resolve_id
from .._utils import run_coro_sync
from ..session import Session, require_active_session
from ..types import NavSetArg
from ._input_update import update_navs
from ._navs import menu_string_as_nav


@add_example()
def nav_insert(
    id: str,
    nav: Union[NavSetArg, str],
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
        The ``id`` of the relevant navigation container (i.e., ``navset_*()`` object).
    nav
        The navigation item to insert (typically a :func:`~shiny.ui.nav` or
        :func:`~shiny.ui.nav_menu`). A :func:`~shiny.ui.nav_menu` isn't allowed when the
        ``target`` references an :func:`~shiny.ui.nav_menu` (or an item within it). A
        string is only allowed when the ``target`` references a
        :func:`~shiny.ui.nav_menu`.
    target
        The ``value`` of an existing :func:`shiny.ui.nav` item, next to which tab will
        be added. Can also be ``None``; see ``position``.
    position
        The position of the new nav item relative to the target nav item. If
        ``target=None``, then ``"before"`` means the new nav item should be inserted at
        the head of the navlist, and ``"after"`` is the end.
    select
        Whether the nav item should be selected upon insertion.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    See Also
    --------
    ~nav_remove
    ~nav_show
    ~nav_hide
    ~shiny.ui.nav
    """

    session = require_active_session(session)

    # N.B. this is only sensible if the target is a menu, but we don't know that,
    # which could cause confusion of we decide to support top-level strings at some
    # in the future.
    if isinstance(nav, str):
        nav = menu_string_as_nav(nav)

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

    def callback() -> None:
        run_coro_sync(session._send_message({"shiny-insert-tab": msg}))

    session.on_flush(callback, once=True)


def nav_remove(id: str, target: str, session: Optional[Session] = None) -> None:
    """
    Remove a nav item from a navigation container.

    Parameters
    ----------
    id
        The ``id`` of the relevant navigation container (i.e., ``navset_*()`` object).
    target
        The ``value`` of an existing :func:`shiny.ui.nav` item to remove.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    See Also
    --------
    ~nav_insert
    ~nav_show
    ~nav_hide
    ~shiny.ui.nav
    """

    session = require_active_session(session)

    msg = {"inputId": resolve_id(id), "target": target}

    def callback() -> None:
        run_coro_sync(session._send_message({"shiny-remove-tab": msg}))

    session.on_flush(callback, once=True)


def nav_show(
    id: str, target: str, select: bool = False, session: Optional[Session] = None
) -> None:
    """
    Show a navigation item

    Parameters
    ----------
    id
        The ``id`` of the relevant navigation container (i.e., ``navset_*()`` object).
    target
        The ``value`` of an existing :func:`shiny.ui.nav` item to show.
    select
        Whether the nav item's content should also be shown.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Note
    ----
    For ``nav_show()`` to be relevant/useful, a :func:`shiny.ui.nav` item must
    have been hidden using :func:`~nav_hide`.

    See Also
    --------
    ~nav_hide
    ~nav_insert
    ~nav_remove
    ~shiny.ui.nav
    """

    session = require_active_session(session)

    id = resolve_id(id)
    if select:
        update_navs(id, selected=target)

    msg = {"inputId": id, "target": target, "type": "show"}

    def callback() -> None:
        run_coro_sync(session._send_message({"shiny-change-tab-visibility": msg}))

    session.on_flush(callback, once=True)


def nav_hide(id: str, target: str, session: Optional[Session] = None) -> None:
    """
    Hide a navigation item

    Parameters
    ----------
    id
        The ``id`` of the relevant navigation container (i.e., ``navset_*()`` object).
    target
        The ``value`` of an existing :func:`shiny.ui.nav` item to hide.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    See Also
    --------
    ~nav_show
    ~nav_insert
    ~nav_remove
    ~shiny.ui.nav
    """

    session = require_active_session(session)

    msg = {"inputId": resolve_id(id), "target": target, "type": "hide"}

    def callback() -> None:
        run_coro_sync(session._send_message({"shiny-change-tab-visibility": msg}))

    session.on_flush(callback, once=True)
