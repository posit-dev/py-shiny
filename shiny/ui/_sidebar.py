from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Optional, TypedDict, cast

from htmltools import (
    HTML,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagList,
    css,
    div,
    tags,
)

from .._deprecated import warn_deprecated
from .._docstring import add_example, no_example
from .._namespaces import ResolvedId, resolve_id_or_none
from .._utils import private_random_id
from ..session import require_active_session
from ..types import MISSING, MISSING_TYPE
from ._card import CardItem
from ._html_deps_shinyverse import components_dependencies
from ._tag import consolidate_attrs, trinary
from ._utils import css_no_sub
from .css import CssUnit, as_css_padding, as_css_unit
from .fill import as_fill_item, as_fillable_container

if TYPE_CHECKING:
    from .. import Session

__all__ = (
    "Sidebar",
    "SidebarOpen",
    "sidebar",
    "layout_sidebar",
    "update_sidebar",
    # Legacy
    "panel_sidebar",
    "panel_main",
)

SidebarOpenValue = Literal["open", "closed", "always"]
"""
A possible value for the `open` parameter in :func:`~shiny.ui.sidebar`:

* `"open"`: the sidebar starts open
* `"closed"`: the sidebar starts closed
* `"always"`: the sidebar is always open and cannot be closed
"""


class SidebarOpenSpec(TypedDict):
    desktop: SidebarOpenValue
    mobile: SidebarOpenValue


@dataclass
class SidebarOpen:
    """
    The initial state of the sidebar at `desktop` and `mobile` screen sizes.
    """

    desktop: SidebarOpenValue = "open"
    """The initial state of the sidebar on desktop screen sizes."""

    mobile: SidebarOpenValue = "closed"
    """The initial state of the sidebar on mobile screen sizes."""

    _VALUES: tuple[SidebarOpenValue, ...] = field(
        default=("open", "closed", "always"),
        repr=False,
        hash=False,
        compare=False,
    )

    @staticmethod
    def _values_str() -> str:
        return f"""'{"', '".join(SidebarOpen._VALUES)}'"""

    def __post_init__(self):
        if self.desktop not in self._VALUES:
            raise ValueError(f"`desktop` must be one of {self._values_str()}")
        if self.mobile not in self._VALUES:
            raise ValueError(f"`mobile` must be one of {self._values_str()}")

    @classmethod
    def _from_string(cls, open: str) -> SidebarOpen:
        """
        Takes a single string describing the initial sidebar state and returns a
        :class:`~shiny.ui.SidebarOpen` object. In general, the value of `open` becomes
        the initial state for both desktop and mobile screen sizes, unless `open` is
        `"desktop"`, in which case the sidebar starts open on desktop screen, closed on
        mobile.

        Parameters
        ----------
        open
            The initial state of the sidebar. The possible values are:

            * `"desktop"`: the sidebar starts open on desktop screen, closed on mobile
            * `"open"`: the sidebar starts open
            * `"closed"`: the sidebar starts closed
            * `"always"`: the sidebar is always open and cannot be closed

        Returns
        -------
        :
            A :class:`~shiny.ui.SidebarOpen` object.
        """
        bad_value = ValueError(
            f"`open` must be a non-empty string of one of {SidebarOpen._values_str()}."
        )

        if not isinstance(open, str) or len(open) == 0:
            raise bad_value

        if open == "desktop":
            return cls(desktop="open", mobile="closed")
        elif open in cls._VALUES:
            return cls(desktop=open, mobile=open)
        else:
            raise bad_value

    @classmethod
    def _as_open(
        cls,
        open: SidebarOpenSpec | SidebarOpenValue | Literal["desktop"],
    ) -> SidebarOpen:
        if isinstance(open, dict):
            return cls(**open)

        if isinstance(open, str):
            return cls._from_string(open)

        raise ValueError(
            f"""`open` must be one of {SidebarOpen._values_str()}, """
            + "or a dictionary with keys `desktop` and `mobile` using these values."
        )


