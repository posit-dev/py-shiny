from __future__ import annotations

from typing import cast

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

    # TODO: How should this work with .set_page_*()/.set_title()?
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

        # If multiple sidebars(), wrap them in layout_sidebar()
        # TODO:
        # 1. Maybe this logic be should handled by non-top-level ctx managers?
        #    That is, if we're not in a top-level ctx manager, automatically wrap
        #    Sidebar() into layout_sidebar()?
        # 2. Provide a way to exit the layout.sidebar() context? Maybe '---'?
        if nSidebars > 1:
            new_args: object = []
            sidebar_idx = [i for i, x in enumerate(args) if isinstance(x, ui.Sidebar)]
            new_args.append(*args[0 : sidebar_idx[0]])
            for i, x in enumerate(sidebar_idx):
                j = sidebar_idx[i + 1] if i < len(sidebar_idx) - 1 else len(args)
                s = ui.layout_sidebar(
                    cast(ui.Sidebar, args[x]),
                    *self.args[x + 1 : j],  # type: ignore
                )
                new_args.append(s)

            return _DEFAULT_PAGE_FUNCTION(*new_args)

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
