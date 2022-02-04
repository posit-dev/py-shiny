from htmltools import tags, Tag, TagChildArg


def shiny_input_label(id: str, label: TagChildArg = None) -> Tag:
    cls = "control-label" + ("" if label else " shiny-label-null")
    return tags.label(label, class_=cls, id=id + "-label", for_=id)
