import dominate.tags as tags

# TODO: implement icon
def action_button(id, label, *args, icon = None, width = None, **kwargs):  
  b = tags.button(
    label, 
    *args,
    id = id, 
    type = "button",
    className = "btn btn-default action-button",
    **kwargs
  )
  # TODO: reinvent css()/validateCssUnit()?
  if width is not None:
    with b:
      tags.attr(style = f"width:{width};")
  return b

def action_link(id, label, *args, icon = None, **kwargs):
  # TODO: implement bookmarking (restoreInput())?
  return tags.a(
    label, 
    *args,
    id = id, 
    href = "#",
    className = "action-button",
    **kwargs
  )