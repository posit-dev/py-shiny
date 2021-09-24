from .html_dependencies import jqui_deps
from htmltools import *
from typing import Callable, Dict, Literal, Optional, Union

# TODO: import these from htmltools?
ChildType = Union[tag_list, html_dependency, str, None]
AttrType = Optional[Dict[str, str]]

def row(*args: ChildType, **kwargs: AttrType) -> tag:
  return div(*args, _class_="row", **kwargs)

def column(width: int, *args: ChildType, offset: int=0, **kwargs: AttrType) -> tag:
  if width < 1 or width > 12:
    raise ValueError("Column width must be between 1 and 12")
  cls = "col-sm-" + str(width)
  if offset > 0:
    # offset-md-x is for bootstrap 4 forward compat
    # (every size tier has been bumped up one level)
    # https://github.com/twbs/bootstrap/blob/74b8fe7/docs/4.3/migration/index.html#L659
    off = str(offset)
    cls += " offset-md-{off} col-sm-offset-{off}"
  return div(*args, _class_=cls, **kwargs)


# TODO: also accept a generic list (and wrap in panel in that case)
def layout_sidebar(sidebar: ChildType, main: ChildType, position: Literal["left", "right"]="left") -> tag:
  return row(sidebar, main) if position == "left" else row(main, sidebar)

def panel_well(*args: ChildType, **kwargs: AttrType) -> tag:
  return div(*args, _class_="well", **kwargs)

def panel_sidebar(*args: ChildType, width: int = 4, **kwargs: AttrType) -> tag:
  return div(
    # A11y semantic landmark for sidebar
    tags.form(*args, role="complementary", _class_="well", **kwargs),
    _class_="col-sm-" + str(width),
  )

def panel_main(*args: ChildType, width: int = 8, **kwargs: AttrType):
  return div(
    # A11y semantic landmark for main region
    *args, role="main",
    _class_="col-sm-" + str(width),
    **kwargs
  )

# TODO: replace `flowLayout()`/`splitLayout()` with a flexbox wrapper?
#def panel_input(*args: ChildType, **kwargs: AttrType):
#  return div(flowLayout(...), _class_="shiny-input-panel")

# TODO: do we have an answer for shiny::NS() yet?
def panel_conditional(condition: str, *args: ChildType, ns: Callable[[str], str] = lambda x: x, **kwargs: AttrType):
  return div(*args, data_display_if=condition, data_ns_prefix=ns(""), **kwargs)


def panel_title(title: str, windowTitle: Optional[str] = None) -> tag_list:
  if windowTitle is None:
    windowTitle = title
  return tag_list(
      html_dependency(
        "shiny-window-title", "999", src = {"href": " "},
        head=f"<title>{windowTitle}</title>",
      ),
      h2(title)
  )

def panel_fixed(*args: ChildType, **kwargs: AttrType) -> tag_list:
  return panel_absolute(*args, fixed=True, **kwargs)

def panel_absolute(*args: ChildType,
                   top: Optional[str]=None,
                   left: Optional[str]=None,
                   right: Optional[str]=None,
                   bottom: Optional[str] = None,
                   width: Optional[str] = None,
                   height: Optional[str] = None,
                   draggable: bool=False, fixed: bool=False,
                   cursor: Literal['auto', 'move', 'default', 'inherit']='auto',
                   **kwargs: AttrType) -> tag_list:
    style = css(
      top=top, left=left, right=right, bottom=bottom,
      width=width, height=height,
      position='fixed' if fixed else 'absolute',
      cursor='move' if draggable else 'inherit' if cursor == 'auto' else cursor
    )
    divTag = div(*args, style=style, **kwargs)
    if not draggable:
      return divTag
    divTag.append(_class_="draggable")
    deps = jqui_deps()
    deps.stylesheet = []
    return tag_list(
      deps, divTag,
      tags.script(html('$(".draggable").draggable();'))
    )


def help_text(*args: ChildType, **kwargs: AttrType) -> tag:
  return span(*args, _class_="help-block", **kwargs)
