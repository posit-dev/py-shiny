__all__ = (
    "nav",
    "nav_menu",
    "nav_item",
    "nav_spacer",
    "nav_content",
    "navs_tab",
    "navs_pill",
    "navs_hidden",
    "navs_tab_card",
    "navs_pill_card",
    "navs_pill_list",
    "navs_bar",
)

import sys
from typing import Optional, Any, Tuple

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import jsx_tag_create, JSXTag, TagList, TagChildArg, JSXTagAttrArg

from ._html_dependencies import nav_deps


def nav(
    title: Any,
    *args: TagChildArg,
    value: Optional[str] = None,
    icon: TagChildArg = None,
) -> JSXTag:
    if not value:
        value = title
    return _nav_tag("Nav", *args, value=value, title=TagList(icon, title))


def nav_menu(
    title: TagChildArg,
    *args: TagChildArg,
    value: Optional[str] = None,
    icon: TagChildArg = None,
    align: Literal["left", "right"] = "left",
) -> JSXTag:
    if not value:
        value = str(title)
    return _nav_tag(
        "NavMenu", *args, value=value, title=TagList(icon, title), align=align
    )


def nav_content(value: str, *args: TagChildArg, icon: TagChildArg = None) -> JSXTag:
    return nav(None, *args, value=value, icon=icon)


def nav_item(*args: TagChildArg) -> JSXTag:
    return _nav_tag("NavItem", *args)


def nav_spacer() -> JSXTag:
    return _nav_tag("NavSpacer")


def navs_tab(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return _nav_tag(
        "Navs",
        *args,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_tab_card(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return _nav_tag(
        "NavsCard",
        *args,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_pill(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return _nav_tag(
        "Navs",
        *args,
        type="pills",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_hidden(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return _nav_tag(
        "Navs",
        *args,
        type="hidden",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_pill_card(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    placement: Literal["above", "below"] = "above",
) -> JSXTag:
    return _nav_tag(
        "NavsCard",
        *args,
        type="pills",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
        placement=placement,
    )


def navs_pill_list(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    well: bool = True,
    fluid: bool = True,
    widths: Tuple[int, int] = (4, 8),
) -> JSXTag:
    return _nav_tag(
        "NavsList",
        *args,
        id=id,
        selected=selected,
        header=header,
        footer=footer,
        well=well,
        fluid=fluid,
        widthNav=widths[0],
        widthContent=widths[1],
    )


def navs_bar(
    *args: TagChildArg,
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
) -> JSXTag:
    return _nav_tag(
        "NavsBar",
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
        fluid=fluid,
    )


def _nav_tag(name: str, *args: TagChildArg, **kwargs: JSXTagAttrArg) -> JSXTag:
    tag = jsx_tag_create("bslib." + name)
    return tag(nav_deps(), *args, **kwargs)
