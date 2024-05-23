from __future__ import annotations

__all__ = (
    "output_plot",
    "output_image",
    "output_text",
    "output_code",
    "output_text_verbatim",
    "output_table",
    "output_ui",
)

from typing import Optional

from htmltools import Tag, TagAttrValue, TagFunction, css, div, tags

from .._docstring import add_example, no_example
from .._namespaces import resolve_id
from ..types import MISSING, MISSING_TYPE
from ._plot_output_opts import (
    BrushOpts,
    ClickOpts,
    DblClickOpts,
    HoverOpts,
    brush_opts,
    click_opts,
    dblclick_opts,
    format_opt_names,
    hover_opts,
)
from .fill import as_fill_item, as_fillable_container


@add_example()
def output_plot(
    id: str,
    width: str | float | int = "100%",
    height: str | float | int = "400px",
    *,
    inline: bool = False,
    click: bool | ClickOpts = False,
    dblclick: bool | DblClickOpts = False,
    hover: bool | HoverOpts = False,
    brush: bool | BrushOpts = False,
    fill: bool | MISSING_TYPE = MISSING,
) -> Tag:
    """
    Create a output container for a static plot.

    Place a :class:`~shiny.render.plot` result in the user interface. See
    :class:`~shiny.render.plot` for more details on what types of plots are supported.

    Parameters
    ----------
    id
        An output id.
    width
        The CSS width, e.g. '400px', or '100%'.
    height
        The CSS height, e.g. '100%' or '600px'.
    inline
        If ``True``, the result is displayed inline.
    click
        This can be a boolean or an object created by :func:`~shiny.ui.click_opts`. The
        default is `False`, but if you use `True` (or equivalently, `click_opts()`), the
        plot will send coordinates to the server whenever it is clicked, and the value
        will be accessible via `input.xx_click()`, where `xx` is replaced with the ID of
        this plot. The input value will be a dictionary with `x` and `y` elements
        indicating the mouse position.
    dblclick
        This is just like the `click` parameter, but for double-click events.
    hover
        Similar to the `click` argument, this can be a boolean or an object created by
        :func:`~shiny.ui.hover_opts`. The default is `False`, but if you use `True` (or
        equivalently, `hover_opts()`), the plot will send coordinates to the server
        whenever it is clicked, and the value will be accessible via `input.xx_hover()`,
        where `xx` is replaced with the ID of this plot. The input value will be a
        dictionary with `x` and `y` elements indicating the mouse position. To control
        the hover time or hover delay type, use :func:`~shiny.ui.hover_opts`.
    brush
        Similar to the `click` argument, this can be a boolean or an object created by
        :func:`~shiny.ui.brush_opts`. The default is `False`, but if you use `True` (or
        equivalently, `brush_opts()`), the plot will allow the user to "brush" in the
        plotting area, and will send information about the brushed area to the server,
        and the value will be accessible via `input.plot_brush()`. Brushing means that
        the user will be able to draw a rectangle in the plotting area and drag it
        around. The value will be a named list with `xmin`, `xmax`, `ymin`, and `ymax`
        elements indicating the brush area. To control the brush behavior, use
        :func:`~shiny.ui.brush_opts`. Multiple `output_image`/`output_plot` calls may
        share the same `id` value; brushing one image or plot will cause any other
        brushes with the same `id` to disappear.
    fill
        Whether or not to allow the plot output to grow/shrink to fit a fillable
        container with an opinionated height (e.g., :func:`~shiny.ui.page_fillable`). If
        no `fill` value is provided, it will default to the inverse of `inline`.

    Returns
    -------
    :
        A UI element

    See Also
    --------
    * :class:`~shiny.render.plot`
    * :func:`~shiny.ui.output_image`
    """
    if isinstance(fill, MISSING_TYPE):
        fill = not inline
    res = output_image(
        id=id,
        width=width,
        height=height,
        inline=inline,
        click=click,
        dblclick=dblclick,
        hover=hover,
        brush=brush,
        fill=fill,
    )
    res.add_class("shiny-plot-output")
    return res


