__all__ = (
    "output_plot",
    "output_image",
    "output_text",
    "output_text_verbatim",
    "output_ui",
)

from typing import Optional
from htmltools import tags, Tag, div, css, TagAttrArg, TagFunction

from .._docstring import doc


@doc(
    "Create a output container for a static plot.",
    note="Currently only supports ``matplotlib`` and ``PIL`` figures.",
    returns="A UI element",
    see_also=[":func:`~shiny.render_plot`", ":func:`~shiny.ui.output_image`"],
)
def output_plot(
    id: str, width: str = "100%", height: str = "400px", inline: bool = False
) -> Tag:
    res = output_image(id=id, width=width, height=height, inline=inline)
    res.add_class("shiny-plot-output")
    return res


@doc(
    "Create a output container for a static image.",
    returns="A UI element",
    see_also=[":func:`~shiny.render_image`", ":func:`~shiny.ui.output_plot`"],
)
def output_image(
    id: str, width: str = "100%", height: str = "400px", inline: bool = False
) -> Tag:
    func = tags.span if inline else div
    style = None if inline else css(width=width, height=height)
    return func(id=id, class_="shiny-image-output", style=style)


@doc(
    "Create a output container for some text.",
    returns="A UI element",
    note="Text is HTML-escaped prior to rendering.",
    see_also=[
        ":func:`~shiny.render_text`",
        ":func:`~shiny.ui.output_text_verbatim`",
    ],
)
def output_text(
    id: str, inline: bool = False, container: Optional[TagFunction] = None
) -> Tag:
    if not container:
        container = tags.span if inline else tags.div
    return container(id=id, class_="shiny-text-output")  # type: ignore


@doc(
    "Create a output container for some text.",
    parameters={
        "placeholder": """
        If the output is empty or ``None``, should an empty rectangle be displayed to
        serve as a placeholder? (does not affect behavior when the output is nonempty)
        """,
    },
    returns="A UI element",
    note="""
    Usually paired with :func:`~shiny.render_text` and the text produced by it is
    HTML-escaped prior to rendering (use :func:`~shiny.render_ui` instead to render
    HTML). See :func:`~shiny.ui.output_text` for an example.
    """,
    see_also=[
        ":func:`~shiny.render_text`",
        ":func:`~shiny.ui.output_text`",
    ],
)
def output_text_verbatim(id: str, placeholder: bool = False) -> Tag:
    cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    return tags.pre(id=id, class_=cls)


@doc(
    "Create a output container for a UI (i.e., HTML) element.",
    parameters={"kwargs": "Attributes to be applied to the output container."},
    returns="A UI element",
    see_also=[
        ":func:`~shiny.render_ui`",
        ":func:`~shiny.ui.output_text`",
    ],
)
def output_ui(
    id: str,
    inline: bool = False,
    container: Optional[TagFunction] = None,
    **kwargs: TagAttrArg
) -> Tag:
    if not container:
        container = tags.span if inline else tags.div
    return container({"class": "shiny-html-output"}, id=id, **kwargs)
