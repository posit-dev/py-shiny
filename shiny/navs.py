from htmltools import tag, tag_list
from typing import Optional, Any, Literal, Tuple

def nav(title: Any, *args: Any, value: Optional[str]=None, icon: Optional[str]=None) -> tag:
  if not value: value=title
  return tag(*args, _name="Nav", value=value, title=title)


def nav_menu(title: Any, *args: Any, value: Optional[str]=None, icon: Optional[str]=None, align: Literal["left", "right"]="left") -> tag:
  if not value: value=title
  return tag(*args, _name="NavMenu", value=value, title=title)

def nav_item(*args: Any) -> tag:
  return tag(*args, _name="NavItem")

def nav_spacer() -> tag:
  return tag(_name="NavSpacer")

#def nav_content(value, *args, icon: Optional[str]=None) -> tag:
#  raise Exception("Not yet implemented")

def navs_tab_card(*args: Any, id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None) -> tag:
  navs=tag(*args, _name="NavsCard", type="tabs", id=id, selected=selected, header=header, footer=footer)
  return Compile(navs)


def navs_pill(*args: Any, id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None) -> tag:
  navs=tag(*args, _name="Navs", type="pills", id=id, selected=selected, header=header, footer=footer)
  return Compile(navs)


def navs_pill_card(*args: Any, id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None, placement: Literal["above", "below"]="above") -> tag:
  navs=tag(*args, _name="NavsCard", type="pills", id=id, selected=selected, header=header, footer=footer, placement=placement)
  return Compile(navs)


def navs_pill_list(*args: Any, id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None, well: bool=True, fluid: bool=True, widths: Tuple=(4, 8)) -> tag:
    navs=tag(*args, _name="NavsList", id=id, selected=selected, header=header, footer=footer, well=well, widthNav=widths[0], widthContent=widths[1])
    return Compile(navs)

# TODO: implement (does this need it's own component)?
#def navs_hidden(*args,  id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None) -> tag:
#    navs=tag(*args, _name="NavsHidden", id=id, selected=selected, header=header, footer=footer)
#    return Compile(navs)

def Compile(tag: tag_list) -> tag_list:
  return tag
