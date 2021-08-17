
from htmltools import *
from typing import Optional, Any

def fluid(*args: Any, title: Optional[str] = None, theme: Optional[str] = None, lang: Optional[str] = None, **kwargs: Any) -> tag_list:
  return bootstrap(
      div(className = "container-fluid", *args, *kwargs),
      title = title,
      theme = theme,
      lang = lang
  )

def bootstrap(*args: Any, title: Optional[str] = None, theme: Optional[str] = None, lang: Optional[str] = None) -> tag_list:
  if title:
    title = tags.head(tags.title(title))
  # TODO: port bslib for custom themes?
  page = tagList(title, *args)
  page.attach_dependency(jquery_lib())
  page.attach_dependency(bootstrap_lib())
  if lang:
    page.append_attrs(lang = lang)
  return page


def jquery_lib() -> html_dependency:
  return htmlDependency(
    name = "jquery",
    version = "3.6.0",
    src = "www/shared",
    package = "prism",
    script = "jquery-3.6.0.min.js",
  )


def bootstrap_lib() -> html_dependency:
  return htmlDependency(
    name = "bootstrap",
    version = "5.0.1",
    src = "www/shared",
    package = "prism",
    script = "bootstrap.bundle.min.js",
    stylesheet = "bootstrap.min.css"
  )