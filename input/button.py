from typing import Optional, Dict, Any
from htmltools import tags

# TODO: implement icon
def action_button(id: str, label: str, *args: Any, icon: Optional[str] = None, width: Optional[str] = None, **kwargs: Dict[str, str]):
  b = tags.button(
    label, *args,
    id = id, type = "button",
    className = "btn btn-default action-button",
    **kwargs
  )
  # TODO: reinvent css()/validateCssUnit()?
  if width is not None:
    b.append_attrs("style", f"width:{width};")
  return b

def action_link(id: str, label: str, *args: Any, icon: Optional[str] = None, **kwargs: Dict[str, str]):
  # TODO: implement bookmarking (restoreInput())?
  return tags.a(
    label, *args,
    id = id, href = "#",
    className = "action-button",
    **kwargs
  )