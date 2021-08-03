import dominate.tags as tags

def text(id, container = None, inline = False):
    if not container:
        container = tags.span if inline else tags.div

    return container(id = id, className = "shiny-text-output")

def text_verbatim(id, placeholder = False):
    cls = "class-text-output" + (" noplaceholder" if not placeholder else "")

    return tags.pre(id = id, className = cls)