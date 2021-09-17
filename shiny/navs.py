from htmltools import jsx_tag, tag_list, tag, html_dependency
from typing import Optional, Any, Literal, Tuple

def nav(title: Any, *args: Any, value: Optional[str]=None, icon: Optional[str]=None) -> tag:
  if not value: value=title
  return bslib_tag("Nav", *args, value=value, title=title)

def nav_menu(title: Any, *args: Any, value: Optional[str]=None, icon: Optional[str]=None, align: Literal["left", "right"]="left") -> tag:
  if not value: value=title
  return bslib_tag("NavMenu", *args, value=value, title=title)

#def nav_content(value, *args, icon: Optional[str]=None) -> tag:
#  raise Exception("Not yet implemented")

def nav_item(*args: Any) -> tag:
  return bslib_tag("NavItem", *args)

def nav_spacer() -> tag:
  return bslib_tag("NavSpacer")


def navs_tab_card(*args: Any, id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None) -> tag:
  return bslib_tag("NavsCard", *args, type="tabs", id=id, selected=selected, header=header, footer=footer)

def navs_pill(*args: Any, id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None) -> tag:
  return bslib_tag("Navs", *args, type="pills", id=id, selected=selected, header=header, footer=footer)

def navs_pill_card(*args: Any, id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None, placement: Literal["above", "below"]="above") -> tag:
  return bslib_tag("NavsCard", *args, type="pills", id=id, selected=selected, header=header, footer=footer, placement=placement)

def navs_pill_list(*args: Any, id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None, well: bool=True, fluid: bool=True, widths: Tuple=(4, 8)) -> tag:
  return bslib_tag("NavsList", *args, id=id, selected=selected, header=header, footer=footer, well=well, widthNav=widths[0], widthContent=widths[1])

# TODO: implement (does this need it's own component)?
#def navs_hidden(*args,  id: Optional[str]=None, selected: Optional[str]=None, header: Any=None, footer: Any=None) -> tag:
#    return bslib_tag("NavsHidden", *args id=id, selected=selected, header=header, footer=footer)


def bslib_tag(name, *args, **kwargs) -> tag:
  tag = jsx_tag("bslib." + name)
  return tag(bslib_dependency(), *args, **kwargs)

def bslib_dependency() -> html_dependency:
  return html_dependency(
    name = "bslib",
    version = "1.0",
    package = "shiny",
    src = "www/shared/bslib/dist",
    script = "navs.min.js"
  )
