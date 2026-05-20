from __future__ import annotations

from pathlib import Path

__all__ = (
    "page_sidebar",
    "page_navbar",
    "page_fillable",
    "page_fluid",
    "page_fixed",
    "page_bootstrap",
    "page_auto",
    "page_output",
)

from copy import copy
from typing import Any, Callable, Literal, Optional, Sequence

from htmltools import (
    MetadataNode,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagList,
    css,
    div,
    head_content,
    tags,
)

from .._docstring import add_example, no_example
from .._namespaces import resolve_id_or_none
from ..types import DEPRECATED, MISSING, MISSING_TYPE, NavSetArg
from ._bootstrap import panel_title
from ._html_deps_external import Theme, ThemeProvider, shiny_page_theme_deps
from ._html_deps_py_shiny import page_output_dependency
from ._html_deps_shinyverse import components_dependencies
from ._navs import (
    NavbarOptions,
    NavMenu,
    NavPanel,
    navbar_options_resolve_deprecated,
    navset_bar,
)
from ._sidebar import Sidebar, SidebarOpen, layout_sidebar
from ._tag import consolidate_attrs
from ._utils import get_window_title
from .css import CssUnit, as_css_padding, as_css_unit
from .fill._fill import as_fill_item, as_fillable_container

page_sidebar_default: SidebarOpen = SidebarOpen(desktop="open", mobile="always")