@no_example()
class Sidebar:
    """
    A sidebar object

    Class returned from :func:`~shiny.ui.sidebar`. Please do not use this
    class directly. Instead, supply the :func:`~shiny.ui.sidebar` object to
    :func:`~shiny.ui.layout_sidebar`.

    Attributes
    ----------
    children
        A tuple of :class:`~htmltools.Tag` objects that are the contents of the sidebar.
    attrs
        A dictionary of attributes that are supplied to the sidebar contents
        :class:`~htmltools.Tag` container.
    width
        A valid CSS unit used for the width of the sidebar.
    position
        Where the sidebar should appear relative to the main content, one of `"left"` or
        `"right"`.
    id
        The resolved ID. Required if wanting to reactively read (or update) the
        `collapsible` state in a Shiny app.
    title
        A character title to be used as the sidebar title, which will be wrapped in a
        `<div>` element with class `sidebar-title`. You can also provide a custom
        :class:`~htmltools.Tag` for the title element, in which case you'll
        likely want to give this element `class = "sidebar-title"`.
    color
        A dictionary with items `"bg"` for background or `"fg"` for foreground color.
    class_
        CSS classes for the sidebar container element, in addition to the fixed
        `.sidebar` class.
    max_height_mobile
        A CSS length unit (passed through :func:`~shiny.ui.css.as_css_unit`) defining
        the maximum height of the horizontal sidebar when viewed on mobile devices. Only
        applies to always-open sidebars on mobile, where by default the sidebar
        container is placed below the main content container on mobile devices.
    gap
        A CSS length unit defining the vertical `gap` (i.e., spacing) between elements
        provided to `*args`.
    padding
        Padding within the sidebar itself. This can be a numeric vector (which will be
        interpreted as pixels) or a character vector with valid CSS lengths. `padding`
        may be one to four values.

        * If a single value, then that value will be used for all four sides.
        * If two, then the first value will be used for the top and bottom, while
          the second value will be used for left and right.
        * If three values, then the first will be used for top, the second will be left
          and right, and the third will be bottom.
        * If four, then the values will be interpreted as top, right, bottom, and left
          respectively.

    Parameters
    ----------
    children
        A tuple of :class:`~htmltools.Tag` objects that are the contents of the sidebar.
    attrs
        A dictionary of attributes that are supplied to the sidebar contents
        :class:`~htmltools.Tag` container.
    width
        A valid CSS unit used for the width of the sidebar.
    position
        Where the sidebar should appear relative to the main content, one of `"left"` or
        `"right"`.
    open
        The initial state of the sidebar. If a string, the possible values are:

        * `"open"`: the sidebar starts open
        * `"closed"`: the sidebar starts closed
        * `"always"`: the sidebar is always open and cannot be closed

        Alternatively, you can provide a dictionary with keys `"desktop"` and `"mobile"`
        to set different initial states for desktop and mobile. For example, when
        `{"desktop": "open", "mobile": "closed"}` the sidebar is initialized in the
        open state on desktop screens or in the closed state on mobile screens.
    id
        A character string. Required if wanting to reactively read (or update) the
        `collapsible` state in a Shiny app.
    title
        A character title to be used as the sidebar title, which will be wrapped in a
        `<div>` element with class `sidebar-title`. You can also provide a custom
        :class:`~htmltools.Tag` for the title element, in which case you'll
        likely want to give this element `class = "sidebar-title"`.
    bg,fg
        A background or foreground color.
    class_
        CSS classes for the sidebar container element, in addition to the fixed
        `.sidebar` class.
    max_height_mobile
        A CSS length unit (passed through :func:`~shiny.ui.css.as_css_unit`) defining
        the maximum height of the horizontal sidebar when viewed on mobile devices. Only
        applies to always-open sidebars on mobile, where by default the sidebar
        container is placed below the main content container on mobile devices.
    gap
        A CSS length unit defining the vertical `gap` (i.e., spacing) between elements
        provided to `*args`.
    padding
        Padding within the sidebar itself. This can be a numeric vector (which will be
        interpreted as pixels) or a character vector with valid CSS lengths. `padding`
        may be one to four values.

        * If a single value, then that value will be used for all four sides.
        * If two, then the first value will be used for the top and bottom, while
          the second value will be used for left and right.
        * If three values, then the first will be used for top, the second will be left
          and right, and the third will be bottom.
        * If four, then the values will be interpreted as top, right, bottom, and left
          respectively.
    """

    def __init__(
        self,
        *,
        children: list[TagChild],
        attrs: TagAttrs,
        position: Literal["left", "right"] = "left",
        open: Optional[SidebarOpenSpec | SidebarOpenValue | Literal["desktop"]] = None,
        width: CssUnit = 250,
        id: Optional[str] = None,
        title: TagChild | str = None,
        fg: Optional[str] = None,
        bg: Optional[str] = None,
        class_: Optional[str] = None,
        max_height_mobile: Optional[str | float] = None,
        gap: Optional[CssUnit] = None,
        padding: Optional[CssUnit | list[CssUnit]] = None,
    ):
        if isinstance(title, (str, int, float)):
            title = tags.header(str(title), class_="sidebar-title")

        self.id: ResolvedId | None = resolve_id_or_none(id)
        self.title = title
        self.class_ = class_
        self.gap = as_css_unit(gap)
        self.padding = as_css_padding(padding)
        # User-provided initial open state
        self._open: SidebarOpen | None = self._as_open(open)
        # Shiny or consumer-provided default open state, change with `_set_default_open()`
        self._default_open = SidebarOpen(desktop="open", mobile="closed")
        self.position = position
        self.width = as_css_unit(width)
        self._max_height_mobile = max_height_mobile
        self.color = {"fg": fg, "bg": bg}
        self.attrs = attrs
        self.children = children

    def open(
        self,
        value: (
            SidebarOpen
            | SidebarOpenSpec
            | SidebarOpenValue
            | Literal["desktop"]
            | None
            | MISSING_TYPE
        ) = MISSING,
    ) -> SidebarOpen:
        """
        Get or set the initial state of the sidebar. Returns a dataclass with `desktop`
        and `mobile` attributes.
        """
        if not isinstance(value, MISSING_TYPE):
            self._open = self._as_open(value)

        if self._open is None:
            return self._default_open
        else:
            return self._open

    @property
    def max_height_mobile(self) -> Optional[str]:
        max_height_mobile = self._max_height_mobile

        if max_height_mobile is not None and self.open().mobile != "always":
            warnings.warn(
                "The `shiny.ui.sidebar(max_height_mobile=)` argument only applies to "
                + "the sidebar when `open` is `'always'` on mobile, but "
                + f"`open` is `'{self.open().mobile}'`. "
                + "The `max_height_mobile` argument will be ignored.",
                # `stacklevel=2`: Refers to the caller of `.max_height_mobile` property method
                stacklevel=2,
            )
            max_height_mobile = None

        return as_css_unit(max_height_mobile)

    @max_height_mobile.setter
    def max_height_mobile(self, max_height_mobile: str | float | None) -> None:
        self._max_height_mobile = max_height_mobile

    def _as_open(
        self,
        open: Optional[
            SidebarOpen | SidebarOpenSpec | SidebarOpenValue | Literal["desktop"]
        ] = None,
    ) -> SidebarOpen | None:
        if open is None:
            return None

        if isinstance(open, SidebarOpen):
            return open

        return SidebarOpen._as_open(open)

    def _get_sidebar_id(self) -> Optional[str]:
        """
        Returns the resolved ID of the sidebar, or `None` if the sidebar is always open.
        When the sidebar is collapsible, but the user hasn't provided an ID, a random ID
        is generated and returned.
        """
        if isinstance(self.id, ResolvedId):
            return self.id

        if self.open().desktop == "always" and self.open().mobile == "always":
            return None

        return private_random_id("bslib_sidebar")

    def _collapse_tag(self, id: str | None) -> Tag:
        """Create the <button> tag for the collapse button."""
        is_expanded = self.open().desktop == "open" or self.open().mobile == "open"
        is_always = self.open() == SidebarOpen(desktop="always", mobile="always")

        return tags.button(
            _collapse_icon(),
            class_="collapse-toggle",
            type="button",
            title="Toggle sidebar",
            aria_expanded=(
                ("true" if is_expanded else "false") if not is_always else None
            ),
            aria_controls=id if not is_always else None,
        )

    def _sidebar_tag(self, id: str | None) -> Tag:
        """Create the `<aside>` tag for the sidebar."""
        is_hidden_initially = (
            self.open().desktop == "closed" or self.open().mobile == "closed"
        )

        return tags.aside(
            {
                "id": id,
                "class": "sidebar",
                "hidden": "true" if is_hidden_initially else None,
            },
            # If the user provided an id, we make the sidebar an input to report state
            {"class": "bslib-sidebar-input"} if self.id is not None else None,
            div(
                {
                    "class": "sidebar-content bslib-gap-spacing",
                    "style": css(
                        gap=self.gap,
                        padding=self.padding,
                    ),
                },
                self.title,
                *self.children,
                self.attrs,
            ),
            class_=self.class_,
        )

    def tagify(self) -> TagList:
        id = self._get_sidebar_id()
        taglist = TagList(self._sidebar_tag(id), self._collapse_tag(id))
        return taglist.tagify()


