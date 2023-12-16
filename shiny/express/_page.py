from __future__ import annotations

from typing import Callable, Literal, Optional, cast

from htmltools import Tag, TagAttrValue, TagChild, TagList

from .. import ui
from ..types import MISSING, MISSING_TYPE
from ..ui._navs import NavMenu, NavPanel
from ..ui._sidebar import Sidebar
from ..ui.css import CssUnit
from ._recall_context import RecallContextManager
from ._run import get_top_level_recall_context_manager

__all__ = (
    "page_auto",
    "page_auto_cm",
    "set_page_title",
    "set_page_lang",
    "set_page_fillable",
    "set_page_wider",
    "use_page_fixed",
    "use_page_fluid",
    "use_page_fillable",
    "use_page_sidebar",
    "use_page_navbar",
)


def page_auto_cm() -> RecallContextManager[Tag]:
    return RecallContextManager(
        page_auto,
        kwargs={
            "_page_fn": None,
            "_fillable": False,
            "_wider": False,
        },
    )


def page_auto(
    *args: object,
    _page_fn: Callable[[object], Tag] | None,
    _fillable: bool,
    _wider: bool,
    **kwargs: object,
) -> Tag:
    # Presence of a top-level nav items and/or sidebar determines the page function
    navs = [x for x in args if isinstance(x, (NavPanel, NavMenu))]
    sidebars = [x for x in args if isinstance(x, ui.Sidebar)]

    nNavs = len(navs)
    nSidebars = len(sidebars)

    if _page_fn is None:
        if nNavs == 0:
            if nSidebars == 0:
                if _fillable:
                    _page_fn = (
                        ui.page_fillable
                    )  # pyright: ignore[reportGeneralTypeIssues]
                elif _wider:
                    _page_fn = ui.page_fluid  # pyright: ignore[reportGeneralTypeIssues]
                else:
                    _page_fn = ui.page_fixed  # pyright: ignore[reportGeneralTypeIssues]

            elif nSidebars == 1:
                # page_sidebar() needs sidebar to be the first arg
                # TODO: Change page_sidebar() to remove `sidebar` and accept a sidebar as a
                # *arg.
                _page_fn = ui.page_sidebar  # pyright: ignore[reportGeneralTypeIssues]
                args = tuple(sidebars + [x for x in args if x not in sidebars])

            else:
                raise NotImplementedError(
                    "Multiple top-level sidebars not allowed. Did you meant to wrap each one in layout_sidebar()?"
                )

        # At least one nav
        else:
            if nSidebars == 0:
                # TODO: what do we do when nArgs != nNavs? Just let page_navbar handle it (i.e. error)?
                _page_fn = ui.page_navbar  # pyright: ignore[reportGeneralTypeIssues]

            elif nSidebars == 1:
                # TODO: change page_navbar() to remove `sidebar` and accept a sidebar as a
                # *arg.
                _page_fn = ui.page_navbar  # pyright: ignore[reportGeneralTypeIssues]
                kwargs["sidebar"] = sidebars[0]

            else:
                raise NotImplementedError(
                    "Multiple top-level sidebars not allowed in combination with top-level navs."
                )

    # If we got here, _page_fn is not None, but the type checker needs a little help.
    _page_fn = cast(Callable[[object], Tag], _page_fn)
    return _page_fn(*args, **kwargs)


# ======================================================================================
# Page attribute setters
# ======================================================================================


def set_page_title(title: str) -> None:
    get_top_level_recall_context_manager().kwargs["title"] = title


def set_page_fillable(fillable: bool) -> None:
    get_top_level_recall_context_manager().kwargs["_fillable"] = fillable


def set_page_wider(wider: bool) -> None:
    get_top_level_recall_context_manager().kwargs["_wider"] = wider


def set_page_lang(lang: str) -> None:
    get_top_level_recall_context_manager().kwargs["lang"] = lang


