__all__ = (
    "output_plot",
    "output_image",
    "output_text",
    "output_text_verbatim",
    "output_table",
    "output_ui",
)

from typing import Dict, Optional, Union

from htmltools import Tag, TagAttrArg, TagFunction, css, div, tags

from .._docstring import add_example
from .._namespaces import resolve_id
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


@add_example()
def output_plot(
    id: str,
    width: str = "100%",
    height: str = "400px",
    *,
    inline: bool = False,
    click: Optional[Union[str, ClickOpts]] = None,
    dblclick: Optional[Union[str, DblClickOpts]] = None,
    hover: Optional[Union[str, HoverOpts]] = None,
    brush: Optional[Union[str, BrushOpts]] = None,
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
        This can be `None` (the default), a string, or an object created by
        :func:`~shiny.ui.click_opts`. If you use a string value like `"plot_click"` (or
        equivalently, `click_opts(id="plot_click")`), the plot will send coordinates to
        the server whenever it is clicked, and the value will be accessible via
        `input.plot_click()`. The value will be a dictionary with `x` and `y` elements
        indicating the mouse position.
    dblclick
        This is just like the `click` parameter, but for double-click events.
    hover
        Similar to the `click` argument, this can be `None` (the default), a string, or
        an object created by :func:`~shiny.ui.hover_opts`. If you use a string value
        like `"plot_hover"` (or equivalently, `hover_opts(id="plot_hover")`), the plot
        will send coordinates to the server pauses on the plot, and the value will be
        accessible via `input.plot_hover()`. The value will be a named list with `x` and
        `y` elements indicating the mouse position. To control the hover time or hover
        delay type, use :func:`~shiny.ui.hover_opts`.
    brush
        Similar to the `click` argument, this can be `None` (the default), a string, or
        an object created by :func:`~shiny.ui.brush_opts`. If you use a string value
        like `"plot_brush"` (or equivalently, `brush_opts(id="plot_brush")`), the plot
        will allow the user to "brush" in the plotting area, and will send information
        about the brushed area to the server, and the value will be accessible via
        `input.plot_brush()`. Brushing means that the user will be able to draw a
        rectangle in the plotting area and drag it around. The value will be a named
        list with `xmin`, `xmax`, `ymin`, and `ymax` elements indicating the brush area.
        To control the brush behavior, use :func:`~shiny.ui.brush_opts`. Multiple
        `output_image`/`output_plot` calls may share the same `id` value; brushing one
        image or plot will cause any other brushes with the same `id` to disappear.

    Returns
    -------
    A UI element

    See Also
    -------
    ~shiny.render.plot ~shiny.ui.output_image
    """
    res = output_image(
        id=resolve_id(id),
        width=width,
        height=height,
        inline=inline,
        click=click,
        dblclick=dblclick,
        hover=hover,
        brush=brush,
    )
    res.add_class("shiny-plot-output")
    return res


@add_example()
def output_image(
    id: str,
    width: str = "100%",
    height: str = "400px",
    *,
    inline: bool = False,
    click: Optional[Union[str, ClickOpts]] = None,
    dblclick: Optional[Union[str, DblClickOpts]] = None,
    hover: Optional[Union[str, HoverOpts]] = None,
    brush: Optional[Union[str, BrushOpts]] = None,
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
        This can be `None` (the default), a string, or an object created by
        :func:`~shiny.ui.click_opts`. If you use a string value like `"plot_click"` (or
        equivalently, `click_opts(id="plot_click")`), the plot will send coordinates to
        the server whenever it is clicked, and the value will be accessible via
        `input.plot_click()`. The value will be a dictionary with `x` and `y` elements
        indicating the mouse position.
    dblclick
        This is just like the `click` parameter, but for double-click events.
    hover
        Similar to the `click` argument, this can be `None` (the default), a string, or
        an object created by :func:`~shiny.ui.hover_opts`. If you use a string value
        like `"plot_hover"` (or equivalently, `hover_opts(id="plot_hover")`), the plot
        will send coordinates to the server pauses on the plot, and the value will be
        accessible via `input.plot_hover()`. The value will be a named list with `x` and
        `y` elements indicating the mouse position. To control the hover time or hover
        delay type, use :func:`~shiny.ui.hover_opts`.
    brush
        Similar to the `click` argument, this can be `None` (the default), a string, or
        an object created by :func:`~shiny.ui.brush_opts`. If you use a string value
        like `"plot_brush"` (or equivalently, `brush_opts(id="plot_brush")`), the plot
        will allow the user to "brush" in the plotting area, and will send information
        about the brushed area to the server, and the value will be accessible via
        `input.plot_brush()`. Brushing means that the user will be able to draw a
        rectangle in the plotting area and drag it around. The value will be a named
        list with `xmin`, `xmax`, `ymin`, and `ymax` elements indicating the brush area.
        To control the brush behavior, use :func:`~shiny.ui.brush_opts`. Multiple
        `output_image`/`output_plot` calls may share the same `id` value; brushing one
        image or plot will cause any other brushes with the same `id` to disappear.

    Returns
    -------
    A UI element

    See Also
    -------
    ~shiny.render.image
    ~shiny.ui.output_plot
    """
    func = tags.span if inline else div
    style = None if inline else css(width=width, height=height)

    args: Dict[str, str] = dict()

    if click is not None:
        if isinstance(click, str):
            click = click_opts(id=click)
        args.update(**format_opt_names(click, "click"))

    if dblclick is not None:
        if isinstance(dblclick, str):
            dblclick = dblclick_opts(id=dblclick)
        args.update(**format_opt_names(dblclick, "dblclick"))

    if hover is not None:
        if isinstance(hover, str):
            hover = hover_opts(id=hover)
        args.update(**format_opt_names(hover, "hover"))

    if brush is not None:
        if isinstance(brush, str):
            brush = brush_opts(id=brush)
            print(brush)
        args.update(**format_opt_names(brush, "brush"))

    return func(
        id=resolve_id(id),
        class_="shiny-image-output",
        style=style,
        **args,
    )


@add_example()
def output_text(
    id: str, inline: bool = False, container: Optional[TagFunction] = None
) -> Tag:
    """
    Create a output container for some text.

    Parameters
    ----------
    id
        An input id.
    inline
        If ``True``, the result is displayed inline
    container
        A Callable that returns the output container.

    Returns
    -------
    A UI element

    Note
    ----
    Text is HTML-escaped prior to rendering.

    See Also
    -------
    ~shiny.render.text
    ~shiny.ui.output_text_verbatim
    """

    if not container:
        container = tags.span if inline else tags.div
    return container(id=resolve_id(id), class_="shiny-text-output")


def output_text_verbatim(id: str, placeholder: bool = False) -> Tag:
    """
    Create a output container for some text.

    Place a :func:`~shiny.render.text` result in the user interface.
    Differs from :func:`~shiny.ui.output_text` in that it wraps the text in a
    fixed-width container with a gray-ish background color and border.

    Parameters
    ----------
    id
        An input id.
    placeholder
        If the output is empty or ``None``, should an empty rectangle be displayed to
        serve as a placeholder? (does not affect behavior when the output is nonempty)

    Returns
    -------
    A UI element

    See Also
    -------
    ~shiny.render.text
    ~shiny.ui.output_text

    Example
    -------
    See :func:`~shiny.ui.output_text`
    """

    cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    return tags.pre(id=resolve_id(id), class_=cls)


@add_example()
def output_table(id: str, **kwargs: TagAttrArg) -> Tag:
    """
    Create a output container for a table.

    Parameters
    ----------
    id
        An input id.
    **kwargs
        Additional attributes to add to the container.

    Returns
    -------

    See Also
    -------
    ~shiny.render.table
    """
    return tags.div({"class": "shiny-html-output"}, id=resolve_id(id), **kwargs)


@add_example()
def output_ui(
    id: str,
    inline: bool = False,
    container: Optional[TagFunction] = None,
    **kwargs: TagAttrArg,
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
    A UI element

    See Also
    -------
    ~shiny.render.ui
    ~shiny.ui.output_text
    """

    if not container:
        container = tags.span if inline else tags.div
    return container({"class": "shiny-html-output"}, id=resolve_id(id), **kwargs)
