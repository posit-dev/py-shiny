from htmltools import jsx_tag, tag, TagChild
from typing import Optional, Any, Literal, List
from .html_dependencies import nav_deps


def nav(
    title: Any,
    *args: TagChild,
    value: Optional[str] = None,
    # icon: Optional[str] = None
) -> tag:
    if not value:
        value = title
    return nav_tag("Nav", *args, value=value, title=title)


def nav_menu(
    title: TagChild,
    *args: TagChild,
    value: Optional[str] = None,
    # icon: Optional[str] = None,
    align: Literal["left", "right"] = "left",
) -> tag:
    if not value:
        value = str(title)
    return nav_tag("NavMenu", *args, value=value, title=title, align=align)


# def nav_content(value, *args, icon: Optional[str] = None) -> tag:
#  raise Exception("Not yet implemented")


def nav_item(*args: TagChild) -> tag:
    return nav_tag("NavItem", *args)


def nav_spacer() -> tag:
    return nav_tag("NavSpacer")


def navs_tab(
    *args: TagChild,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
) -> tag:
    return nav_tag(
        "Navs",
        *args,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_tab_card(
    *args: TagChild,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
) -> tag:
    return nav_tag(
        "NavsCard",
        *args,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_pill(
    *args: TagChild,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
) -> tag:
    return nav_tag(
        "Navs",
        *args,
        type="pills",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_pill_card(
    *args: TagChild,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    placement: Literal["above", "below"] = "above",
) -> tag:
    return nav_tag(
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
    *args: TagChild,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    well: bool = True,
    fluid: bool = True,
    widths: List[int] = [4, 8],
) -> tag:
    return nav_tag(
        "NavsList",
        *args,
        id=id,
        selected=selected,
        header=header,
        footer=footer,
        well=well,
        widthNav=widths[0],
        widthContent=widths[1],
    )


# def navs_hidden(*args, id: Optional[str] = None, selected: Optional[str] = None, header: Any=None, footer: Any=None) -> tag:
#  return nav_tag("NavsHidden", *args, id=id, selected=selected, header=header, footer=footer)


def navs_bar(
    *args: TagChild,
    title: Optional[str] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    bg: Optional[str] = None,
    inverse: Literal["auto", True, False] = "auto",
    collapsible: bool = True,
    fluid: bool = True,
) -> tag:
    return nav_tag(
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


def nav_tag(name: str, *args: TagChild, **kwargs: Any) -> tag:
    tag = jsx_tag("bslib." + name)
    return tag(nav_deps(), *args, **kwargs)
