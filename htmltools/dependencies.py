import os
import importlib
from tempfile import TemporaryDirectory
from urllib.parse import quote
from typing import Optional, Union, List, Dict, Callable, Any
from .tags import tags, tag_list
from .util import html


# python version of system.file()
def package_dir(package: str) -> str:
  with TemporaryDirectory():
    pkg_file = importlib.import_module('.', package = package).__file__
    return os.path.dirname(pkg_file)

class html_dependency():
  def __init__(self, name: str, version: str, src: Union[str, Dict[str, str]],
                     script: Optional[Union[str, List[str], List[Dict[str, str]]]] = None,
                     stylesheet: Optional[Union[str, List[str], List[Dict[str, str]]]] = None,
                     package: Optional[str] = None, all_files: bool = False,
                     meta: Optional[List[Dict[str, str]]] = None,
                     head: Optional[str] = None):
    self.name = name
    self.version = version
    self.src = src if isinstance(src, dict) else {"file": src}
    self.script = self._as_dicts(script, "src")
    self.stylesheet = self._as_dicts(stylesheet, "href")
    # Ensures a rel='stylesheet' default
    for i, s in enumerate(self.stylesheet):
      if "rel" not in s: self.stylesheet[i].update({"rel": "stylesheet"})
    self.package = package
    # TODO: implement shiny::createWebDependency()
    self.all_files = all_files
    self.meta = meta if meta else []
    self.head = head
    # TODO: do we need attachments?
    #self.attachment = attachment

  # TODO: do we really need hrefFilter? Seems rmarkdown was the only one that needed it
  # https://github.com/search?l=r&q=%22hrefFilter%22+user%3Acran+language%3AR&ref=searchresults&type=Code&utf8=%E2%9C%93
  def render(self, src_type: str = "file", encode_path: Callable[[str], str] = quote) -> str:
    src = self.src[src_type]
    if not src:
      raise Exception(f"HTML dependency {self.name}@{self.version} has no '{src_type}' definition")

    # Assume href is already URL encoded
    src = encode_path(src) if src_type == "file" else src

    sheets = self.stylesheet.copy()
    for i, s in enumerate(sheets):
      sheets[i].update({"href": encode_path(s["href"])})

    scripts = self.script.copy()
    for i, s in enumerate(scripts):
      scripts[i].update({"src": encode_path(s["src"])})

    metas = [tags.meta(**m) for m in self.meta]
    links = [tags.link(**s) for s in sheets]
    scripts = [tags.script(**s) for s in scripts]
    head = html(self.head) if self.head else None
    return tag_list(*metas, *links, *scripts, head).render()

  def _src_path(self) -> str:
    dir = package_dir(self.package) if self.package else ""
    return os.path.join(dir, self.src)

  def _as_dicts(self, val: Any, attr: str) -> List[Dict[str, str]]:
    if val is None:
      return []
    if isinstance(val, str):
      return [{attr: val}]
    if isinstance(val, list):
      return [{attr: i} if isinstance(i, str) else i for i in val]
    raise Exception(f"Invalid type for {repr(val)} in HTML dependency {self.name}@{self.version}")

  def __repr__(self):
    return f'<html_dependency "{self.name}@{self.version}">'

  def __str__(self):
    return self.render()

