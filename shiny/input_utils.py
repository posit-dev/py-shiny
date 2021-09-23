from htmltools import *
from sentinels import Sentinel
from typing import Optional

missing = Sentinel("missing")

def shiny_input_label(id: str, label: Optional[str] = None) -> tag:
  cls = "control-label" + ("" if label else "shiny-label-null")
  return tags.label(
      label, _class_=cls,
      id=id + "-label",
      _for_=id
  )