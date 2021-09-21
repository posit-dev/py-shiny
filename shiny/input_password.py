
from htmltools import *
from .input_utils import *
from typing import Optional

def passwordInput(id: str, label: str, value: str = "", width: Optional[str] = None, placeholder: Optional[str] = None) -> tag:
  return div(
    shiny_input_label(id, label),
    tags.input(
      id=id, type="password", value=value,
      _class_="form-control", placeholder=placeholder
    ),
    _class_ = "form-group shiny-input-container",
    style = f"width: {width};" if width else "",
  )
