from typing import Optional
from htmltools import tags, Tag, div, css, TagAttrArg, TagFunction


def output_plot(
    id: str, width: str = "100%", height: str = "400px", inline: bool = False
) -> Tag:
    res = output_image(id=id, width=width, height=height, inline=inline)
    res.add_class("shiny-plot-output")
    return res


def output_image(
    id: str, width: str = "100%", height: str = "400px", inline: bool = False
) -> Tag:
    func = tags.span if inline else div
    style = None if inline else css(width=width, height=height)
    return func(id=id, class_="shiny-image-output", style=style)


def output_text(
    id: str, inline: bool = False, container: Optional[TagFunction] = None
) -> Tag:
    if not container:
        container = tags.span if inline else tags.div
    return container(id=id, class_="shiny-text-output")  # type: ignore


def output_text_verbatim(id: str, placeholder: bool = False) -> Tag:
    cls = "shiny-text-output" + (" noplaceholder" if not placeholder else "")
    return tags.pre(id=id, class_=cls)


def output_ui(
    id: str,
    inline: bool = False,
    container: Optional[TagFunction] = None,
    **kwargs: TagAttrArg
) -> Tag:
    if not container:
        container = tags.span if inline else tags.div
    return container({"class": "shiny-html-output"}, id=id, **kwargs)
