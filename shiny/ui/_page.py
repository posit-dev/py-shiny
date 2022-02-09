__all__ = (
    "page_navbar",
    "page_fluid",
    "page_fixed",
    "page_bootstrap",
)

import sys
from typing import Optional, Any, List
from warnings import warn

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import tags, Tag, TagList, div, TagChildArg

from ._html_dependencies import bootstrap_deps
from ._navs import navs_bar


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
    window_title: Optional[str] = None,
    lang: Optional[str] = None
) -> Tag:

    if title is not None and window_title is None:
        # Try to infer window_title from contents of title
        window_title = " ".join(_find_characters(title))
        if not window_title:
            warn(
                "Unable to infer a `window_title` default from `title`. Consider providing a character string to `window_title`."
            )

    return tags.html(
        tags.head(tags.title(window_title)),
        tags.body(
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
            )
        ),
        lang=lang,
    )


def page_fluid(
    *args: Any, title: Optional[str] = None, lang: Optional[str] = None, **kwargs: str
) -> Tag:
    return page_bootstrap(
        div({"class": "container-fluid"}, *args, **kwargs), title=title, lang=lang
    )


def page_fixed(
    *args: Any, title: Optional[str] = None, lang: Optional[str] = None, **kwargs: str
) -> Tag:
    return page_bootstrap(
        div({"class": "container"}, *args, **kwargs), title=title, lang=lang
    )


# TODO: implement theme (just Bootswatch for now?)
def page_bootstrap(
    *args: Any, title: Optional[str] = None, lang: Optional[str] = None
) -> Tag:
    page = TagList(*bootstrap_deps(), *args)
    head = tags.title(title) if title else None
    return tags.html(tags.head(head), tags.body(page), lang=lang)


def _find_characters(x: Any) -> List[str]:
    if isinstance(x, str):
        return [x]
    elif isinstance(x, list):
        return [y for y in x if isinstance(y, str)]
    else:
        return []
