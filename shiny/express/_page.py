from __future__ import annotations

from htmltools import Tag

from .. import ui
from ..ui._navs import NavMenu, NavPanel
from ._recall_context import RecallContextManager


def page_auto_cm() -> RecallContextManager[Tag]:
    return RecallContextManager(page_auto)


def page_auto(*args: object) -> Tag:
    # Presence of a top-level nav items and/or sidebar determines the page function
    navs = [x for x in args if isinstance(x, (NavPanel, NavMenu))]
    sidebars = [x for x in args if isinstance(x, ui.Sidebar)]

    nNavs = len(navs)
    nSidebars = len(sidebars)

    if nNavs == 0:
        if nSidebars == 0:
            return _DEFAULT_PAGE_FUNCTION(
                *args  # pyright: ignore[reportGeneralTypeIssues]
            )

        if nSidebars == 1:
            # page_sidebar() needs sidebar to be the first arg
            new_args = sidebars + [x for x in args if x not in sidebars]
            return ui.page_sidebar(
                *new_args  # pyright: ignore[reportGeneralTypeIssues]
            )

        if nSidebars > 1:
            raise NotImplementedError(
                "Multiple top-level sidebars not allowed. Did you meant to wrap each one in layout_sidebar()?"
            )

    # At least one nav
    else:
        if nSidebars == 0:
            # TODO: what do we do when nArgs != nNavs? Just let page_navbar handle it (i.e. error)?
            return ui.page_navbar(*args)  # pyright: ignore[reportGeneralTypeIssues]

        if nSidebars == 1:
            return ui.page_navbar(
                *args,  # pyright: ignore[reportGeneralTypeIssues]
                sidebar=sidebars[0],
            )

        if nSidebars > 1:
            raise NotImplementedError(
                "Multiple top-level sidebars not allowed in combination with top-level navs"
            )

    return _DEFAULT_PAGE_FUNCTION(*args)  # pyright: ignore[reportGeneralTypeIssues]


_DEFAULT_PAGE_FUNCTION = ui.page_fixed
