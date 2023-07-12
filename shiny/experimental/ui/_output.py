# !!`shiny.experimental`!! This file is a direct copy to `shiny/_output.py`. Functions that were not altered were removed. Inserted code as been marked with `NEW`&`/NEW`
# Related: https://github.com/rstudio/shiny/pull/3715

from __future__ import annotations

from typing import Optional

from htmltools import Tag, TagAttrValue, TagFunction, css, div, tags

from ..._namespaces import resolve_id
from ...types import MISSING, MISSING_TYPE
from ...ui._plot_output_opts import (
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
from ._fill import as_fill_item, as_fillable_container


# @add_example()
def output_plot(
    id: str,
    width: str = "100%",
    height: str = "400px",
    *,
    inline: bool = False,
    click: bool | ClickOpts = False,
    dblclick: bool | DblClickOpts = False,
    hover: bool | HoverOpts = False,
    brush: bool | BrushOpts = False,
    # NEW
    fill: bool | MISSING_TYPE = MISSING,
    # /NEW
) -> Tag:
    """
    Create a output container for a static plot.

    Place a :func:`~shiny.render.plot` result in the user interface. See
    :func:`~shiny.render.plot` for more details on what types of plots are supported.

    Parameters
    ----------
    id
        An input id.
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

    Returns
    -------
    :
        A UI element

    See Also
    -------
    * :func:`~shiny.render.plot`
    * :func:`~shiny.ui.output_image`
    """

    # NEW
    if isinstance(fill, MISSING_TYPE):
        fill = not inline
    # /NEW

    res = output_image(
        id=id,
        width=width,
        height=height,
        inline=inline,
        click=click,
        dblclick=dblclick,
        hover=hover,
        brush=brush,
        # NEW
        fill=fill,
        # /NEW
    )
    res.add_class("shiny-plot-output")
    return res


# @add_example()
def output_image(
    id: str,
    width: str = "100%",
    height: str = "400px",
    *,
    inline: bool = False,
    click: bool | ClickOpts = False,
    dblclick: bool | DblClickOpts = False,
    hover: bool | HoverOpts = False,
    brush: bool | BrushOpts = False,
    # NEW
    fill: bool = False,
    # /NEW
) -> Tag:
    """
    Create a output container for a static image.

    Parameters
    ----------
    id
        An input id.
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

    Returns
    -------
    :
        A UI element

    See Also
    -------
    ~shiny.render.image
    ~shiny.ui.output_plot
    """
    func = tags.span if inline else div
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


# @add_example()
def output_ui(
    id: str,
    inline: bool = False,
    container: Optional[TagFunction] = None,
    # NEW
    fill: bool = False,
    fillable: bool = False,
    # /NEW
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a output container for a UI (i.e., HTML) element.

    Parameters
    ----------
    id
        An input id.
    inline
        If ``True``, the result is displayed inline
    container
        A Callable that returns the output container.
    kwargs
        Attributes to be applied to the output container.

    Returns
    -------
    :
        A UI element

    See Also
    -------
    ~shiny.render.ui
    ~shiny.ui.output_text
    """

    if not container:
        container = tags.span if inline else tags.div
    res = container(
        {"class": "shiny-html-output"},
        id=resolve_id(id),
        **kwargs,
    )

    if fillable:
        res = as_fillable_container(res)
    if fill:
        res = as_fill_item(res)

    return res