@add_example()
def output_image(
    id: str,
    width: str | float | int = "100%",
    height: str | float | int = "400px",
    *,
    inline: bool = False,
    click: bool | ClickOpts = False,
    dblclick: bool | DblClickOpts = False,
    hover: bool | HoverOpts = False,
    brush: bool | BrushOpts = False,
    fill: bool = False,
) -> Tag:
    """
    Create a output container for a static image.

    Parameters
    ----------
    id
        An output id.
    width
        The CSS width, e.g. '400px', or '100%'.
    height
        The CSS height, e.g. '100%' or '600px'.
    inline
        If ``True``, the result is displayed inline.
    click
        This can be a boolean or an object created by :func:`~shiny.ui.click_opts`. The
        default is `False`, but if you use `True` (or equivalently, `click_opts()`), the
        plot will send coordinates to the server whenever it is clicked, and the value
        will be accessible via `input.xx_click()`, where `xx` is replaced with the ID of
        this plot. The input value will be a dictionary with `x` and `y` elements
        indicating the mouse position.
    dblclick
        This is just like the `click` parameter, but for double-click events.
    hover
        Similar to the `click` argument, this can be a boolean or an object created by
        :func:`~shiny.ui.hover_opts`. The default is `False`, but if you use `True` (or
        equivalently, `hover_opts()`), the plot will send coordinates to the server
        whenever it is clicked, and the value will be accessible via `input.xx_hover()`,
        where `xx` is replaced with the ID of this plot. The input value will be a
        dictionary with `x` and `y` elements indicating the mouse position. To control
        the hover time or hover delay type, use :func:`~shiny.ui.hover_opts`.
    brush
        Similar to the `click` argument, this can be a boolean or an object created by
        :func:`~shiny.ui.brush_opts`. The default is `False`, but if you use `True` (or
        equivalently, `brush_opts()`), the plot will allow the user to "brush" in the
        plotting area, and will send information about the brushed area to the server,
        and the value will be accessible via `input.plot_brush()`. Brushing means that
        the user will be able to draw a rectangle in the plotting area and drag it
        around. The value will be a named list with `xmin`, `xmax`, `ymin`, and `ymax`
        elements indicating the brush area. To control the brush behavior, use
        :func:`~shiny.ui.brush_opts`. Multiple `output_image`/`output_plot` calls may
        share the same `id` value; brushing one image or plot will cause any other
        brushes with the same `id` to disappear.
    fill
        Whether or not to allow the image output to grow/shrink to fit a fillable
        container with an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).

    Returns
    -------
    :
        A UI element

    See Also
    --------
    * :class:`~shiny.render.image`
    * :func:`~shiny.ui.output_plot`
    """
    func = tags.span if inline else div
    width = f"{width}px" if isinstance(width, (float, int)) else width
    height = f"{height}px" if isinstance(height, (float, int)) else height
    style = None if inline else css(width=width, height=height)

    args: dict[str, str] = dict()

    id_resolved = resolve_id(id)

    if click is not False:
        if click is True:
            click = click_opts()
        click["id"] = id_resolved + "_click"
        args.update(**format_opt_names(click, "click"))

    if dblclick is not False:
        if dblclick is True:
            dblclick = dblclick_opts()
        dblclick["id"] = id_resolved + "_dblclick"
        args.update(**format_opt_names(dblclick, "dblclick"))

    if hover is not False:
        if hover is True:
            hover = hover_opts()
        hover["id"] = id_resolved + "_hover"
        args.update(**format_opt_names(hover, "hover"))

    if brush is not False:
        if brush is True:
            brush = brush_opts()
        brush["id"] = id_resolved + "_brush"
        args.update(**format_opt_names(brush, "brush"))

    container = func(
        id=id_resolved,
        class_="shiny-image-output",
        style=style,
        **args,
    )
    if fill:
        container = as_fill_item(container)

    return container


