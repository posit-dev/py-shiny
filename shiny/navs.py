import sys
from typing import Optional, Any, Tuple

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import jsx_tag_create, JSXTag, TagList, TagChildArg, JSXTagAttrArg

from .html_dependencies import nav_deps


def nav(
    title: Any,
    *arguments: TagChildArg,
    value: Optional[str] = None,
    icon: TagChildArg = None,
) -> JSXTag:
    if not value:
        value = title
    return nav_tag("Nav", *arguments, value=value, title=TagList(icon, title))


def nav_menu(
    title: TagChildArg,
    *arguments: TagChildArg,
    value: Optional[str] = None,
    icon: TagChildArg = None,
    align: Literal["left", "right"] = "left",
) -> JSXTag:
    if not value:
        value = str(title)
    return nav_tag(
        "NavMenu", *arguments, value=value, title=TagList(icon, title), align=align
    )


# def nav_content(value, *arguments, icon: TagChildArg = None) -> tag:
#  raise Exception("Not yet implemented")


def nav_item(*arguments: TagChildArg) -> JSXTag:
    return nav_tag("NavItem", *arguments)


def nav_spacer() -> JSXTag:
    return nav_tag("NavSpacer")


def navs_tab(
    *arguments: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return nav_tag(
        "Navs",
        *arguments,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_tab_card(
    *arguments: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return nav_tag(
        "NavsCard",
        *arguments,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_pill(
    *arguments: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return nav_tag(
        "Navs",
        *arguments,
        type="pills",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_pill_card(
    *arguments: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    placement: Literal["above", "below"] = "above",
) -> JSXTag:
    return nav_tag(
        "NavsCard",
        *arguments,
        type="pills",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
        placement=placement,
    )


def navs_pill_list(
    *arguments: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    well: bool = True,
    fluid: bool = True,
    widths: Tuple[int, int] = (4, 8),
) -> JSXTag:
    return nav_tag(
        "NavsList",
        *arguments,
        id=id,
        selected=selected,
        header=header,
        footer=footer,
        well=well,
        widthNav=widths[0],
        widthContent=widths[1],
    )


# def navs_hidden(*arguments, id: Optional[str] = None, selected: Optional[str] = None, header: Any=None, footer: Any=None) -> tag:
#  return nav_tag("NavsHidden", *arguments, id=id, selected=selected, header=header, footer=footer)


def navs_bar(
    *arguments: TagChildArg,
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
    return nav_tag(
        "NavsBar",
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
        fluid=fluid,
    )


def nav_tag(name: str, *arguments: TagChildArg, **kwargs: JSXTagAttrArg) -> JSXTag:
    tag = jsx_tag_create("bslib." + name)
    return tag(nav_deps(), *arguments, **kwargs)
