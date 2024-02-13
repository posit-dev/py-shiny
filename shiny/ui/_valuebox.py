from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from htmltools import (
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagFunction,
    Tagifiable,
    css,
    tags,
)

from .._docstring import add_example, no_example
from ._card import CardItem, card, card_body
from ._tag import consolidate_attrs
from ._utils import css_no_sub
from .css import as_css_unit
from .css._css_unit import CssUnit, as_grid_unit
from .fill import as_fill_item, as_fillable_container

__all__ = (
    "value_box",
    "showcase_left_center",
    "showcase_top_right",
    "showcase_bottom",
    "value_box_theme",
    "ValueBoxTheme",
    "ShowcaseLayout",
)

# TODO-future; Better documentation to bslib's value box and theme;
# Related: https://rstudio.github.io/bslib/reference/value_box.html#themes,
# Related: https://github.com/rstudio/bslib/pull/758/files

# Define literal types
SHOWCASE_LAYOUTS_STR = Literal["left center", "top right", "bottom"]
SHOWCASE_LAYOUTS_VALS = ("left center", "top right", "bottom")


@dataclass
class ShowcaseLayout:
    """
    Showcase layout

    Base layout information utilized to display :func:`~shiny.ui.value_box`'s `showcase` value.

    See Also
    --------
    * :func:`~shiny.ui.showcase_left_center`
    * :func:`~shiny.ui.showcase_top_right`
    * :func:`~shiny.ui.showcase_bottom`
    * :func:`~shiny.ui.value_box`
    """

    class_: str
    """CSS class to set on the layout"""
    width: CssUnit | None
    """Width of the showcase area"""
    width_full_screen: CssUnit | None
    """Width of the showcase area when the value box is full screen"""
    height: CssUnit | None
    """Height of the showcase area"""
    height_full_screen: CssUnit | None
    """Height of the showcase area when the value box is full screen"""
    max_height: CssUnit | None
    """Maximum height of the showcase area"""
    max_height_full_screen: CssUnit | None
    """Maximum height of the showcase area when the value box is full screen"""

    def __init__(
        self,
        *,
        class_: str,
        width: CssUnit | None = "33%",
        width_full_screen: CssUnit | None = "1fr",
        height: CssUnit | None = None,
        height_full_screen: CssUnit | None = None,
        max_height: CssUnit | None = "100px",
        max_height_full_screen: CssUnit | None = "67%",
    ) -> None:
        self.class_ = class_
        self.width = as_grid_unit(width)
        self.width_full_screen = as_grid_unit(width_full_screen)
        self.height = as_grid_unit(height)
        self.height_full_screen = as_grid_unit(height_full_screen)
        self.max_height = as_css_unit(max_height)
        self.max_height_full_screen = as_css_unit(max_height_full_screen)


@add_example()
def showcase_left_center(
    *,
    width: CssUnit = "30%",
    width_full_screen: CssUnit | None = "1fr",
    max_height: CssUnit | None = "100px",
    max_height_full_screen: CssUnit | None = "67%",
) -> ShowcaseLayout:
    """
    Showcase left center

    A :func:`~shiny.ui.showcase_left_center` is a `ShowcaseLayout` with
    the following default properties:

    * `width` is `"30%"`
    * `width_full_screen` is `"1fr"`
    * `max_height` is `"100px"`
    * `max_height_full_screen` is `"67%"`

    See Also
    --------
    * :func:`~shiny.ui.showcase_top_right`
    * :func:`~shiny.ui.showcase_bottom`
    * :func:`~shiny.ui.value_box`
    """
    return ShowcaseLayout(
        class_="showcase-left-center",
        width=width,
        width_full_screen=width_full_screen,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
    )


