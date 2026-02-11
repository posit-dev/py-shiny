from __future__ import annotations

__all__ = ("icon",)

from typing import TYPE_CHECKING, Literal, Optional

from htmltools import Tag, TagAttrValue, tags

from .._docstring import add_example
from .css._css_unit import CssUnit, as_css_unit

if TYPE_CHECKING:
    from faicons import icon_svg as _icon_svg


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
        Additional HTML attributes for the SVG element (e.g., ``class_``, ``style``).

    Returns
    -------
    :
        An SVG tag element.

    See Also
    --------
    * :func:`~shiny.ui.input_action_button`
    * :func:`~shiny.ui.value_box`
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
    height = None
    width = None
    if size is not None:
        css_size = as_css_unit(size)
        height = css_size
        width = css_size

    # Map a11y to faicons parameters
    a11y_param = "deco" if a11y == "decorative" else "sem"

    return icon_svg(
        name,
        style=style,
        height=height,
        width=width,
        title=title,
        a11y=a11y_param,
        **kwargs,
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
    children: list[Tag | str] = []
    if title:
        children.append(tags.title(title))

    # Add the SVG content (path data or raw SVG content)
    svg_content = icon_data.get("content", "")
    if svg_content:
        from htmltools import HTML

        children.append(HTML(svg_content))

    return tags.svg(
        *children,
        {"class": " ".join(css_classes), "style": ";".join(styles)},
        xmlns="http://www.w3.org/2000/svg",
        viewBox=icon_data["viewBox"],
        **a11y_attrs,
        **kwargs,
    )
