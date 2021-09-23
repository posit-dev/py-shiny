from htmltools import *
from .input_utils import *
from typing import Optional, Union, List, Dict

def input_checkbox(id: str, label: str, value: bool=False, width: Optional[str] = None):
  return div(
    div(
      tags.label(
          tags.input(id=id, type="checkbox", checked="checked" if value else None),
          span(label)
      ),
      _class_="checkbox",
    ),
    _class_="form-group shiny-input-container",
    style=f"width: {width};" if width else None
  )

choicesType = Union[Dict[str, str], List[str]]

def input_checkbox_group(id: str, label: str, choices: choicesType, choice_names: Optional[List[str]] = None, selected: Optional[str] = None, inline: bool = False, width: Optional[str] = None):
  input_label = shiny_input_label(id, label)
  options = generate_options(id=id, type='checkbox', choices=choices, choice_names=choice_names, selected=selected, inline=inline)
  return div(
    input_label, options,
    id=id, style=f"width: {width};" if width else None,
    _class_="form-group shiny-input-checkboxgroup shiny-input-container" + (" shiny-input-container-inline" if inline else ""),
    # https://www.w3.org/TR/wai-aria-practices/examples/checkbox/checkbox-1/checkbox-1.html
    role="group", aria_labelledby=input_label.get_attr("id")
  )

def input_radio_buttons(id: str, label: str, choices: choicesType, choice_names: Optional[List[str]] = None, selected: Optional[str] = None, inline: bool = False, width: Optional[str] = None):
  input_label = shiny_input_label(id, label)
  options = generate_options(id=id, type='radio', choices=choices, choice_names=choice_names, selected=selected, inline=inline)
  return div(
    input_label, options,
    id=id, style=f"width: {width};" if width else None,
    _class_="form-group shiny-input-radiogroup shiny-input-container" + (" shiny-input-container-inline" if inline else ""),
    # https://www.w3.org/TR/2017/WD-wai-aria-practices-1.1-20170628/examples/radio/radio-1/radio-1.html
    role="radiogroup", aria_labelledby=input_label.get_attr("id")
  )

def generate_options(id, type, choices, choice_names, selected, inline):
  if not choice_names:
    choice_names = list(choices.keys()) if isinstance(choices, dict) else choices
  choices = [v for k, v in choices.items()] if isinstance(choices, dict) else choices
  if type == 'radio' and not selected:
    selected = choices[0]
  return div(
      *[generate_option(id, type, choices[i], choice_names[i], selected, inline) for i in range(len(choices))],
      _class_="shiny-options-group"
    )

def generate_option(id, type, choice, choice_name, selected, inline):
  input = tags.input(
    type=type, name=id, value=choice,
    checked="checked" if selected == choice else None
  )
  if inline:
    return tags.label(input, span(choice_name), _class_=type+"-inline")
  else:
    return div(tags.label(input, span(choice_name)), _class_=type)