@add_example()
def page_sidebar(
    sidebar: Sidebar,
    *args: TagChild | TagAttrs,
    title: Optional[str | Tag | TagList] = None,
    fillable: bool = False,
    fillable_mobile: bool = False,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
    theme: Optional[str | Path | Theme | ThemeProvider] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a page with a sidebar and a title.

    Parameters
    ----------
    sidebar
        Content to display in the sidebar.
    *args
        UI elements.
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
    theme
        A custom Shiny theme created using the :class:`~shiny.ui.Theme` class, or a path
        to a local or online CSS file that will replace the Bootstrap CSS bundled by
        default with a Shiny app. This file should be a complete `bootstrap.css` or
        `bootstrap.min.css` file.

        For advanced uses, you can also pass a :class:`~htmltools.Tagifiable` object.
        In this case, Shiny will suppress the default Bootstrap CSS.

        To modify the theme of an app without replacing the Bootstrap CSS entirely, use
        :func:`~shiny.ui.include_css` to add custom CSS.
    **kwargs
        Additional attributes passed to :func:`~shiny.ui.layout_sidebar`.

    Returns
    -------
    :
        A UI element.
    """

    if isinstance(title, str):
        title = tags.h1(title, class_="bslib-page-title navbar-brand")

    if title is not None:
        navbar_title = tags.div(
            tags.div(title, class_="container-fluid"),
            class_="navbar navbar-static-top",
        )
    else:
        navbar_title = None

    if not isinstance(sidebar, Sidebar):
        raise TypeError(
            "`sidebar=` is not a `Sidebar` instance. Use `ui.sidebar(...)` to create one."
        )

    if sidebar._default_open != page_sidebar_default:
        sidebar = copy(sidebar)
        sidebar._default_open = page_sidebar_default

    attrs, children = consolidate_attrs(*args, **kwargs)

    return page_fillable(
        {"class": "bslib-page-sidebar"},
        navbar_title,
        layout_sidebar(
            sidebar,
            page_main_container(*children, fillable=fillable),
            attrs,
            fillable=fillable,
            border=False,
            border_radius=False,
        ),
        get_window_title(title, window_title=window_title),
        padding=0,
        gap=0,
        lang=lang,
        theme=theme,
        fillable_mobile=fillable_mobile,
    )


def page_main_container(*args: TagChild, fillable: bool = True) -> Tag:
    main = tags.main({"class": "bslib-page-main bslib-gap-spacing"}, *args)
    if not fillable:
        return main
    return as_fillable_container(as_fill_item(main))


@no_example()
def page_navbar(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    title: Optional[str | Tag | TagList] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
    # Only page_navbar gets enhanced treatement for `fillable`
    # If an `*args`'s `data-value` attr string is in `fillable`, then the component is fillable
    fillable: bool | list[str] = False,
    fillable_mobile: bool = False,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    navbar_options: Optional[NavbarOptions] = None,
    fluid: bool = True,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
    theme: Optional[str | Path | Theme | ThemeProvider] = None,
    # Deprecated -- v1.3.0 2025-01 ----
    position: (
        Literal["static-top", "fixed-top", "fixed-bottom"] | MISSING_TYPE
    ) = DEPRECATED,
    bg: str | None | MISSING_TYPE = DEPRECATED,
    inverse: bool | MISSING_TYPE = DEPRECATED,
    underline: bool | MISSING_TYPE = DEPRECATED,
    collapsible: bool | MISSING_TYPE = DEPRECATED,
) -> Tag:
    """
    Create a page with a navbar and a title.

    Parameters
    ----------
    *args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match its
        ``value``).
    sidebar
        A :func:`~shiny.ui.sidebar` component to display on every page.
    fillable
        Whether or not the main content area should be considered a fillable
        (i.e., flexbox) container.
    fillable_mobile
        Whether or not ``fillable`` should apply on mobile devices.
    gap
        A CSS length unit defining the gap (i.e., spacing) between elements provided to
        `*args`. This value is only used when the navbar is _fillable_.
    padding
        Padding to use for the body. This can be a numeric vector (which will be
        interpreted as pixels) or a character vector with valid CSS lengths. The length
        can be between one and four. If one, then that value will be used for all four
        sides. If two, then the first value will be used for the top and bottom, while
        the second value will be used for left and right. If three, then the first will
        be used for top, the second will be left and right, and the third will be
        bottom. If four, then the values will be interpreted as top, right, bottom, and
        left respectively. This value is only used when the navbar is _fillable_.
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    window_title
        The browser's window title (defaults to the host URL of the page). Can also be
        set as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    theme
        A custom Shiny theme created using the :class:`~shiny.ui.Theme` class, or a path
        to a local or online CSS file that will replace the Bootstrap CSS bundled by
        default with a Shiny app. This file should be a complete `bootstrap.css` or
        `bootstrap.min.css` file.

        For advanced uses, you can also pass a :class:`~htmltools.Tagifiable` object.
        In this case, Shiny will suppress the default Bootstrap CSS.

        To modify the theme of an app without replacing the Bootstrap CSS entirely, use
        :func:`~shiny.ui.include_css` to add custom CSS.
    fluid
        ``True`` to use fluid layout; ``False`` to use fixed layout.
    navbar_options
        Configure the appearance and behavior of the navbar using
        :func:`~shiny.ui.navbar_options` to set properties like position, background
        color, and more.

        `navbar_options` was added in v1.3.0 and replaces deprecated arguments
        `position`, `bg`, `inverse`, `collapsible`, and `underline`.
    position
        Deprecated in v1.3.0. Please use `navbar_options` instead; see
        :func:`~shiny.ui.navbar_options` for details.

        Determines whether the navbar should be displayed at the top of the page with
        normal scrolling behavior ("static-top"), pinned at the top ("fixed-top"), or
        pinned at the bottom ("fixed-bottom"). Note that using "fixed-top" or
        "fixed-bottom" will cause the navbar to overlay your body content, unless you
        add padding (e.g., ``tags.style("body {padding-top: 70px;}")``).
    bg
        Deprecated in v1.3.0. Please use `navbar_options` instead; see
        :func:`~shiny.ui.navbar_options` for details.

        Background color of the navbar (a CSS color).
    inverse
        Deprecated in v1.3.0. Please use `navbar_options` instead; see
        :func:`~shiny.ui.navbar_options` for details.

        Either ``True`` for a light text color or ``False`` for a dark text color.
    collapsible
        Deprecated in v1.3.0. Please use `navbar_options` instead; see
        :func:`~shiny.ui.navbar_options` for details.

        ``True`` to automatically collapse the elements into an expandable menu on mobile devices or narrow window widths.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.nav`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.page_fluid`

    Example
    -------
    See :func:`~shiny.ui.nav`.
    """
    pageClass = "bslib-page-navbar"

    if sidebar is not None:
        if not isinstance(sidebar, Sidebar):
            raise TypeError(
                "`sidebar=` is not a `Sidebar` instance. Use `ui.sidebar(...)` to create one."
            )

        pageClass += " has-page-sidebar"
        if sidebar._default_open != page_sidebar_default:
            sidebar = copy(sidebar)
            sidebar._default_open = page_sidebar_default

    tagAttrs: TagAttrs = {"class": pageClass}

    navbar_options = navbar_options_resolve_deprecated(
        fn_caller="page_navbar",
        options_user=navbar_options,
        position=position,
        bg=bg,
        inverse=inverse,
        underline=underline,
        collapsible=collapsible,
    )

    navbar = navset_bar(
        *args,
        title=title,
        id=resolve_id_or_none(id),
        selected=selected,
        sidebar=sidebar,
        fillable=fillable,
        gap=gap,
        padding=padding,
        navbar_options=navbar_options,
        header=header,
        footer=footer,
        fluid=fluid,
    )
    # This is a page-level navbar, so opt into page-level layouts (in particular for
    # navbar with a global sidebar)
    navbar._is_page_level = True

    page_args = (
        tagAttrs,
        navbar,
        get_window_title(title, window_title=window_title),
    )
    page_kwargs = {
        "title": None,
        "lang": lang,
    }

    # If a sidebar is provided, we want the layout_sidebar(fill = TRUE) component
    # (which is a sibling of the <nav>) to always fill the page
    if fillable is False and sidebar is None:
        return page_bootstrap(
            *page_args,
            theme=theme,
            **page_kwargs,
        )

    else:
        return page_fillable(
            *page_args,
            fillable_mobile=fillable_mobile,
            padding=0,
            gap=0,
            theme=theme,
            **page_kwargs,
        )


@no_example()
def page_fillable(
    *args: TagChild | TagAttrs,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    gap: Optional[CssUnit] = None,
    fillable_mobile: bool = False,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    theme: Optional[str | Path | Theme | ThemeProvider] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a fillable page.

    Parameters
    ----------
    *args
        UI elements.
    padding
        Padding to use for the body. See :func:`~shiny.ui.css.as_css_padding`
        for more details.
    fillable_mobile
        Whether or not the page should fill the viewport's height on mobile devices
        (i.e., narrow windows).
    gap
        A CSS length unit passed through :func:`~shiny.ui.css.as_css_unit`
        defining the `gap` (i.e., spacing) between elements provided to `*args`.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    theme
        A custom Shiny theme created using the :class:`~shiny.ui.Theme` class, or a path
        to a local or online CSS file that will replace the Bootstrap CSS bundled by
        default with a Shiny app. This file should be a complete `bootstrap.css` or
        `bootstrap.min.css` file.

        For advanced uses, you can also pass a :class:`~htmltools.Tagifiable` object.
        In this case, Shiny will suppress the default Bootstrap CSS.

        To modify the theme of an app without replacing the Bootstrap CSS entirely, use
        :func:`~shiny.ui.include_css` to add custom CSS.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.page_fluid`
    * :func:`~shiny.ui.page_fixed`
    """
    attrs, children = consolidate_attrs(*args, **kwargs)

    style = css(padding=as_css_padding(padding), gap=as_css_unit(gap))

    page = page_bootstrap(
        head_content(tags.style("html { height: 100%; }")),
        {"class": "bslib-page-fill bslib-gap-spacing", "style": style},
        {"class": "bslib-flow-mobile"} if not fillable_mobile else None,
        attrs,
        *children,
        components_dependencies(),
        title=title,
        lang=lang,
        theme=theme,
    )

    # page returns a <html> tag, but we need to make the <body> fillable
    body = page.children[1]
    if not isinstance(body, Tag) or body.name != "body":
        raise ValueError("Expected a <body> tag")

    page.children[1] = as_fillable_container(body)

    return page