@add_example()
def showcase_top_right(
    *,
    width: CssUnit = "40%",
    width_full_screen: CssUnit | None = "1fr",
    max_height: CssUnit | None = "75px",
    max_height_full_screen: CssUnit | None = "67%",
) -> ShowcaseLayout:
    """
    Showcase top right

    A :func:`~shiny.ui.showcase_top_right` is a `ShowcaseLayout` with
    the following default properties:

    * `width` is `"40%"`
    * `width_full_screen` is `"1fr"`
    * `max_height` is `"75px"`
    * `max_height_full_screen` is `"67%"`

    See Also
    --------
    * :func:`~shiny.ui.showcase_left_center`
    * :func:`~shiny.ui.showcase_bottom`
    * :func:`~shiny.ui.value_box`
    """

    return ShowcaseLayout(
        class_="showcase-top-right",
        width=width,
        width_full_screen=width_full_screen,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
    )


@add_example()
def showcase_bottom(
    *,
    width: CssUnit = "100%",
    width_full_screen: CssUnit | None = None,
    height: CssUnit | None = "auto",
    height_full_screen: CssUnit | None = "2fr",
    max_height: CssUnit | None = "100px",
    max_height_full_screen: CssUnit | None = None,
) -> ShowcaseLayout:
    """
    Showcase bottom

    A :func:`~shiny.ui.showcase_bottom` is a `ShowcaseLayout` with
    the following default properties:

    * `width` is `"100%"`
    * `width_full_screen` is `None`
    * `height` is `"auto"`
    * `height_full_screen` is `"2fr"`
    * `max_height` is `"100px"`
    * `max_height_full_screen` is `None`

    See Also
    --------
    * :func:`~shiny.ui.showcase_left_center`
    * :func:`~shiny.ui.showcase_top_right`
    * :func:`~shiny.ui.value_box`
    """

    return ShowcaseLayout(
        class_="showcase-bottom",
        width=width,
        width_full_screen=width_full_screen,
        height=height,
        height_full_screen=height_full_screen,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
    )


def resolve_showcase_layout(
    showcase_layout: SHOWCASE_LAYOUTS_STR | ShowcaseLayout,
) -> ShowcaseLayout:
    if isinstance(showcase_layout, ShowcaseLayout):
        return showcase_layout

    if showcase_layout == "left center":
        return showcase_left_center()
    elif showcase_layout == "top right":
        return showcase_top_right()
    elif showcase_layout == "bottom":
        return showcase_bottom()
    else:
        showcase_layouts = "'" + "', '".join(SHOWCASE_LAYOUTS_VALS) + "'"
        raise ValueError(
            f"`showcase_layout` must be one of {showcase_layouts} or inherit from `ShowcaseLayout`"
        )


@dataclass
class ValueBoxTheme:
    class_: str | None
    fg: str | None
    bg: str | None


@no_example()
def value_box_theme(
    name: Optional[str] = None,
    *,
    fg: Optional[str] = None,
    bg: Optional[str] = None,
) -> ValueBoxTheme:
    """
    Value box theme

    A theme for a :func:`~shiny.ui.value_box`. Themes provide a convenient way to use
    your app's Bootstrap theme colors as the foreground or background colors of the
    value box. For more control, you can create your own theme with
    :func:`~shiny.ui.value_box_theme` where you can pass foreground and background
    value.

    See
    [rstudio/bslib#themes](https://rstudio.github.io/bslib/reference/value_box.html#themes)
    for more examples.


    Parameters
    ---------
    name
        The name of the theme, e.g. `"primary"`, `"danger"`, `"purple"`.  `name` can
        also be a Bootstrap-supported color: `"blue"`, `"purple"`, `"pink"`, `"red"`,
        `"orange"`, `"yellow"`, `"green"`, `"teal"`, and `"cyan"`. These colors can be
        used with `bg-NAME`, `text-NAME`, and `bg-gradient-NAME1-NAME2`. If a `name`
        does not start with `text-` or `bg-`, it will be auto-prefixed with `bg-`.
    fg,bg
        The background and foreground colors for the theme.

    Returns
    -------
    :
        A `ValueBoxTheme`

    See Also
    --------
    * :func:`~shiny.ui.value_box`
    """
    # bg
    #     If only `bg` is provided,
    #     then the foreground color is automatically chosen from `$black` or `$white` to
    #     provide the best contrast with the background color.
    if name is None:
        if bg is None:
            name = "default"
        else:
            # TODO-future; color contrast
            # # Don't warn if we can't get a contrast color, `bg` might be valid
            # # CSS but not something sass can compute on
            # if fg is None:
            #     fg = get_contrast_color(bg, warn=False)
            ...
        return ValueBoxTheme(class_=name, bg=bg, fg=fg)

    if not isinstance(name, str):
        raise TypeError(
            """`value_box_theme(theme=)` should be a single string, """
            """e.g. `"primary"`, `"danger"`, `"purple"`, etc."""
        )

    if not (name.startswith("bg-") or name.startswith("text-")):
        name = "bg-" + name

    return ValueBoxTheme(class_=name, bg=bg, fg=fg)


