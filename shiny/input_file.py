from htmltools import *
from .input_utils import *
from typing import Optional, List

def input_file(id: str, label: str, multiple: bool=False, accept: Optional[List[str]]=None, width: Optional[str]=None, button_label: str="Browse...", placeholder: str="No file selected"):

  btn_file = span(
    button_label,
    tags.input(
      id=id, name=id, type="file", multiple="multiple" if multiple else None,
      accept=",".join(accept) if accept else None,
      # Don't use "display: none;" style, which causes keyboard accessibility issue; instead use the following workaround: https://css-tricks.com/places-its-tempting-to-use-display-none-but-dont/
      style="position: absolute !important; top: -99999px !important; left: -99999px !important;"
    ),
    _class_="btn btn-default btn-file"
  )

  return div(
    shiny_input_label(id, label),
    div(
      tags.label(btn_file, _class_="input-group-btn input-group-prepend"),
      tags.input(type = "text", _class_ = "form-control", placeholder = placeholder, readonly = "readonly"),
      _class_="input-group"
    ),
    div(
      div(_class_="progress-bar"),
      id=id+"_progress", _class_="progress active shiny-file-input-progress"
    ),
    _class_="form-group shiny-input-container",
    style=f"width: {width};" if width else None
  )