@add_example()
def page_fluid(
    *args: TagChild | TagAttrs,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    theme: Optional[str | Path | Theme | ThemeProvider] = None,
    **kwargs: str,
) -> Tag:
    """
    Create a fluid page.

    Parameters
    ----------
    *args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    theme
        A custom Shiny theme created using the :class:`~shiny.ui.Theme` class, or a path
        to a local or online CSS file that will replace the Bootstrap CSS bundled by
        default with a Shiny app. This file should be a complete `bootstrap.css` or
        `bootstrap.min.css` file.

        For advanced uses, you can also pass a :class:`~htmltools.Tagifiable` object.
        In this case, Shiny will suppress the default Bootstrap CSS.

        To modify the theme of an app without replacing the Bootstrap CSS entirely, use
        :func:`~shiny.ui.include_css` to add custom CSS.
    **kwargs
        Attributes on the page level container.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.page_fixed`
    * :func:`~shiny.ui.page_bootstrap`
    * :func:`~shiny.ui.page_navbar`
    """

    return page_bootstrap(
        div({"class": "container-fluid"}, *args, **kwargs),
        title=title,
        lang=lang,
        theme=theme,
    )


@add_example()
def page_fixed(
    *args: TagChild | TagAttrs,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    theme: Optional[str | Path | Theme | ThemeProvider] = None,
    **kwargs: str,
) -> Tag:
    """
    Create a fixed page.

    Parameters
    ----------
    *args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    theme
        A custom Shiny theme created using the :class:`~shiny.ui.Theme` class, or a path
        to a local or online CSS file that will replace the Bootstrap CSS bundled by
        default with a Shiny app. This file should be a complete `bootstrap.css` or
        `bootstrap.min.css` file.

        For advanced uses, you can also pass a :class:`~htmltools.Tagifiable` object.
        In this case, Shiny will suppress the default Bootstrap CSS.

        To modify the theme of an app without replacing the Bootstrap CSS entirely, use
        :func:`~shiny.ui.include_css` to add custom CSS.
    **kwargs
        Attributes on the page level container.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.page_fluid`
    * :func:`~shiny.ui.page_bootstrap`
    * :func:`~shiny.ui.page_navbar`
    """

    return page_bootstrap(
        div({"class": "container"}, *args, **kwargs),
        title=title,
        lang=lang,
        theme=theme,
    )


