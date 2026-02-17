from __future__ import annotations

__all__ = ("icon",)

from typing import Literal, Optional

from htmltools import Tag, tags

from .._docstring import add_example
from .css._css_unit import CssUnit, as_css_unit


@add_example()
def icon(
    name: str,
    *,
    lib: Literal["fa", "bs"] = "fa",
    style: Optional[Literal["solid", "regular", "brands"]] = None,
    fill: Optional[str] = None,
    fill_opacity: Optional[str] = None,
    stroke: Optional[str] = None,
    stroke_width: Optional[str] = None,
    stroke_opacity: Optional[str] = None,
    size: Optional[CssUnit] = None,
    margin_left: Optional[str] = None,
    margin_right: Optional[str] = None,
    position: Optional[str] = None,
    title: Optional[str] = None,
    a11y: Literal["decorative", "semantic"] = "decorative",
    id: Optional[str] = None,
) -> Tag:
    """
    Create an icon.

    Create an icon from either FontAwesome or Bootstrap Icons libraries. FontAwesome
    icons require the ``faicons`` package to be installed. Bootstrap Icons are bundled
    with Shiny and work out of the box.

    Parameters
    ----------
    name
        The name of the icon (e.g., ``"gear"``, ``"star"``, ``"user"``).
    lib
        The icon library to use. Either ``"fa"`` (FontAwesome) or ``"bs"`` (Bootstrap
        Icons). Defaults to ``"fa"``.
    style
        For FontAwesome icons: The icon style (``"solid"``, ``"regular"``, or ``"brands"``).
        For Bootstrap icons: Additional CSS styles to apply.
    fill
        The icon's fill color. Defaults to ``"currentColor"``.
    fill_opacity
        The icon's fill opacity (0.0 - 1.0).
    stroke
        The icon's stroke color.
    stroke_width
        The icon's stroke width.
    stroke_opacity
        The icon's stroke opacity (0.0 - 1.0).
    size
        The size of the icon as a CSS unit (e.g., ``"1em"``, ``"2rem"``, ``24``).
    margin_left
        The icon's left margin. Defaults to ``"auto"`` for FontAwesome.
        Ignored for Bootstrap icons.
    margin_right
        The icon's right margin. Defaults to ``"0.2em"`` for FontAwesome.
        Ignored for Bootstrap icons.
    position
        The icon's CSS position. Defaults to ``"relative"`` for FontAwesome.
        Ignored for Bootstrap icons.
    title
        An accessible title for the icon (required when ``a11y="semantic"``).
    a11y
        Accessibility mode. ``"decorative"`` (default) hides the icon from screen
        readers. ``"semantic"`` makes the icon accessible and requires a title.
    id
        HTML id attribute for the SVG element.

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

    # FontAwesome icon with specific style
    ui.icon("github", style="brands")

    # Icon with custom size
    ui.icon("gear", size="2em")

    # Semantic icon with title for accessibility
    ui.icon("circle-exclamation", title="Warning icon", a11y="semantic")

    # Icon with custom fill color
    ui.icon("star", fill="gold")

    # Icon with id attribute
    ui.icon("star", id="my-icon")
    ```
    """
    if a11y == "semantic" and not title:
        raise ValueError("title is required when a11y='semantic'")

    if lib == "fa":
        return _icon_fa(
            name=name,
            style=style,
            fill=fill,
            fill_opacity=fill_opacity,
            stroke=stroke,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
            size=size,
            margin_left=margin_left,
            margin_right=margin_right,
            position=position,
            title=title,
            a11y=a11y,
            id=id,
        )
    elif lib == "bs":
        return _icon_bs(
            name=name,
            fill=fill,
            fill_opacity=fill_opacity,
            stroke=stroke,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
            size=size,
            title=title,
            a11y=a11y,
            style=style,
            id=id,
        )
    else:
        raise ValueError(f"Unknown icon library: '{lib}'. Use 'fa' or 'bs'.")


def _icon_fa(
    name: str,
    *,
    style: Optional[str],
    fill: Optional[str],
    fill_opacity: Optional[str],
    stroke: Optional[str],
    stroke_width: Optional[str],
    stroke_opacity: Optional[str],
    size: Optional[CssUnit],
    margin_left: Optional[str],
    margin_right: Optional[str],
    position: Optional[str],
    title: Optional[str],
    a11y: str,
    id: Optional[str],
) -> Tag:
    """Create a FontAwesome icon using the faicons package."""
    try:
        from faicons import icon_svg
    except ImportError:
        raise ImportError(
            "FontAwesome icons require the 'faicons' package. "
            "Install it with: pip install faicons"
        ) from None

    # Convert size to string for faicons
    height = width = as_css_unit(size) if size is not None else None

    # Map a11y to faicons parameters
    a11y_param = "deco" if a11y == "decorative" else "sem"

    # Provide icon_svg defaults for parameters not explicitly provided
    # This ensures icon() behaves like icon_svg() by default
    if fill is None:
        fill = "currentColor"
    if margin_left is None:
        margin_left = "auto"
    if margin_right is None:
        margin_right = "0.2em"
    if position is None:
        position = "relative"

    result = icon_svg(
        name,
        style=style,
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
        title=title,
        a11y=a11y_param,
    )

    # Apply id attribute if provided
    if id is not None:
        result.attrs["id"] = id

    return result


def _icon_bs(
    name: str,
    *,
    fill: Optional[str],
    fill_opacity: Optional[str],
    stroke: Optional[str],
    stroke_width: Optional[str],
    stroke_opacity: Optional[str],
    size: Optional[CssUnit],
    title: Optional[str],
    a11y: str,
    style: Optional[str],
    id: Optional[str],
) -> Tag:
    """Create a Bootstrap icon from bundled data."""
    from ._icon_data import BS_ICONS

    if name not in BS_ICONS:
        raise ValueError(
            f"Unknown Bootstrap icon: '{name}'. "
            f"See https://icons.getbootstrap.com for available icons."
        )

    icon_data = BS_ICONS[name]

    # Build CSS classes
    css_classes = ["bi", f"bi-{name}"]

    # Build styles - apply fill, stroke, etc. as CSS properties
    styles: list[str] = []

    # Apply fill (default to currentColor if not specified)
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

    if size is not None:
        css_size = as_css_unit(size)
        styles.append(f"height:{css_size}")
        styles.append(f"width:{css_size}")

    # For Bootstrap icons, the 'style' parameter can provide additional CSS
    if style is not None:
        styles.append(style)

    # Accessibility attributes
    a11y_attrs: dict[str, str] = {"role": "img"}
    if a11y == "decorative":
        a11y_attrs["aria_hidden"] = "true"

    # Build SVG children
    from htmltools import HTML

    children: list[Tag | str | HTML] = []
    if title:
        children.append(tags.title(title))

    # Add the SVG content (path data or raw SVG content)
    svg_content = icon_data.get("content", "")
    if svg_content:
        children.append(HTML(svg_content))

    # Build the SVG tag
    svg_tag = tags.svg(
        *children,
        {
            "class": " ".join(css_classes),
            "style": ";".join(styles),
        },
        xmlns="http://www.w3.org/2000/svg",
        viewBox=icon_data["viewBox"],
        **a11y_attrs,
    )

    # Add id attribute if provided
    if id is not None:
        svg_tag.attrs["id"] = id

    return svg_tag
