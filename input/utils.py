from htmltools import tags

def shiny_input_label(id: str, label: str = None):
  cls = "control-label" + ("" if label else "shiny-label-null")
  return tags.label(
      label, className = cls,
      id = id + "-label",
      _for = id
  )