# TODO: implement theme (just Bootswatch for now?)
@no_example()
def page_bootstrap(
    *args: TagChild | TagAttrs,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    theme: Optional[str | Path | Theme | ThemeProvider] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a Bootstrap UI page container.

    Parameters
    ----------
    *args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    theme
        A custom Shiny theme created using the :class:`~shiny.ui.Theme` class, or a path
        to a local or online CSS file that will replace the Bootstrap CSS bundled by
        default with a Shiny app. This file should be a complete `bootstrap.css` or
        `bootstrap.min.css` file.

        For advanced uses, you can also pass a :class:`~htmltools.Tagifiable` object.
        In this case, Shiny will suppress the default Bootstrap CSS.

        To modify the theme of an app without replacing the Bootstrap CSS entirely, use
        :func:`~shiny.ui.include_css` to add custom CSS.
    **kwargs
        Attributes on the the `<body>` tag.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.page_fluid`
    * :func:`~shiny.ui.page_navbar`
    """
    head = tags.title(title) if title else None
    return tags.html(
        tags.head(head),
        tags.body(shiny_page_theme_deps(theme), *args, **kwargs),
        lang=lang,
    )


@no_example()
def page_auto(
    *args: TagChild | TagAttrs,
    title: str | MISSING_TYPE = MISSING,
    window_title: str | MISSING_TYPE = MISSING,
    lang: str | MISSING_TYPE = MISSING,
    theme: str | Path | Theme | ThemeProvider | MISSING_TYPE = MISSING,
    fillable: bool | MISSING_TYPE = MISSING,
    full_width: bool = False,
    page_fn: Callable[..., Tag] | None = None,
    **kwargs: object,
) -> Tag:
    """
    A page container which automatically decides which page function to use.

    If there is a top-level :func:`~shiny.ui.nav_panel`, :func:`~shiny.ui.page_auto`
    will use :func:`~shiny.ui.page_navbar`. Otherwise, if there is a top-level sidebar,
    :func:`~shiny.ui.page_sidebar` is used.

    If there are neither top-level nav panels nor sidebars, this will use the `fillable`
    and `full_width` arguments to determine which page function to use:

    1. If `fillable` is `True`, :func:`~shiny.ui.page_fillable` is used.
    2. Otherwise, if `full_width` is `True`, :func:`~shiny.ui.page_fluid` is used.
    3. If neither are `True`, :func:`~shiny.ui.page_fixed` is used.

    Parameters
    ----------
    *args
        UI elements. These are used to determine which page function to use, and they
        are also passed along to that page function.
    title
        A title shown on the page.
    window_title
        The browser window title. If no value is provided, this will use the value of
        ``title``.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    theme
        A custom Shiny theme created using the :class:`~shiny.ui.Theme` class, or a path
        to a local or online CSS file that will replace the Bootstrap CSS bundled by
        default with a Shiny app. This file should be a complete `bootstrap.css` or
        `bootstrap.min.css` file.

        For advanced uses, you can also pass a :class:`~htmltools.Tagifiable` object.
        In this case, Shiny will suppress the default Bootstrap CSS.

        To modify the theme of an app without replacing the Bootstrap CSS entirely, use
        :func:`~shiny.ui.include_css` to add custom CSS.
    fillable
        If there is a top-level sidebar or nav, then the value is passed through to the
        :func:`~shiny.ui.page_sidebar` or :func:`~shiny.ui.page_navbar` function.
        Otherwise, if ``True``, use :func:`~shiny.ui.page_fillable`, where the content
        fills the window; if ``False`` (the default), the value of ``full_width`` will
        determine which page function is used.
    full_width
        This has an effect only if there are no sidebars or top-level navs, and
        ``fillable`` is ``False``. If this is ``False`` (the default), use use
        :func:`~shiny.ui.page_fixed`; if ``True``, use :func:`~shiny.ui.page_fillable`.
    page_fn
        The page function to use. If ``None`` (the default), will automatically choose
        one based on the arguments provided. If not ``None``, this will override all
        heuristics for choosing page functions.
    **kwargs
        Additional arguments, which are passed to the page function.

    Returns
    -------
    :
        A UI element.
    """
    if not isinstance(title, MISSING_TYPE):
        kwargs["title"] = title
    if not isinstance(window_title, MISSING_TYPE):
        kwargs["window_title"] = window_title
    if not isinstance(lang, MISSING_TYPE):
        kwargs["lang"] = lang
    if not isinstance(theme, MISSING_TYPE):
        kwargs["theme"] = theme

    # Presence of a top-level nav items and/or sidebar determines the page function
    navs = [x for x in args if isinstance(x, (NavPanel, NavMenu))]
    sidebars = [x for x in args if isinstance(x, Sidebar)]

    nNavs = len(navs)
    nSidebars = len(sidebars)
    if page_fn is None:
        if nNavs == 0:
            if nSidebars == 0:
                if isinstance(fillable, MISSING_TYPE):
                    fillable = False

                if fillable:
                    page_fn = _page_auto_fillable
                elif full_width:
                    page_fn = _page_auto_fluid
                else:
                    page_fn = _page_auto_fixed

            elif nSidebars == 1:
                if not isinstance(fillable, MISSING_TYPE):
                    kwargs["fillable"] = fillable

                # page_sidebar() needs sidebar to be the first arg
                # TODO: Change page_sidebar() to remove `sidebar` and accept a sidebar as a
                # *arg.
                page_fn = page_sidebar
                args = tuple(sidebars + [x for x in args if x not in sidebars])

            else:
                raise NotImplementedError(
                    "Multiple top-level sidebars not allowed. Did you meant to wrap each one in layout_sidebar()?"
                )

        # At least one nav
        else:
            if not isinstance(fillable, MISSING_TYPE):
                kwargs["fillable"] = fillable

            if nSidebars == 0:
                # TODO: what do we do when nArgs != nNavs? Just let page_navbar handle it (i.e. error)?
                page_fn = page_navbar

            elif nSidebars == 1:
                # TODO: change page_navbar() to remove `sidebar` and accept a sidebar as a
                # *arg.
                page_fn = page_navbar
                args = tuple([x for x in args if x not in sidebars])
                kwargs["sidebar"] = sidebars[0]

            else:
                raise NotImplementedError(
                    "Multiple top-level sidebars not allowed in combination with top-level navs."
                )

    # If we got here, _page_fn is not None, but the type checker needs a little help.
    return page_fn(*args, **kwargs)


# For `page_fillable`, `page_fluid`, and `page_fixed`, the `title` arg sets the window
# title, but doesn't add anything visible on the page.
#
# In contrast, for `page_auto`, the `title` arg adds a title panel to the page, and the
# `window_title` arg sets the window title.
#
# The wrapper functions below provide the `page_auto` interface, where `title` to add a
# title panel to the page, and `window_title` to set the title of the window. If `title`
# is provided but `window_title` is not, then `window_title` is set to the value of
# `title`.
def _page_auto_fillable(
    *args: TagChild | TagAttrs,
    title: str | None = None,
    window_title: str | None = None,
    **kwargs: Any,
) -> Tag:
    if window_title is None and title is not None:
        window_title = title

    return page_fillable(
        None if title is None else panel_title(title),
        *args,
        title=window_title,
        **kwargs,
    )


def _page_auto_fluid(
    *args: TagChild | TagAttrs,
    title: str | None = None,
    window_title: str | None = None,
    **kwargs: str,
) -> Tag:
    if window_title is None and title is not None:
        window_title = title

    return page_fluid(
        None if title is None else panel_title(title),
        *args,
        title=window_title,
        **kwargs,
    )


def _page_auto_fixed(
    *args: TagChild | TagAttrs,
    title: str | None = None,
    window_title: str | None = None,
    **kwargs: Any,
) -> Tag:
    if window_title is None and title is not None:
        window_title = title

    return page_fixed(
        None if title is None else panel_title(title),
        *args,
        title=window_title,
        **kwargs,
    )


@no_example()
def page_output(id: str) -> Tag:
    """
    Create a page container where the entire body is a UI output.

    Parameters
    ----------
    id
        An output id.

    Returns
    -------
    :
        A UI element which is meant to be used as a page container.
    """
    return tags.html(
        tags.head(),
        tags.body(id=id, class_="shiny-page-output"),
        page_output_dependency(),
        lang="en",
    )