@add_example()
def sidebar(
    *args: TagChild | TagAttrs,
    position: Literal["left", "right"] = "left",
    open: Optional[SidebarOpenSpec | SidebarOpenValue | Literal["desktop"]] = None,
    width: CssUnit = 250,
    id: Optional[str] = None,
    title: TagChild | str = None,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    class_: Optional[str] = None,
    max_height_mobile: Optional[str | float] = None,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    **kwargs: TagAttrValue,
) -> Sidebar:
    # See [this article](https://rstudio.github.io/bslib/articles/sidebars.html)
    #   to learn more.
    # TODO-future; If color contrast is implemented. Docs for `bg` and `fg`:
    #     If only one of either is provided, an
    #     accessible contrasting color is provided for the opposite color, e.g. setting
    #     `bg` chooses an appropriate `fg` color.

    """
    Sidebar element

    Create a collapsing sidebar layout by providing a `sidebar()` object to the
    `sidebar=` argument of:

    * :func:`~shiny.ui.layout_sidebar`
      * Creates a sidebar layout component which can be dropped inside any Shiny UI page method (e.g. :func:`~shiny.ui.page_fillable`) or :func:`~shiny.ui.card` context.
    * :func:`~shiny.ui.navset_bar`, :func:`~shiny.ui.navset_card_tab`, and :func:`~shiny.ui.navset_card_pill`
      * Creates a multi page/tab UI with a singular `sidebar()` (which is
        shown on every page/tab).

    Parameters
    ----------
    *args
        Contents of the sidebar. Or tag attributes that are supplied to the
        resolved :class:`~htmltools.Tag` object.
    width
        A valid CSS unit used for the width of the sidebar.
    position
        Where the sidebar should appear relative to the main content, one of `"left"` or
        `"right"`.
    open
        The initial state of the sidebar. If a string, the possible values are:

        * `"open"`: the sidebar starts open
        * `"closed"`: the sidebar starts closed
        * `"always"`: the sidebar is always open and cannot be closed

        Alternatively, you can provide a dictionary with keys `"desktop"` and `"mobile"`
        to set different initial states for desktop and mobile. For example, when
        `{"desktop": "open", "mobile": "closed"}` the sidebar is initialized in the
        open state on desktop screens or in the closed state on mobile screens.
    id
        A character string. Required if wanting to reactively read (or update) the
        `collapsible` state in a Shiny app.
    title
        A character title to be used as the sidebar title, which will be wrapped in a
        `<div>` element with class `sidebar-title`. You can also provide a custom
        :class:`~htmltools.Tag` for the title element, in which case you'll
        likely want to give this element `class = "sidebar-title"`.
    bg,fg
        A background or foreground color.
    class_
        CSS classes for the sidebar container element, in addition to the fixed
        `.sidebar` class.
    max_height_mobile
        A CSS length unit (passed through :func:`~shiny.ui.css.as_css_unit`) defining
        the maximum height of the horizontal sidebar when viewed on mobile devices. Only
        applies to always-open sidebars on mobile, where by default the sidebar
        container is placed below the main content container on mobile devices.
    gap
        A CSS length unit defining the vertical `gap` (i.e., spacing) between elements
        provided to `*args`.
    padding
        Padding within the sidebar itself. This can be a numeric vector (which will be
        interpreted as pixels) or a character vector with valid CSS lengths. `padding`
        may be one to four values.

        * If a single value, then that value will be used for all four sides.
        * If two, then the first value will be used for the top and bottom, while
          the second value will be used for left and right.
        * If three values, then the first will be used for top, the second will be left
          and right, and the third will be bottom.
        * If four, then the values will be interpreted as top, right, bottom, and left
          respectively.
    **kwargs
        Named attributes are supplied to the sidebar content container.

    Returns
    -------
    :
        A :class:`~shiny.ui.Sidebar` object.

    See Also
    --------
    * :func:`~shiny.ui.layout_sidebar`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    """
    # TODO-future; validate bg, fg, class_

    # TODO-future; implement
    # if fg is None and bg is not None:
    #     fg = get_color_contrast(bg)
    # if bg is None and fg is not None:
    #     bg = get_color_contrast(fg)

    attrs, children = consolidate_attrs(*args, **kwargs)

    return Sidebar(
        children=children,
        attrs=attrs,
        width=width,
        position=position,
        open=open,
        id=id,
        title=title,
        fg=fg,
        bg=bg,
        class_=class_,
        max_height_mobile=max_height_mobile,
        gap=gap,
        padding=padding,
    )