@add_example()
def output_text(
    id: str, inline: bool = False, container: Optional[TagFunction] = None
) -> Tag:
    """
    Create a output container for some text.

    Parameters
    ----------
    id
        An output id.
    inline
        If ``True``, the result is displayed inline.
    container
        A Callable that returns the output container.

    Returns
    -------
    :
        A UI element

    Note
    ----
    Text is HTML-escaped prior to rendering.

    See Also
    --------
    * :class:`~shiny.render.text`
    * :func:`~shiny.ui.output_text_verbatim`
    """

    if not container:
        container = tags.span if inline else tags.div
    return container(id=resolve_id(id), class_="shiny-text-output")


@no_example()
def output_code(id: str, placeholder: bool = True) -> Tag:
    """
    Create a output container for code (monospaced text).

    This is similar to :func:`~shiny.ui.output_text`, except that it displays the text
    in a fixed-width container with a gray-ish background color and border.

    Parameters
    ----------
    id
        An output id.
    placeholder
        If the output is empty or ``None``, should an empty rectangle be displayed to
        serve as a placeholder? (This does not affect behavior when the output is
        nonempty.)

    Returns
    -------
    :
        A UI element

    Note
    ----
    This function is currently the same as :func:`~shiny.ui.output_text_verbatim`, but
    this may change in future versions of Shiny.

    See Also
    --------
    * :class:`~shiny.render.text`
    * :func:`~shiny.ui.output_text`
    * :func:`~shiny.ui.output_text_verbatim`

    Example
    -------
    See :func:`~shiny.ui.output_text`
    """

    cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    return tags.pre(id=resolve_id(id), class_=cls)


@add_example(ex_dir="../api-examples/input_text")
def output_text_verbatim(id: str, placeholder: bool = False) -> Tag:
    """
    Create a output container for some text.

    Place a :class:`~shiny.render.text` result in the user interface.
    Differs from :func:`~shiny.ui.output_text` in that it wraps the text in a
    fixed-width container with a gray-ish background color and border.

    Parameters
    ----------
    id
        An output id.
    placeholder
        If the output is empty or ``None``, should an empty rectangle be displayed to
        serve as a placeholder? (This does not affect behavior when the output
        is nonempty.)

    Returns
    -------
    :
        A UI element

    See Also
    --------
    * :class:`~shiny.render.text`
    * :func:`~shiny.ui.output_text`

    Example
    -------
    See :func:`~shiny.ui.output_text`
    """

    cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    return tags.pre(id=resolve_id(id), class_=cls)


@add_example()
def output_table(id: str, **kwargs: TagAttrValue) -> Tag:
    """
    Create a output container for a table.

    Parameters
    ----------
    id
        An output id.
    **kwargs
        Additional attributes to add to the container.

    Returns
    -------
    :

    See Also
    --------
    * :class:`~shiny.render.table`
    """
    return tags.div({"class": "shiny-html-output"}, id=resolve_id(id), **kwargs)


@add_example()
def output_ui(
    id: str,
    inline: bool = False,
    container: Optional[TagFunction] = None,
    fill: bool = False,
    fillable: bool = False,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a output container for a UI (i.e., HTML) element.

    Parameters
    ----------
    id
        An output id.
    inline
        If ``True``, the result is displayed inline.
    container
        A Callable that returns the output container.
    fill
        Whether or not to allow the UI output to grow/shrink to fit a fillable container
        with an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    fillable
        Whether or not the UI output area should be considered a fillable (i.e.,
        flexbox) container.
    **kwargs
        Attributes to be applied to the output container.

    Returns
    -------
    :
        A UI element

    See Also
    --------
    * :class:`~shiny.render.ui`
    * :func:`~shiny.ui.output_text`
    """

    if not container:
        container = tags.span if inline else tags.div
    res = container({"class": "shiny-html-output"}, id=resolve_id(id), **kwargs)
    if fill:
        res = as_fill_item(res)
    if fillable:
        res = as_fillable_container(res)
    return res
