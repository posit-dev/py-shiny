from htmltools import tags
from typing import Optional

def shiny_input_label(id: str, label: Optional[str] = None):
  cls = "control-label" + ("" if label else "shiny-label-null")
  return tags.label(
      label, _class_ = cls,
      id = id + "-label",
      _for_ = id
  )