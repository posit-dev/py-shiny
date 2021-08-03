import dominate.tags as tags

def shiny_input_label(id, label = None):
  cls = "control-label" + ("" if label else "shiny-label-null")
  return tags.label(
      label, className = cls,
      id = id + "-label",
      _for = id
  )