@add_example()
def layout_sidebar(
    sidebar: Sidebar,
    *args: TagChild | TagAttrs,
    fillable: bool = True,
    fill: bool = True,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    border: Optional[bool] = None,
    border_radius: Optional[bool] = None,
    border_color: Optional[str] = None,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
) -> CardItem:
    """
    Sidebar layout

    Create a sidebar layout component which can be dropped inside any Shiny UI page
    method (e.g. :func:`~shiny.ui.page_fillable`) or
    :func:`~shiny.ui.card` context.

    Parameters
    ----------
    *args
        One argument needs to be of class :class:`~shiny.ui.Sidebar` object created by
        :func:`~shiny.ui.sidebar`. The remaining arguments will contain the contents to
        the main content area. Or tag attributes that are supplied to the resolved
        :class:`~htmltools.Tag` object.
    fillable
        Whether or not the main content area should be wrapped in a fillable container.
        See :func:`~shiny.ui.fill.as_fillable_container` for details.
    fill
        Whether or not the sidebar layout should be wrapped in a fillable container. See
        :func:`~shiny.ui.fill.as_fill_item` for details.
    bg,fg
        A background or foreground color.
    border
        Whether or not to show a border around the sidebar layout.
    border_radius
        Whether or not to round the corners of the sidebar layout.
    border_color
        A border color.
    gap
        A CSS length unit defining the vertical `gap` (i.e., spacing) between elements
        provided to `*args`. This value will only be used if `fillable` is `True`.
    padding
        Padding within the sidebar itself. This can be a numeric vector (which will be
        interpreted as pixels) or a character vector with valid CSS lengths. `padding`
        may be one to four values.

        * If a single value, then that value will be used for all four sides.
        * If two, then the first value will be used for the top and bottom, while
          the second value will be used for left and right.
        * If three values, then the first will be used for top, the second will be left
          and right, and the third will be bottom.
        * If four, then the values will be interpreted as top, right, bottom, and left
          respectively.
    height
        Any valid CSS unit to use for the height.

    Returns
    -------
    :
        A :class:`~htmltools.Tag` object.

    See Also
    --------
    * :func:`~shiny.ui.sidebar`
    """

    sidebar, args = _get_layout_sidebar_sidebar(sidebar, args)

    # TODO-future; implement
    # if fg is None and bg is not None:
    #     fg = get_color_contrast(bg)
    # if bg is None and fg is not None:
    #     bg = get_color_contrast(fg)

    attrs, children = consolidate_attrs(*args, **kwargs)
    # TODO-future: >= 2023-11-01); Once `panel_main()` is removed, we can remove this loop
    for child in children:
        if isinstance(child, DeprecatedPanelMain):
            attrs = consolidate_attrs(attrs, child.attrs)[0]
            # child.children will be handled when tagified

    main = div(
        {
            "class": f"main{' bslib-gap-spacing' if fillable else ''}",
            "style": css(
                gap=as_css_unit(gap),
                padding=as_css_padding(padding),
            ),
        },
        attrs,
        *children,
    )
    if fillable:
        main = as_fillable_container(main)

    res = div(
        {"class": "bslib-sidebar-layout bslib-mb-spacing"},
        {"class": "sidebar-right"} if sidebar.position == "right" else None,
        {"class": "sidebar-collapsed"} if sidebar.open().desktop == "closed" else None,
        main,
        sidebar,
        components_dependencies(),
        _sidebar_init_js(),
        data_bslib_sidebar_init="true",
        data_open_desktop=sidebar.open().desktop,
        data_open_mobile=sidebar.open().mobile,
        data_collapsible_mobile=(
            "true" if sidebar.open().mobile != "always" else "false"
        ),
        data_collapsible_desktop=(
            "true" if sidebar.open().desktop != "always" else "false"
        ),
        data_bslib_sidebar_border=trinary(border),
        data_bslib_sidebar_border_radius=trinary(border_radius),
        style=css_no_sub(
            **{
                "--_sidebar-width": sidebar.width,
                "--_sidebar-bg": sidebar.color["bg"],
                "--_sidebar-fg": sidebar.color["fg"],
                "--_main-fg": fg,
                "--_main-bg": bg,
                "--bs-card-border-color": border_color,
                "height": as_css_unit(height),
                "--_mobile-max-height": sidebar.max_height_mobile,
            },
        ),
    )
    if fill:
        res = as_fill_item(res)

    return CardItem(res)


