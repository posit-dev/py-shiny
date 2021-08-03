
import dominate as dom
import dominate.tags as tags

def fluid(*args, title = None, theme = None, lang = None, **kwargs):
    return bootstrap(
        tags.div(className = "container-fluid", *args, *kwargs),
        title = title,
        theme = theme,
        lang = lang
    )

def bootstrap(*args, title = None, theme = None, lang = None, **kwargs):
    if not title:
      title = ''
    
    doc = dom.document(title=title)

    if lang:
      doc.set_attribute(lang, lang)

    # TODO: reinvent htmlDependency() (and bslib?)
    with doc.head:
      tags.script(src='https://code.jquery.com/jquery-3.6.0.min.js')
      tags.script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js")
      tags.link(href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css", rel="stylesheet")

    for arg in args:
      if arg:
        doc += arg
    
    return doc