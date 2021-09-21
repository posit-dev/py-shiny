from htmltools import *
from .input_utils import *
from typing import Optional

def input_text(id: str, label: str, value: str="", width: Optional[str]=None, placeholder: Optional[str]=None) -> tag:
  return div(
    shiny_input_label(id, label),
    tags.input(
      id=id, type="text", _class_="form-control",
      value=value, placeholder = placeholder
    ),
    _class_ = "form-group shiny-input-container",
    style=f"width: {width};" if width else None
  )

def input_text_area(id: str, label: str, value: str="", width: Optional[str] = None, height: Optional[str] = None,
                    cols: Optional[int] = None, rows: Optional[int] = None, placeholder: Optional[str] = None,
                    resize: Optional[str]=None) -> tag:

    style=""
    # The width is specified on the parent div.
    if not width:
      style += f"width: 100%;"
    if height:
      style += f"height: {height};"
    if resize:
      style += f"resize: {resize};"

    if resize and resize not in ["none", "both", "horizontal", "vertical"]:
      raise ValueError("Invalid resize value: " + str(resize))

    area = tags.textarea(
      id=id, _class_="form-control", style=style,
      placeholder=placeholder, rows=rows, cols=cols,
      children=value
    )

    return div(
      shiny_input_label(id, label), area,
      _class_ = "form-group shiny-input-container",
      style = f"width: {width};" if width else None
    )
