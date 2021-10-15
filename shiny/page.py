from htmltools import tags, Tag, TagList, HTMLDocument, div, TagChildArg
from typing import Literal, Optional, Any, List
from warnings import warn
from .html_dependencies import bootstrap_deps
from .navs import navs_bar
from .input_utils import missing


def page_navbar(
    *args: TagChildArg,  # Create a type for nav()?
    title: Optional[TagChildArg] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    bg: Optional[str] = None,
    inverse: Literal["auto", True, False] = "auto",
    collapsible: bool = True,
    fluid: bool = True,
    window_title: Optional[str] = missing,
    lang: Optional[str] = None
) -> HTMLDocument:

    # https://github.com/rstudio/shiny/issues/2310
    if title and window_title is missing:
        window_title: List[str] = find_characters(title)
        if window_title:
            window_title: Tag = tags.title(" ".join(window_title))
        else:
            warn(
                "Unable to infer a `window_title` default from `title`. Consider providing a character string to `window_title`."
            )
            window_title: None = None

    return HTMLDocument(
        navs_bar(
            *args,
            title=title,
            id=id,
            selected=selected,
            position=position,
            header=header,
            footer=footer,
            bg=bg,
            inverse=inverse,
            collapsible=collapsible,
            fluid=fluid
        ),
        tags.head(window_title),
        lang=lang,
    )


def page_fluid(
    *args: Any, title: Optional[str] = None, lang: Optional[str] = None, **kwargs: str
) -> HTMLDocument:
    return page_bootstrap(
        div(*args, class_="container-fluid", *kwargs), title=title, lang=lang
    )


def page_fixed(
    *args: Any, title: Optional[str] = None, lang: Optional[str] = None, **kwargs: str
) -> HTMLDocument:
    return page_bootstrap(
        div(*args, class_="container", **kwargs), title=title, lang=lang
    )


# TODO: implement theme (just Bootswatch for now?)
def page_bootstrap(
    *args: Any, title: Optional[str] = None, lang: Optional[str] = None
) -> HTMLDocument:
    page = TagList(bootstrap_deps(), *args)
    head = tags.title(title) if title else None
    return HTMLDocument(tags.html(tags.head(head), tags.body(page), lang=lang))


def find_characters(x: Any) -> List[str]:
    if isinstance(x, str):
        return [x]
    elif isinstance(x, list):
        return [y for y in x if isinstance(y, str)]
    else:
        return []
