import sys
from typing import Optional, Any, List
from warnings import warn

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import tags, Tag, TagList, div, TagChildArg

from .html_dependencies import bootstrap_deps
from .navs import navs_bar


def page_navbar(
    *arguments: TagChildArg,  # Create a type for nav()?
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
    window_title: Optional[str] = None,
    lang: Optional[str] = None
) -> Tag:

    if title is not None and window_title is None:
        # Try to infer window_title from contents of title
        window_title = " ".join(find_characters(title))
        if not window_title:
            warn(
                "Unable to infer a `window_title` default from `title`. Consider providing a character string to `window_title`."
            )

    return tags.html(
        tags.head(tags.title(window_title)),
        tags.body(
            navs_bar(
                *arguments,
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
            )
        ),
        lang=lang,
    )


def page_fluid(
    *arguments: Any,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: str
) -> Tag:
    return page_bootstrap(
        div(*arguments, class_="container-fluid", **kwargs), title=title, lang=lang
    )


def page_fixed(
    *arguments: Any,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: str
) -> Tag:
    return page_bootstrap(
        div(*arguments, class_="container", **kwargs), title=title, lang=lang
    )


# TODO: implement theme (just Bootswatch for now?)
def page_bootstrap(
    *arguments: Any, title: Optional[str] = None, lang: Optional[str] = None
) -> Tag:
    page = TagList(bootstrap_deps(), *arguments)
    head = tags.title(title) if title else None
    return tags.html(tags.head(head), tags.body(page), lang=lang)


def find_characters(x: Any) -> List[str]:
    if isinstance(x, str):
        return [x]
    elif isinstance(x, list):
        return [y for y in x if isinstance(y, str)]
    else:
        return []
