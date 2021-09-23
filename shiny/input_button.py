from typing import Optional, Dict, Any
from htmltools import tags, tag

# TODO: implement icon
def input_button(id: str, label: str, *args: Any, icon: Optional[str] = None, width: Optional[str] = None, **kwargs: Dict[str, str]) -> tag:
  return tags.button(
    label, *args,
    id = id, type = "button",
    _class_ = "btn btn-default action-button",
    style = f"width: {width};" if width else None,
    **kwargs
  )

def input_link(id: str, label: str, *args: Any, icon: Optional[str] = None, **kwargs: Dict[str, str]) -> tag:
  return tags.a(
    label, *args,
    id = id, href = "#",
    _class_ = "action-button",
    **kwargs
  )