def _get_layout_sidebar_sidebar(
    sidebar: Sidebar,
    args: tuple[TagChild | TagAttrs, ...],
) -> tuple[Sidebar, tuple[TagChild | TagAttrs, ...]]:
    updated_args: list[TagChild | TagAttrs] = []
    original_args = tuple(args)

    # sidebar: Sidebar | None = None
    sidebar_orig_arg: Sidebar | DeprecatedPanelSidebar = sidebar

    if isinstance(sidebar, DeprecatedPanelSidebar):
        sidebar = sidebar.sidebar

    if not isinstance(sidebar, Sidebar):
        raise ValueError(
            "`layout_sidebar()` is not being supplied with a `sidebar()` object. Please supply a `sidebar()` object to `layout_sidebar(sidebar)`."
        )

    # Use `original_args` here so `updated_args` can be safely altered in place
    for i, arg in zip(range(len(original_args)), original_args):
        if isinstance(arg, DeprecatedPanelSidebar):
            raise ValueError(
                "`panel_sidebar()` is not being used as the first argument to `layout_sidebar(sidebar,)`. `panel_sidebar()` has been deprecated and will go away in a future version of Shiny. Please supply `panel_sidebar()` arguments directly to `args` in `layout_sidebar(sidebar)` and use `sidebar()` instead of `panel_sidebar()`."
            )
        elif isinstance(arg, Sidebar):
            raise ValueError(
                "`layout_sidebar()` is being supplied with multiple `sidebar()` objects. Please supply only one `sidebar()` object to `layout_sidebar()`."
            )

        elif isinstance(arg, DeprecatedPanelMain):
            if i != 0:
                raise ValueError(
                    "`panel_main()` is not being supplied as the second argument to `layout_sidebar()`. `panel_main()`/`panel_sidebar()` have been deprecated and will go away in a future version of Shiny. Please supply `panel_main()` arguments directly to `args` in `layout_sidebar(sidebar, *args)` and use `sidebar()` instead of `panel_sidebar()`."
                )
            if not isinstance(sidebar_orig_arg, DeprecatedPanelSidebar):
                raise ValueError(
                    "`panel_main()` is not being used with `panel_sidebar()`. `panel_main()`/`panel_sidebar()` have been deprecated and will go away in a future version of Shiny. Please supply `panel_main()` arguments directly to `args` in `layout_sidebar(sidebar, *args)` and use `sidebar()` instead of `panel_sidebar()`."
                )

            if len(args) > 2:
                raise ValueError(
                    "Unexpected extra legacy `*args` have been supplied to `layout_sidebar()` in addition to `panel_main()` or `panel_sidebar()`. `panel_main()` has been deprecated and will go away in a future version of Shiny. Please supply `panel_main()` arguments directly to `args` in `layout_sidebar(sidebar, *args)` and use `sidebar()` instead of `panel_sidebar()`."
                )
            # Notes for this point in the code:
            # * We are working with args[0], a `DeprecatedPanelMain`; sidebar was originally a `DeprecatedPanelSidebar`
            # * len(args) == 1 or 2

            # Handle legacy `layout_sidebar(sidebar, main, position=)` value
            if len(args) == 2:
                arg1 = args[1]
                if not (arg1 == "left" or arg1 == "right"):
                    raise ValueError(
                        "layout_sidebar(*args) contains non-valid legacy values. Please use `sidebar()` instead of `panel_sidebar()` and supply any `panel_main()` arguments directly to `args` in `layout_sidebar(sidebar, *args)`."
                    )
                # We know `sidebar_orig_arg` is a `DeprecatedPanelSidebar` here
                sidebar.position = cast(  # pyright: ignore[reportOptionalMemberAccess]
                    Literal["left", "right"],
                    arg1,
                )

            # Only keep panel_main content
            updated_args = [arg]

            # Cases have been covered, quit loop
            break

            # Extract `DeprecatedPanelMain` attrs and children in followup for loop
        else:
            # Keep the arg!
            updated_args.append(arg)

    return (sidebar, tuple(updated_args))