@add_example()
def value_box(
    title: TagChild,
    value: TagChild,
    *args: TagChild | TagAttrs,
    showcase: Optional[TagChild] = None,
    showcase_layout: SHOWCASE_LAYOUTS_STR | ShowcaseLayout = "left center",
    full_screen: bool = False,
    theme: Optional[str | ValueBoxTheme] = None,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Value box

    An opinionated (:func:`~shiny.ui.card`-powered) box, designed for
    displaying a `value` and `title`. Optionally, a `showcase` can provide context
    for what the `value` represents (for example, it could hold an icon, or even a
    :func:`~shiny.ui.output_plot`).

    Parameters
    ----------
    title,value
        A string, number, or :class:`~htmltools.Tag` child to display as
        the title or value of the value box. The `title` appears above the `value`.
    *args
        Unnamed arguments may be any :class:`~htmltools.Tag` children to display below
        `value`. Named arguments are passed to :func:`~shiny.ui.card` as
        element attributes.
    showcase
        A :class:`~htmltools.Tag` child to showcase (e.g., an icon, a
        :func:`~shiny.ui.output_plot`, etc).
    showcase_layout
        One of `"left center"` (default), `"top right"` or `"bottom"`. Alternatively,
        you can customize the showcase layout options with the
        :func:`~shiny.ui.showcase_left_center`, :func:`~shiny.ui.showcase_top_right`,
        or :func:`~shiny.ui.showcase_bottom` functions. Use the options functions when
        you want to control the height or width of the showcase area.
    theme
        The name of a theme (e.g. `"primary"`, `"danger"`, `"purple"`, `"bg-green"`,
        `"text-red"`) for the value box, or a theme constructed with
        :func:`~shiny.ui.value_box_theme`.

        The theme names provide a convenient way to use your app's Bootstrap theme
        colors as the foreground or background colors of the value box. For more
        control, you can create your own theme with :func:`~shiny.ui.value_box_theme`
        where you can pass foreground and background colors directly.

        Bootstrap supported color themes: `"blue"`, `"purple"`, `"pink"`, `"red"`,
        `"orange"`, `"yellow"`, `"green"`, `"teal"`, and `"cyan"`. These colors can be
        used with `bg-NAME`, `text-NAME`, and `bg-gradient-NAME1-NAME2` to change the
        background, foreground, or use a background gradient respectively.

        If a `theme` string does not start with `text-` or `bg-`, it will be auto
        prefixed with `bg-`.
    full_screen
        If `True`, an icon will appear when hovering over the card body. Clicking the
        icon expands the card to fit viewport size.
    height,max_height
        Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
        `full_screen`.
    fill
        Whether to allow the value box to grow/shrink to fit a fillable container with
        an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    class_
        Utility classes for customizing the appearance of the summary card. Use `bg-*`
        and `text-*` classes (e.g, `"bg-danger"` and `"text-light"`) to customize the
        background/foreground colors.
    **kwargs
        Additional attributes to pass to :func:`~shiny.ui.card`.

    Returns
    -------
    :
        A :func:`~shiny.ui.card`

    See Also
    --------
    * :func:`~shiny.ui.value_box_theme`
    * :func:`~shiny.ui.showcase_bottom`
    * :func:`~shiny.ui.showcase_left_center`
    * :func:`~shiny.ui.showcase_top_right`
    * :func:`~shiny.ui.card`
    """

    # theme
    #     See the **Themes** section for
    #     more details.
    # height,max_height
    #     Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
    #     `full_screen` (in this case, consider setting a `height` in
    #     :func:`~shiny.experimental.ui.card_body`).

    attrs, children = consolidate_attrs(
        *args,
        class_=class_,
        **kwargs,
    )

    # ---- Title and value ----
    if showcase_layout is None:  # pyright: ignore[reportUnnecessaryComparison]
        showcase_layout = SHOWCASE_LAYOUTS_VALS[0]
    if isinstance(title, (str, int, float)):
        title = tags.p(title)
    if isinstance(value, (str, int, float)):
        value = tags.p(value)

    if title is not None:
        title = wrap_in_carrier_tag_with_class("value-box-title", title)
    if value is not None:
        value = wrap_in_carrier_tag_with_class("value-box-value", value)

    # ---- Contents ----
    contents: Tagifiable = wrap_in_carrier_tag_with_class(
        "value-box-area",
        title,
        value,
        *children,
    )

    # ---- Showcase ----
    if showcase is not None:
        showcase_layout = resolve_showcase_layout(showcase_layout)
        contents = render_showcase_layout(
            showcase_layout=showcase_layout,
            showcase=showcase,
            contents=contents,
        )

    if not isinstance(theme, ValueBoxTheme):
        theme = value_box_theme(theme)

    # ---- Layout ----

    return card(
        {
            "class": "bslib-value-box",
            "style": css_no_sub(
                **{
                    "color": theme.fg,
                    "background-color": theme.bg,
                    # These variables are used by the full screen card button
                    "--bslib-color-fg": theme.fg,
                    "--bslib-color-bg": theme.bg,
                },
            ),
        },
        {"class": theme.class_} if theme.class_ else None,
        {"class": class_} if class_ else None,
        (
            {"class": showcase_layout.class_}
            if showcase and isinstance(showcase_layout, ShowcaseLayout)
            else None
        ),
        attrs,
        contents,
        full_screen=full_screen,
        height=height,
        max_height=max_height,
        fill=fill,
    )


def render_showcase_layout(
    # Requiring named args as the typing is possible to mix up
    *,
    showcase_layout: ShowcaseLayout,
    showcase: TagChild,
    contents: Tag,
) -> CardItem:
    showcase = wrap_in_carrier_tag_with_class("value-box-showcase", showcase)

    grid_props = css_no_sub(
        **{
            "--bslib-grid-height": "auto",
            "--bslib-grid-height-mobile": "auto",
            "---bslib-value-box-showcase-w": showcase_layout.width,
            "---bslib-value-box-showcase-w-fs": showcase_layout.width_full_screen,
            "---bslib-value-box-showcase-h": showcase_layout.height,
            "---bslib-value-box-showcase-h-fs": showcase_layout.height_full_screen,
            "---bslib-value-box-showcase-max-h": showcase_layout.max_height,
            "---bslib-value-box-showcase-max-h-fs": showcase_layout.max_height_full_screen,
        },
    )

    value_box_grid = wrap_in_carrier_tag_with_class(
        "value-box-grid",
        showcase,
        contents,
        fillable=False,
        fill=True,
        style=grid_props,
    )

    return card_body(
        value_box_grid,
        style=css(padding=0),
        fillable=True,
    )


def wrap_in_carrier_tag_with_class(
    class_: str,
    *args: TagChild | TagAttrs,
    tag: TagFunction = tags.div,
    fillable: bool = True,
    fill: bool = True,
    **kwargs: TagAttrValue,
) -> Tag:
    ret = tag({"class": class_}, *args, **kwargs)
    if fill:
        ret = as_fill_item(ret)
    if fillable:
        ret = as_fillable_container(ret)
    return ret
