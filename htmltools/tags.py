import json
import re
from typing import Any, Optional, Dict
from .util import html, html_escape, normalize_text

# TODO: how to do a 'suggested' dependency?
from IPython.core.display import display as idisplay
from IPython.core.display import HTML as ihtml

class tag():
  def __init__(self, *args: Any, name: str, children: Optional[Any] = None, **kwargs: Dict[str, str]) -> None:
    self.name = name
    self.attrs = [kwargs] if kwargs else []
    self.children = list(args)
    if children:
      self.children = self.children + children

  def __call__(self, *args: Any, **kwargs: Dict[str, str]) -> None:
    self.append_attrs(**kwargs)
    self.append_children(*args)
    return self

  def append_attrs(self, **kwargs: Dict[str, str]) -> None:
    if kwargs: self.attrs.append(kwargs)

  def append_children(self, *args: Dict[str, str]) -> None:
    if args: self.children.append(args)

  def as_string(self) -> str:
    return self.render(indent = 0)

  def show(self, renderer: str = "idisplay") -> None:
    if renderer == "idisplay":
      return idisplay(ihtml(self.as_string()))
    else:
      raise Exception(f"Unknown renderer {renderer}")

  def render(self, indent: int = 0, eol: str = '\n') -> str:
    # open tag
    indent_txt = ' ' * indent
    txt = indent_txt + '<' + self.name

    # write attributes
    attrs = self._flatten_attrs()
    for key, val in attrs.items():
      if val is None or False: continue
      # e.g., data_foo -> data-foo
      key = key.replace('_', '-')
      # e.g., className -> class
      # TODO: any more reserved names we need to need to handle?
      key = 'class' if key == 'className' else key
      # escape HTML attr values (unless they're wrapped in HTML())
      val = val if isinstance(val, html) else html_escape(str(val), attr = True)
      txt += f' {key}="{val}"'

    children = [x for x in self.children if x is not None]

    # Early exist for void elements http://dev.w3.org/html5/spec/single-page.html#void-elements
    if len(children) == 0 and self.name in ["area", "base", "br", "col", "command", "embed", "hr", "img", "input", "keygen", "link", "meta", "param", "source", "track", "wbr"]:
      return txt + ' />'

    # Early exit if no children
    txt += '>'
    close = '</' + self.name + '>'
    if len(children) == 0:
      return txt + close

    # Inline a single/empty child text node
    if len(children) == 1 and not isinstance(children[0], tag):
        return txt + normalize_text(str(children[0])) + close

    # Write children
    next_indent = indent + 1
    next_indent_txt = eol + (' ' * next_indent)
    for x in children:
      txt += next_indent_txt;
      if isinstance(x, tag):
        txt += x.render(next_indent, eol)
      else:
        txt += normalize_text(str(x))

    return txt + eol + indent_txt + close

  def __str__(self) -> str:
    return self.render()

  def __repr__(self) -> str:
    return f'<tag {self.name} {len(self.attrs)} attributes {len(self.children)} children>'

  def _flatten_attrs(self) -> Dict[str, str]:
    attrs = {}
    for x in self.attrs:
      for key, val in x.items():
        if val is None: continue
        attrs[key] = self.attrs.get(key) + str(val) if key in attrs else str(val)

    return attrs

class tag_list(tag):
  def __init__(self, *args) -> None:
    tag.__init__(self, *args, name = "")

  def render(self, indent: int = 0, eol: str = '\n') -> str:
    html = tag.render(self, indent, eol)
    html = html.split(eol)
    if len(html) == 1:
      html = re.sub('^<>', '', html[0])
      return re.sub('</>$', '', html)
    else:
      del html[0]
      del html[len(html) - 1]
      html = [re.sub('^  ', '', h) for h in html]
      return eol.join(html)

def tag_factory(name: str) -> tag:
  def __init__(self, *args: Any, **kwargs: Dict[str, str]) -> None:
    tag.__init__(self, *args, name = name, **kwargs)
  return __init__

# Generate a class for each known tag
class tags_(dict):
  def __init__(self) -> None:
    with open('htmltools/known_tags.json') as f:
      known_tags = json.load(f)
      for tag_ in known_tags:
        self[tag_] = type(tag_, (tag, ), {"__init__": tag_factory(name = tag_) })

  def __getattr__(self, name: str) -> Any:
    return self[name]

tags = tags_()