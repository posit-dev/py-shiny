from typing import Callable, Optional
from htmltools import tags, tag

def text(id, container: Optional[Callable[[], tag]] = None, inline: bool = False):
    if not container:
        container = tags.span if inline else tags.div

    return container(id = id, className = "shiny-text-output")

def text_verbatim(id: str, placeholder: bool = False):
    cls = "class-text-output" + (" noplaceholder" if not placeholder else "")

    return tags.pre(id = id, className = cls)