from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Optional

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

from .._docstring import add_example, no_example
from .._namespaces import resolve_id_or_none
from .._typing_extensions import TypedDict
from .._utils import private_random_id
from ..bookmark import restore_input
from ..module import ResolvedId
from ..session import require_active_session
from ..types import MISSING, MISSING_TYPE
from ._card import CardItem
from ._html_deps_shinyverse import components_dependencies
from ._tag import consolidate_attrs, trinary
from ._utils import css_no_sub
from .css import CssUnit, as_css_padding, as_css_unit
from .fill import as_fill_item, as_fillable_container

if TYPE_CHECKING:
    from ..session import Session

__all__ = (
    "Sidebar",
    "SidebarOpen",
    "sidebar",
    "layout_sidebar",
    "update_sidebar",
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
    mobile: SidebarOpenValue | Literal["always-above"]


@dataclass
class SidebarOpen:
    """
    The initial state of the sidebar at `desktop` and `mobile` screen sizes.
    """

    desktop: SidebarOpenValue = "open"
    """The initial state of the sidebar on desktop screen sizes."""

    mobile: SidebarOpenValue | Literal["always-above"] = "closed"
    """The initial state of the sidebar on mobile screen sizes."""

    _VALUES: tuple[SidebarOpenValue, ...] = field(
        default=("open", "closed", "always"),
        repr=False,
        hash=False,
        compare=False,
    )

    _VALUES_MOBILE: tuple[SidebarOpenValue | Literal["always-above"], ...] = field(
        default=("open", "closed", "always", "always-above"),
        repr=False,
        hash=False,
        compare=False,
    )

    def __post_init__(self):
        if self.desktop not in self._VALUES:
            raise ValueError(f"`desktop` must be one of: {self._VALUES}.")
        if self.mobile not in self._VALUES_MOBILE:
            raise ValueError(f"`mobile` must be one of: {self._VALUES_MOBILE}.")

    def _is_always_open(
        self, on: Literal["desktop", "mobile", "both"] = "both"
    ) -> bool:
        desktop = self.desktop == "always"
        mobile = self.mobile in ("always", "always-above")
        switch = {"desktop": desktop, "mobile": mobile, "both": desktop and mobile}
        return switch[on]

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
            f"`open` must be a string matching one of: {SidebarOpen._VALUES}."
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
            f"""`open` must be one of {SidebarOpen._VALUES}, """
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
        open state on desktop screens or in the closed state on mobile screens. You can
        also choose to place an always-open sidebar above the main content on mobile
        devices by setting `open={"mobile": "always-above"}`.
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

        if max_height_mobile is not None and not self.open()._is_always_open("mobile"):
            warnings.warn(
                "The `shiny.ui.sidebar(max_height_mobile=)` argument only applies to "
                + "the sidebar when `open` is 'always' or 'always-above' on mobile, but "
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

    def _is_always_open(
        self, on: Literal["desktop", "mobile", "both"] = "both"
    ) -> bool:
        return self.open()._is_always_open(on)

    def _get_sidebar_id(self) -> Optional[str]:
        """
        Returns the resolved ID of the sidebar, or `None` if the sidebar is always open.
        When the sidebar is collapsible, but the user hasn't provided an ID, a random ID
        is generated and returned.
        """
        if isinstance(self.id, ResolvedId):
            return self.id

        if self._is_always_open():
            return None

        return private_random_id("bslib_sidebar")

    def _collapse_tag(self, id: str | None) -> Tag:
        """Create the <button> tag for the collapse button."""
        is_expanded = self.open().desktop == "open" or self.open().mobile == "open"

        return tags.button(
            _collapse_icon(),
            class_="collapse-toggle",
            type="button",
            title="Toggle sidebar",
            aria_expanded=(
                ("true" if is_expanded else "false")
                if not self._is_always_open()
                else None
            ),
            aria_controls=id if not self._is_always_open() else None,
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

    resolved_id = resolve_id_or_none(id)

    if resolved_id:
        restored_open: bool | None = restore_input(resolved_id)
        if restored_open is not None:
            open = "open" if restored_open else "closed"

    return Sidebar(
        children=children,
        attrs=attrs,
        width=width,
        position=position,
        open=open,
        id=resolved_id,
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

    if sidebar.open().mobile == "always-above":
        contents = (sidebar, main)
    else:
        contents = (main, sidebar)

    res = div(
        {"class": "bslib-sidebar-layout bslib-mb-spacing"},
        {"class": "sidebar-right"} if sidebar.position == "right" else None,
        {"class": "sidebar-collapsed"} if sidebar.open().desktop == "closed" else None,
        *contents,
        components_dependencies(),
        _sidebar_init_js(),
        data_bslib_sidebar_init="true",
        data_open_desktop=sidebar.open().desktop,
        data_open_mobile=sidebar.open().mobile,
        data_collapsible_mobile=(
            "false" if sidebar.open()._is_always_open("mobile") else "true"
        ),
        data_collapsible_desktop=(
            "false" if sidebar.open()._is_always_open("desktop") else "true"
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

    if not isinstance(sidebar, Sidebar):
        raise ValueError(
            "`layout_sidebar()` is not being supplied with a `sidebar()` object. "
            "Please supply a `sidebar()` object to `layout_sidebar(sidebar)`."
        )

    # Use `original_args` here so `updated_args` can be safely altered in place
    for arg in original_args:
        if isinstance(arg, Sidebar):
            raise ValueError(
                "`layout_sidebar()` is being supplied with multiple `sidebar()` objects. "
                "Please supply only one `sidebar()` object to `layout_sidebar()`."
            )

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
