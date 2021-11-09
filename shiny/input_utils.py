from typing import Optional

from htmltools import tags, Tag


def shiny_input_label(id: str, label: Optional[str] = None) -> Tag:
    cls = "control-label" + ("" if label else " shiny-label-null")
    return tags.label(label, class_=cls, id=id + "-label", for_=id)
