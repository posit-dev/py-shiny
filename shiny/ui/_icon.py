from __future__ import annotations

__all__ = ("icon",)

from typing import Literal, Optional

from htmltools import Tag, TagAttrValue, tags

from .._docstring import add_example
from .css._css_unit import CssUnit, as_css_unit


@add_example()
def icon(
    name: str,
    *,
    lib: Literal["fa", "bs"] = "fa",
    style: Optional[Literal["solid", "regular", "brands"]] = None,
    size: Optional[CssUnit] = None,
    title: Optional[str] = None,
    a11y: Literal["decorative", "semantic"] = "decorative",
    **kwargs: TagAttrValue,
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
        Icons).
    style
        The FontAwesome icon style. One of ``"solid"`` (default), ``"regular"``, or
        ``"brands"``. Ignored when ``lib="bs"``.
    size
        The size of the icon as a CSS unit (e.g., ``"1em"``, ``"2rem"``, ``24``).
    title
        An accessible title for the icon (required when ``a11y="semantic"``).
    a11y
        Accessibility mode. ``"decorative"`` (default) hides the icon from screen
        readers. ``"semantic"`` makes the icon accessible and requires a title.
    **kwargs
        For FontAwesome icons (``lib="fa"``): Additional parameters passed to
        ``faicons.icon_svg()``, such as ``fill``, ``margin_left``, ``margin_right``,
        and other styling options. Also accepts HTML attributes like ``class_``, ``id``.

        For Bootstrap icons (``lib="bs"``): HTML attributes for the SVG element
        (e.g., ``class_``, ``id``). The ``style`` and ``class_`` attributes will be
        merged with the icon's built-in styles and classes.

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
    ui.icon("warning", title="Warning icon", a11y="semantic")

    # Icon with custom styling
    ui.icon("star", class_="text-warning")
    ```
    """
    if a11y == "semantic" and not title:
        raise ValueError("title is required when a11y='semantic'")

    if lib == "fa":
        return _icon_fa(name, style=style, size=size, title=title, a11y=a11y, **kwargs)
    elif lib == "bs":
        return _icon_bs(name, size=size, title=title, a11y=a11y, **kwargs)
    else:
        raise ValueError(f"Unknown icon library: '{lib}'. Use 'fa' or 'bs'.")


def _icon_fa(
    name: str,
    *,
    style: Optional[str],
    size: Optional[CssUnit],
    title: Optional[str],
    a11y: str,
    **kwargs: TagAttrValue,
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

    # Provide icon_svg defaults for parameters not explicitly overridden in kwargs
    # This ensures icon() behaves like icon_svg() by default
    kwargs.setdefault("fill", "currentColor")
    kwargs.setdefault("margin_left", "auto")
    kwargs.setdefault("margin_right", "0.2em")
    kwargs.setdefault("position", "relative")

    return icon_svg(
        name,
        style=style,
        height=height,
        width=width,
        title=title,
        a11y=a11y_param,
        **kwargs,  # type: ignore[arg-type]
    )


def _icon_bs(
    name: str,
    *,
    size: Optional[CssUnit],
    title: Optional[str],
    a11y: str,
    **kwargs: TagAttrValue,
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

    # Build styles
    styles = ["fill:currentColor"]
    if size is not None:
        css_size = as_css_unit(size)
        styles.append(f"height:{css_size}")
        styles.append(f"width:{css_size}")

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

    # Merge user-provided classes with our icon classes
    user_classes = kwargs.pop("class_", "")
    all_classes = " ".join(css_classes)
    if user_classes:
        all_classes = f"{all_classes} {user_classes}"

    # Merge user-provided styles with our icon styles
    user_style = kwargs.pop("style", "")
    all_styles = ";".join(styles)
    if user_style:
        all_styles = f"{all_styles};{user_style}"

    return tags.svg(
        *children,
        {"class": all_classes, "style": all_styles},
        xmlns="http://www.w3.org/2000/svg",
        viewBox=icon_data["viewBox"],
        **a11y_attrs,
        **kwargs,
    )