# ======================================================================================
# Page functions
# ======================================================================================


def use_page_fixed(
    *,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: str,
) -> None:
    """
    Create a fixed page.

    This function wraps :func:`~shiny.ui.page_fixed`.

    Parameters
    ----------
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
        Attributes on the page level container.
    """
    get_top_level_recall_context_manager().kwargs.update(
        dict(
            _page_fn=ui.page_fixed,
            title=title,
            lang=lang,
            **kwargs,
        )
    )


def use_page_fluid(
    *,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: str,
) -> None:
    """
    Create a fluid page.

    This function wraps :func:`~shiny.ui.page_fluid`.

    Parameters
    ----------
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
        Attributes on the page level container.
    """
    get_top_level_recall_context_manager().kwargs.update(
        dict(
            _page_fn=ui.page_fluid,
            title=title,
            lang=lang,
            **kwargs,
        )
    )


def use_page_fillable(
    *,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    gap: Optional[CssUnit] = None,
    fillable_mobile: bool = False,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> None:
    """
    Use a fillable page.

    This function wraps :func:`~shiny.ui.page_fillable`.

    Parameters
    ----------
    padding
        Padding to use for the body. See :func:`~shiny.ui.css_unit.as_css_padding`
        for more details.
    fillable_mobile
        Whether or not the page should fill the viewport's height on mobile devices
        (i.e., narrow windows).
    gap
        A CSS length unit passed through :func:`~shiny.ui.css_unit.as_css_unit`
        defining the `gap` (i.e., spacing) between elements provided to `*args`.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    """
    get_top_level_recall_context_manager().kwargs.update(
        dict(
            _page_fn=ui.page_fillable,
            padding=padding,
            gap=gap,
            fillable_mobile=fillable_mobile,
            title=title,
            lang=lang,
            **kwargs,
        )
    )


def use_page_sidebar(
    *,
    title: Optional[str | Tag | TagList] = None,
    fillable: bool = True,
    fillable_mobile: bool = False,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> None:
    """
    Create a page with a sidebar and a title.
    This function wraps :func:`~shiny.ui.page_sidebar`.
    Parameters
    ----------
    sidebar
        Content to display in the sidebar.
    title
        A title to display at the top of the page.
    fillable
        Whether or not the main content area should be considered a fillable
        (i.e., flexbox) container.
    fillable_mobile
        Whether or not ``fillable`` should apply on mobile devices.
    window_title
        The browser's window title (defaults to the host URL of the page). Can also be
        set as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
        Additional attributes passed to :func:`~shiny.ui.layout_sidebar`.
    Returns
    -------
    :
        A UI element.
    """
    get_top_level_recall_context_manager().kwargs.update(
        dict(
            _page_fn=ui.page_sidebar,
            title=title,
            fillable=fillable,
            fillable_mobile=fillable_mobile,
            window_title=window_title,
            lang=lang,
            **kwargs,
        )
    )


def use_page_navbar(
    *,
    title: Optional[str | Tag | TagList] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
    # Only page_navbar gets enhanced treatement for `fillable`
    # If an `*args`'s `data-value` attr string is in `fillable`, then the component is fillable
    fillable: bool | list[str] = True,
    fillable_mobile: bool = False,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    bg: Optional[str] = None,
    inverse: bool = False,
    underline: bool = True,
    collapsible: bool = True,
    fluid: bool = True,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
) -> None:
    get_top_level_recall_context_manager().kwargs.update(
        dict(
            _page_fn=ui.page_navbar,
            title=title,
            id=id,
            selected=selected,
            sidebar=sidebar,
            fillable=fillable,
            fillable_mobile=fillable_mobile,
            gap=gap,
            padding=padding,
            position=position,
            header=header,
            footer=footer,
            bg=bg,
            inverse=inverse,
            underline=underline,
            collapsible=collapsible,
            fluid=fluid,
            window_title=window_title,
            lang=lang,
        )
    )
