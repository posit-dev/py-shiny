from __future__ import annotations

__all__ = ("icon",)

import re
import warnings
from typing import Literal, Optional, Union, cast

from htmltools import HTML, Tag, TagAttrValue, css, html_escape, tags

from .._docstring import add_example
from .css._css_unit import CssUnit, as_css_unit

# Type alias for icon sizes
IconSize = Union[
    Literal["2xs", "xs", "sm", "md", "lg", "xl", "2xl"],
    CssUnit,
]

# Semantic size mappings (based on FontAwesome conventions)
_SIZE_MAP = {
    "2xs": "0.625em",
    "xs": "0.75em",
    "sm": "0.875em",
    "md": "1em",
    "lg": "1.25em",
    "xl": "1.5em",
    "2xl": "2em",
}


def _resolve_icon_size(size: Optional[IconSize]) -> Optional[str]:
    """Convert semantic size names to CSS units."""
    if size is None:
        return None
    if isinstance(size, str) and size in _SIZE_MAP:
        return _SIZE_MAP[size]
    return as_css_unit(size)


@add_example()
def icon(
    name: str,
    *,
    lib: Literal["fa", "bs"] = "fa",
    size: Optional[IconSize] = None,
    fill: Optional[str] = None,
    class_: Optional[str] = None,
    id: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create an icon.

    Create an icon from either FontAwesome or Bootstrap Icons libraries. Both icon
    sets are bundled with Shiny and work out of the box.

    Icons are treated as decorative by default (hidden from screen readers). We recommend
    providing accessible labels on the icon's container (e.g., a button with `aria-label`)
    rather than the icon itself. If you need the icon to communicate meaning directly,
    pass `aria_label` via kwargs to make it visible to screen readers.

    Parameters
    ----------
    name
        The name of the icon (e.g., `"gear"`, `"star"`, `"user"`).
    lib
        The icon library to use. Either `"fa"` (FontAwesome) or `"bs"` (Bootstrap
        Icons). Defaults to `"fa"`.
    size
        The size of the icon. Can be a semantic size (`"2xs"`, `"xs"`, `"sm"`, `"md"`,
        `"lg"`, `"xl"`, `"2xl"`) or a CSS unit (e.g., `"2em"`, `"24px"`, `1.5`).
        Semantic sizes:

        - `"2xs"`: 0.625em (10px)
        - `"xs"`: 0.75em (12px)
        - `"sm"`: 0.875em (14px)
        - `"md"`: 1em (16px)
        - `"lg"`: 1.25em (20px)
        - `"xl"`: 1.5em (24px)
        - `"2xl"`: 2em (32px)

    fill
        The icon's fill color. Defaults to `"currentColor"`.
    class_
        Additional CSS classes to apply to the icon.
    id
        HTML id attribute for the SVG element.
    **kwargs
        Additional HTML attributes or SVG styling parameters. Common parameters include:

        - `style`: For FontAwesome icon styles (`"solid"`, `"regular"`, `"brands"`)
        - `fill_opacity`: Icon fill opacity (0-1)
        - `stroke`, `stroke_width`, `stroke_opacity`: SVG stroke properties
        - `margin_left`, `margin_right`, `position`: FontAwesome positioning (advanced)
        - `aria_label`: Make icon visible to screen readers with this label
        - `data-*`: Data attributes for testing or JavaScript interaction
        - Any standard HTML/SVG attributes

    Returns
    -------
    :
        An SVG tag element.

    See Also
    --------
    * :func:`~shiny.ui.input_action_button`
    * :func:`~shiny.ui.value_box`

    Examples
    --------
    ```python
    from shiny import ui

    # FontAwesome icon (default library)
    ui.icon("star")

    # Bootstrap icon
    ui.icon("heart-fill", lib="bs")

    # Icon with semantic size
    ui.icon("gear", size="lg")

    # Icon with custom size and color
    ui.icon("star", size="2em", fill="gold")

    # FontAwesome brand icon (via kwargs)
    ui.icon("github", style="brands")

    # Icon with custom CSS classes
    ui.icon("star", lib="bs", class_="text-warning spin-animation")

    # Icon with data attributes for testing
    ui.icon("gear", lib="bs", data_testid="settings-icon")

    # Icon with accessible label (when icon conveys unique meaning)
    ui.icon("exclamation-triangle", lib="bs", aria_label="Warning")

    # Recommended: Label the container, not the icon
    ui.input_action_button(
        "delete_btn",
        ui.icon("trash", lib="bs"),
        aria_label="Delete item"
    )
    ```
    """
    if lib == "fa":
        return _icon_fa(
            name=name,
            fill=fill,
            size=size,
            class_=class_,
            id=id,
            **kwargs,
        )
    elif lib == "bs":
        return _icon_bs(
            name=name,
            fill=fill,
            size=size,
            class_=class_,
            id=id,
            **kwargs,
        )
    else:
        raise ValueError(f"Unknown icon library: '{lib}'. Use 'fa' or 'bs'.")


_CSS_LENGTH_UNITS = {
    "cm", "mm", "in", "px", "pt", "pc",
    "em", "ex", "ch", "rem",
    "vw", "vh", "vmin", "vmax", "%",
}


def _parse_length_unit(x: Optional[str]) -> Optional[dict[str, object]]:
    """Parse a CSS length string like '2em' into {'value': 2.0, 'unit': 'em'}."""
    if x is None:
        return None
    if not re.search(r"^[0-9]*\.?[0-9]+[a-z%]+$", x):
        raise ValueError(
            "Values provided to `height` and `width` must have a numerical "
            "value followed by a CSS length unit."
        )
    unit = re.sub(r"[0-9.]+?", "", x)
    if unit not in _CSS_LENGTH_UNITS:
        raise ValueError(f"{unit} is not a valid CSS length unit.")
    value = float(re.sub(r"[a-z%]+$", "", x))
    return {"value": value, "unit": unit}


def _icon_fa(
    name: str,
    *,
    fill: Optional[str],
    size: Optional[CssUnit],
    class_: Optional[str],
    id: Optional[str],
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a FontAwesome icon from bundled icon data.

    All icons are decorative by default (aria-hidden="true").
    """
    from ._icon_data import FA_ICONS

    icon_data = FA_ICONS.get(name)
    if icon_data is None:
        raise ValueError(
            f"Unknown FontAwesome icon: '{name}'. "
            f"See https://fontawesome.com/icons for available icons."
        )

    # Extract FA-specific and a11y parameters from kwargs
    style = cast(Optional[str], kwargs.pop("style", None))
    fill_opacity = cast(Optional[str], kwargs.pop("fill_opacity", None))
    stroke = cast(Optional[str], kwargs.pop("stroke", None))
    stroke_width = cast(Optional[str], kwargs.pop("stroke_width", None))
    stroke_opacity = cast(Optional[str], kwargs.pop("stroke_opacity", None))
    margin_left = cast(Optional[str], kwargs.pop("margin_left", None))
    margin_right = cast(Optional[str], kwargs.pop("margin_right", None))
    position = cast(Optional[str], kwargs.pop("position", None))
    title = cast(Optional[str], kwargs.pop("title", None))
    a11y = str(kwargs.pop("a11y", "decorative"))

    # Resolve icon style (solid, regular, brands, etc.)
    styles = icon_data["styles"]
    resolved_style = styles[0] if style is None else style
    if resolved_style not in styles:
        raise ValueError(
            f"Style '{resolved_style}' not found for '{name}' icon. "
            f"Possible styles are: {styles}"
        )

    svg = icon_data["svg"][resolved_style]
    svg_width = float(svg["width"])

    # Convert size to CSS unit (handling semantic sizes)
    resolved_size = _resolve_icon_size(size)
    height = resolved_size
    width = resolved_size

    # Compute aspect-ratio-aware dimensions (matching faicons logic)
    h = _parse_length_unit(height)
    w = _parse_length_unit(width)
    if h is None and w is None:
        height = "1em"
        width = str(round(svg_width / 512, 2)) + "em"
    elif h is not None and w is None:
        width = (
            str(round(svg_width / 512 * cast(float, h["value"]), 2))
            + cast(str, h["unit"])
        )
    elif h is None and w is not None:
        height = (
            str(round(cast(float, w["value"]) / (svg_width / 512), 2))
            + cast(str, w["unit"])
        )

    # Apply defaults.
    # margin_left/margin_right/position defaults match faicons.icon_svg() so that
    # ui.icon() is a drop-in replacement for users migrating from that package.
    if fill is None:
        fill = "currentColor"
    if margin_left is None:
        margin_left = "auto"
    if margin_right is None:
        margin_right = "0.2em"
    if position is None:
        position = "relative"

    # Build SVG attributes
    svg_attrs: dict[str, str] = {"viewBox": f"0 0 {svg['width']} 512"}

    if height is not None and width is not None:
        svg_attrs["preserveAspectRatio"] = "none"

    # Map a11y mode (decorative by default)
    if a11y == "decorative":
        svg_attrs["aria-hidden"] = "true"
        svg_attrs["role"] = "img"
    elif a11y == "semantic":
        label_title = icon_data["label"] if title is None else title
        svg_attrs["aria-label"] = html_escape(label_title, attr=True)
        svg_attrs["role"] = "img"

    # Build the SVG tag
    result = tags.svg(
        None if title is None else tags.title(html_escape(title)),
        Tag("path", d=svg["path"]),
        **svg_attrs,
        class_="fa",
        style=css(
            fill=fill,
            fill_opacity=fill_opacity,
            stroke=stroke,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
            height=height,
            width=width,
            margin_left=margin_left,
            margin_right=margin_right,
            position=position,
            vertical_align="-0.125em",
            overflow="visible",
        ),
    )

    # Apply class_ if provided
    if class_ is not None:
        result.add_class(class_)

    # Apply id if provided
    if id is not None:
        result.attrs["id"] = id

    # Apply remaining kwargs as HTML attributes
    if kwargs:
        result.attrs.update(kwargs)

    return result


def _icon_bs(
    name: str,
    *,
    fill: Optional[str],
    size: Optional[CssUnit],
    class_: Optional[str],
    id: Optional[str],
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a Bootstrap icon from bundled data.

    All icons are decorative by default (aria-hidden="true").
    """
    from ._icon_data import BS_ICONS

    if name not in BS_ICONS:
        raise ValueError(
            f"Unknown Bootstrap icon: '{name}'. "
            f"See https://icons.getbootstrap.com for available icons."
        )

    icon_data = BS_ICONS[name]

    # Extract BS-specific and a11y parameters from kwargs
    style = cast(Optional[str], kwargs.pop("style", None))
    fill_opacity = cast(Optional[str], kwargs.pop("fill_opacity", None))
    stroke = cast(Optional[str], kwargs.pop("stroke", None))
    stroke_width = cast(Optional[str], kwargs.pop("stroke_width", None))
    stroke_opacity = cast(Optional[str], kwargs.pop("stroke_opacity", None))
    title = cast(Optional[str], kwargs.pop("title", None))
    a11y = str(kwargs.pop("a11y", "decorative"))

    # Build inline styles
    styles: list[str] = []

    # Apply fill (default to currentColor)
    if fill is not None:
        styles.append(f"fill:{fill}")
    else:
        styles.append("fill:currentColor")

    if fill_opacity is not None:
        styles.append(f"fill-opacity:{fill_opacity}")
    if stroke is not None:
        styles.append(f"stroke:{stroke}")
    if stroke_width is not None:
        styles.append(f"stroke-width:{stroke_width}")
    if stroke_opacity is not None:
        styles.append(f"stroke-opacity:{stroke_opacity}")

    # Convert size to CSS unit (handling semantic sizes)
    css_size = _resolve_icon_size(size)
    if css_size is not None:
        styles.append(f"height:{css_size}")
        styles.append(f"width:{css_size}")

    # Allow additional inline CSS via style parameter
    if style is not None:
        styles.append(style)

    # Build SVG children
    children: list[Tag | str | HTML] = []
    if title:
        children.append(tags.title(title))

    svg_content = icon_data.get("content", "")
    if svg_content:
        children.append(HTML(svg_content))

    # Build accessibility attributes (decorative by default).
    # For semantic mode, derive an accessible name from title if provided, otherwise
    # fall back to the icon name (hyphens replaced with spaces). A bare role="img"
    # with no accessible name is worse than aria-hidden, so we always provide one.
    a11y_attrs: dict[str, str] = {"role": "img"}
    if a11y == "decorative":
        a11y_attrs["aria_hidden"] = "true"
    elif a11y == "semantic":
        if title is not None:
            a11y_attrs["aria-label"] = html_escape(title, attr=True)
        else:
            derived_label = name.replace("-", " ")
            warnings.warn(
                f"ui.icon('{name}', a11y='semantic') has no title. "
                f"Using '{derived_label}' as the accessible label. "
                f"Provide a title for a more descriptive label.",
                stacklevel=3,
            )
            a11y_attrs["aria-label"] = derived_label

    # Build the SVG tag
    svg_tag = tags.svg(
        *children,
        {
            "class": " ".join(["bi", f"bi-{name}"]),
            "style": ";".join(styles),
        },
        xmlns="http://www.w3.org/2000/svg",
        viewBox=icon_data["viewBox"],
        **a11y_attrs,
        **kwargs,  # Apply remaining kwargs as HTML attributes
    )

    # Apply class_ if provided (merges with bi classes)
    if class_ is not None:
        svg_tag.add_class(class_)

    # Apply id if provided
    if id is not None:
        svg_tag.attrs["id"] = id

    return svg_tag