@add_example()
def update_sidebar(
    id: str,
    *,
    show: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    """
    Update a sidebar's visibility.

    Set a :func:`~shiny.ui.sidebar` state during an active Shiny user session.

    Parameters
    ----------
    id
        The `id` of the :func:`~shiny.ui.sidebar` to toggle.
    show
        The desired visible state of the sidebar, where `True` opens the sidebar and `False` closes the sidebar (if not already in that state).
    session
        A Shiny session object (the default should almost always be used).

    See Also
    --------
    * :func:`~shiny.ui.sidebar`
    * :func:`~shiny.ui.layout_sidebar`
    """
    session = require_active_session(session)

    # method: Literal["toggle", "open", "close"]
    # if open is None or open == "toggle":
    #     method = "toggle"
    # elif open is True or open == "open":
    #     method = "open"
    # elif open is False or open == "closed":
    #     method = "close"
    # else:
    #     if open == "always" or open == "desktop":
    #         raise ValueError(
    #             f"`open = '{open}'` is not supported by `update_sidebar()`"
    #         )
    #     raise ValueError(
    #         "open must be NULL (or 'toggle'), TRUE (or 'open'), or FALSE (or 'closed')"
    #     )
    if show is not None:
        method = "open" if bool(show) else "close"

        def callback() -> None:
            session.send_input_message(id, {"method": method})

        session.on_flush(callback, once=True)


def _collapse_icon() -> TagChild:
    return HTML(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="bi bi-chevron-left collapse-icon" style="fill:currentColor;" aria-hidden="true" role="img" ><path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"></path></svg>'
    )


def _sidebar_init_js() -> Tag:
    # Note: if we want to avoid inline `<script>` tags in the future for
    # initialization code, we might be able to do so by turning the sidebar layout
    # container into a web component
    return tags.script(
        {"data-bslib-sidebar-init": True},
        "bslib.Sidebar.initCollapsibleAll()",
    )


######################


# Deprecated 2023-06-13
# Includes: DeprecatedPanelSidebar
@no_example()
def panel_sidebar(
    *args: TagChild | TagAttrs,
    width: int = 4,
    **kwargs: TagAttrValue,
) -> DeprecatedPanelSidebar:
    """Deprecated. Please use :func:`~shiny.ui.sidebar` instead."""
    # TODO-future: >= 2024-01-01; Add deprecation message below
    # Plan of action:
    # * No deprecation messages today (2023-10-11), and existing code _just works_.
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
@no_example()
def panel_main(
    *args: TagChild | TagAttrs,
    width: int = 8,
    **kwargs: TagAttrValue,
) -> DeprecatedPanelMain:
    """Deprecated. Please supply the `*args` of :func:`~shiny.ui.panel_main` directly to :func:`~shiny.ui.layout_sidebar`."""
    # TODO-future: >= 2023-11-01; Add deprecation message below
    # warn_deprecated("Please use `layout_sidebar(*args)` instead of `panel_main()`. `panel_main()` will go away in a future version of Shiny.")

    # warn if keys are being ignored
    attrs, children = consolidate_attrs(*args, **kwargs)
    if len(attrs) > 0:
        return DeprecatedPanelMain(attrs=attrs, children=children)
        warn_deprecated(
            "`*args: TagAttrs` or `**kwargs: TagAttrValue` values supplied to `panel_main()` are being ignored. Please supply them directly to `layout_sidebar()`."
        )

    return DeprecatedPanelMain(attrs={}, children=children)


# Deprecated 2023-06-13


# This class should be removed when `panel_sidebar()` is removed
class DeprecatedPanelSidebar(
    # While it doesn't seem right to inherit from `Sidebar`, it's the easiest way to
    # make sure `layout_sidebar(sidebar: Sidebar)` works without mucking up the
    # function signature.
    Sidebar
):
    """
    [Deprecated] Sidebar panel

    Class returned from :func:`~shiny.ui.panel_sidebar`. Please do not
    use this class and instead supply your content to
    :func:`~shiny.ui.layout_sidebar` directly.

    Parameters
    ----------
    *args
        Contents to the sidebar. Or tag attributes that are supplied to the resolved
        :class:`~htmltools.Tag` object.
    width
        An integeger between 1 and 12, inclusive, that determines the width of the
        sidebar. The default is 4.
    **kwargs
        Tag attributes that are supplied to the resolved :class:`~htmltools.Tag` object.

    Attributes
    ----------
    sidebar
        A output from :func:`~shiny.ui.sidebar`.

    See Also
    --------
    * :func:`~shiny.ui.layout_sidebar`
    * :func:`~shiny.ui.sidebar`
    """

    # Store `attrs` for `layout_sidebar()` to retrieve
    sidebar: Sidebar

    def __init__(
        self, *args: TagChild | TagAttrs, width: int = 4, **kwargs: TagAttrValue
    ) -> None:
        self.sidebar = sidebar(
            *args,
            width=f"{int(width / 12 * 100)}%",
            open="always",
            **kwargs,  # pyright: ignore[reportArgumentType]
        )

    # Hopefully this is never used. But wanted to try to be safe
    def tagify(self) -> TagList:
        """
        Tagify the `self.sidebar.tag` and return the result in a TagList
        """
        return TagList(self.sidebar._sidebar_tag(id=None).tagify())


# This class should be removed when `panel_main()` is removed
# Must be `Tagifiable`, so it can fit as a type `TagChild`
class DeprecatedPanelMain:
    """
    [Deprecated] Main panel

    Class returned from :func:`~shiny.ui.panel_main`. Please do not use
    this class and instead supply your content to
    :func:`~shiny.ui.layout_sidebar` directly.


    Parameters
    ----------
    attrs
        Attributes to apply to the parent tag of the children.
    children
        Children UI Elements to render inside the parent tag.

    Attributes
    ----------
    attrs
        Attributes to apply to the parent tag of the children.
    children
        Children UI Elements to render inside the parent tag.

    See Also
    --------
    * :func:`~shiny.ui.layout_sidebar`
    * :func:`~shiny.ui.sidebar`
    """

    # Store `attrs` for `layout_sidebar()` to retrieve
    attrs: TagAttrs
    # Return `children` in `layout_sidebar()` via `.tagify()` method
    children: list[TagChild]

    def __init__(self, *, attrs: TagAttrs, children: list[TagChild]) -> None:
        self.attrs = attrs
        self.children = children

    def tagify(self) -> TagList:
        """
        Tagify the `children` and return the result in a TagList
        """
        return TagList(self.children).tagify()
