from __future__ import annotations

from typing import Literal, Optional

from htmltools import TagAttrs, TagAttrValue, TagChild, TagList

from ..._deprecated import warn_deprecated
from ...session import Session
from ._navs import NavSetArg, NavSetCard, navset_card_pill, navset_card_tab
from ._sidebar import (
    DeprecatedPanelMain,
    DeprecatedPanelSidebar,
    Sidebar,
    toggle_sidebar,
)
from ._tooltip import toggle_tooltip, update_tooltip
from ._utils import consolidate_attrs

__all__ = (
    # Navs
    "navset_pill_card",
    "navset_tab_card",
    # Tooltip
    "tooltip_update",
    # Sidebar
    "sidebar_toggle",
    "panel_sidebar",
    "panel_main",
    "DeprecatedPanelSidebar",
    "DeprecatedPanelMain",
)


######################
# Navs
######################


# Deprecated 2023-08-15
def navset_pill_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
    placement: Literal["above", "below"] = "above",
) -> NavSetCard:
    """Deprecated. Please use `navset_card_pill()` instead of `navset_pill_card()`."""
    warn_deprecated(
        "`navset_pill_card()` is deprecated. "
        "This method will be removed in a future version, "
        "please use :func:`~shiny.experimental.ui.navset_card_pill` instead."
    )
    return navset_card_pill(
        *args,
        id=id,
        selected=selected,
        sidebar=sidebar,
        header=header,
        footer=footer,
        placement=placement,
    )


# Deprecated 2023-08-15
def navset_tab_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> NavSetCard:
    """Deprecated. Please use `navset_card_tab()` instead of `navset_tab_card()`."""
    warn_deprecated(
        "`navset_tab_card()` is deprecated. "
        "This method will be removed in a future version, "
        "please use :func:`~shiny.experimental.ui.navset_card_tab` instead."
    )
    return navset_card_tab(
        *args,
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


######################
# Tooltip
######################
# Deprecated 2023-08-23
def tooltip_update(id: str, *args: TagChild, session: Optional[Session] = None) -> None:
    """Deprecated. Please use `update_tooltip()` instead of `tooltip_update()`."""
    warn_deprecated(
        "`tooltip_update()` is deprecated. "
        "This method will be removed in a future version, "
        "please use :func:`~shiny.experimental.ui.update_tooltip` instead."
    )
    update_tooltip(
        id,
        *args,
        session=session,
    )


# Deprecated 2023-08-23
def tooltip_toggle(
    id: str,
    show: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `toggle_tooltip()` instead of `tooltip_toggle()`."""
    warn_deprecated(
        "`tooltip_toggle()` is deprecated. "
        "This method will be removed in a future version, "
        "please use :func:`~shiny.experimental.ui.toggle_tooltip` instead."
    )
    toggle_tooltip(
        id=id,
        show=show,
        session=session,
    )


######################
# Sidebar
######################


# Deprecated 2023-08-23
def sidebar_toggle(
    id: str,
    open: Literal["toggle", "open", "closed", "always"] | bool | None = None,
    session: Session | None = None,
) -> None:
    """Deprecated. Please use `toggle_sidebar()` instead of `sidebar_toggle()`."""
    warn_deprecated(
        "`sidebar_toggle()` is deprecated. "
        "This method will be removed in a future version, "
        "please use :func:`~shiny.experimental.ui.toggle_sidebar` instead."
    )
    toggle_sidebar(
        id=id,
        open=open,
        session=session,
    )


# Deprecated 2023-06-13
# Includes: DeprecatedPanelSidebar
def panel_sidebar(
    *args: TagChild | TagAttrs,
    width: int = 4,
    **kwargs: TagAttrValue,
) -> DeprecatedPanelSidebar:
    """Deprecated. Please use :func:`~shiny.experimental.ui.sidebar` instead of
    `ui.panel_sidebar()`."""
    # TODO-future: >= 2023-11-01; Add deprecation message below
    # Plan of action:
    # * No deprecation messages today (2023-05-18), and existing code _just works_.
    # * Change all examples to use the new API.
    # * In, say, 6 months, start emitting messages for code that uses the old API.

    # warn_deprecated("Please use `sidebar()` instead of `panel_sidebar()`. `panel_sidebar()` will go away in a future version of Shiny.")
    return DeprecatedPanelSidebar(
        *args,
        width=width,
        **kwargs,
    )


# Deprecated 2023-06-13
# Includes: DeprecatedPanelMain
def panel_main(
    *args: TagChild | TagAttrs,
    width: int = 8,
    **kwargs: TagAttrValue,
) -> TagList | DeprecatedPanelMain:
    """Deprecated. Please supply `panel_main(*args)` directly to `layout_sidebar()`."""
    # TODO-future: >= 2023-11-01; Add deprecation message below
    # warn_deprecated(
    #     "Please supply `panel_main(*args)` directly to `layout_sidebar()`."
    # )
    # warn if keys are being ignored
    attrs, children = consolidate_attrs(*args, **kwargs)
    if len(attrs) > 0:
        return DeprecatedPanelMain(attrs=attrs, children=children)
        warn_deprecated(
            "`*args: TagAttrs` or `**kwargs: TagAttrValue` values supplied to `panel_main()` are being ignored. Please supply them directly to `layout_sidebar()`."
        )

    return TagList(*children)
