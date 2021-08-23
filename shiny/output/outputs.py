from typing import Callable, Optional
from htmltools import tags, tag

def text(id: str, container: Optional[Callable[[], tag]] = None, inline: bool = False) -> tag:
  if not container:
    container = tags.span if inline else tags.div

  return container(id = id, _class_ = "shiny-text-output")

def text_verbatim(id: str, placeholder: bool = False) -> tag:
  cls = "class-text-output" + (" noplaceholder" if not placeholder else "")

  return tags.pre(id = id, _class_ = cls)