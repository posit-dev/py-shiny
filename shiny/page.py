from htmltools import tags, tag_list, html_document
from htmltools.util import flatten
from typing import Literal, Optional, Any, List
from .html_dependencies import bootstrap_deps, shiny_deps
from .navs import navs_bar
from .input_utils import missing

def page_navbar(*args, title: Optional[str]=None, id: Optional[str]=None, selected: Optional[str]=None,
                position: Literal["static-top", "fixed-top", "fixed-bottom"]="static-top",
                header: Any=None, footer: Any=None,
                bg: Optional[str]=None, inverse: Literal["auto", True, False]="auto",
                collapsible: bool=True, fluid: bool=True,
                window_title: Optional[str]=missing,
                lang: Optional[str]=None) -> html_document:

  # https://github.com/rstudio/shiny/issues/2310
  if title and window_title is missing:
    window_title=flatten(find_characters(title))
    if window_title:
      window_title=tags.title(" ".join(window_title))
    else:
      raise Warning("Unable to infer a `window_title` default from `title`. Consider providing a character string to `window_title`.")
      window_title=None

  return html_document(
    navs_bar(
      *args, title=title, id=id, selected=selected,
      position=position, header=header,
      footer=footer, bg=bg, inverse=inverse,
      collapsible=collapsible, fluid=fluid
    ),
    head=window_title,
    lang=lang
  )

def page_fluid(*args: Any, title: Optional[str]=None, lang: Optional[str]=None, **kwargs: str) -> html_document:
  return page_bootstrap(
    tags.div(_class_="container-fluid", *args, *kwargs),
    title=title,
    lang=lang
  )

# TODO: implement theme (just Bootswatch for now?)
def page_bootstrap(*args: Any, title: Optional[str]=None, lang: Optional[str]=None) -> html_document:
  page=tag_list(bootstrap_deps(), *args)
  head=tags.title(title) if title else None
  return html_document(body=page, head=head, lang=lang)


def find_characters(x):
  if isinstance(x, str):
    return [x]
  elif isinstance(x, list):
    return [y for y in x if isinstance(y, str)]
  else:
    return []
