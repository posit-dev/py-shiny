import re
from typing import List

class html(str):
  def __new__(cls, *args: List[str]) -> str:
    return str.__new__(cls, '\n'.join(args))

def html_escape(text: str, attr: bool = False):
  specials = {
    "&": "&amp;",
    ">": "&gt;",
    "<": "&lt;",
  }
  if attr:
    specials.update({
      '"': "&quot;",
      "'": "&apos;",
      '\r': '&#13;',
      '\n': '&#10;'
    })

  if not re.search("|".join(specials), text):
    return text

  for key, value in specials.items():
    text = text.replace(key, value)

  return text


def normalize_text(txt: str):
  return txt if isinstance(txt, html) else html_escape(txt, attr = False)