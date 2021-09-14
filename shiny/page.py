
from htmltools import tags, tag_list, html_document, html_dependency
from typing import Optional, Any, List

def page_fluid(*args: Any, title: Optional[str] = None, theme: Optional[str] = None, lang: Optional[str] = None, **kwargs: str) -> html_document:
  return page_bootstrap(
    tags.div(_class_ = "container-fluid", *args, *kwargs),
    title = title,
    theme = theme,
    lang = lang
  )


# TODO: port bslib for custom themes?
def page_bootstrap(*args: Any, title: Optional[str] = None, theme: Optional[str] = None, lang: Optional[str] = None) -> html_document:
  page = tag_list(*shiny_deps(), *args)
  head = tags.title(title) if title else None
  return html_document(body = page, head = head, lang = lang)


def shiny_deps() -> List[html_dependency]:
  return [
    jquery_lib(),
    bootstrap_deps(), # TODO: remove bootstrap dependency once we have an htmlTemplate() equivalent
    html_dependency(
      name = "shiny",
      version = "0.0.1",
      package = "shiny",
      src = "www/shared",
      script = "shiny.min.js",
      stylesheet = "shiny.min.css"
    )
  ]

def bootstrap_deps() -> html_dependency:
  return html_dependency(
    name = "bootstrap",
    version = "5.0.1",
    src = "www/shared/bootstrap",
    package = "shiny",
    script = "bootstrap.bundle.min.js",
    stylesheet = "bootstrap.min.css"
  )

def jquery_lib() -> html_dependency:
  return html_dependency(
    name = "jquery",
    version = "3.6.0",
    package = "shiny",
    src = "www/shared/jquery",
    script = "jquery-3.6.0.min.js",
  )
