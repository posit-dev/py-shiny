from htmltools import *
from typing import Optional, Literal, Any, Union
from .utils import run_coro_sync, process_deps
from .shinysession import ShinySession, get_current_session

# TODO: icons
def modal_button(label: str) -> tag:
  return tags.button(
      #validateIcon(icon),
      label, type="button",
      _class_="btn btn-default",
      data_dismiss="modal",
      data_bs_dismiss="modal",
  )

# TODO: maybe this should be a class with show()/remove() methods?
def modal(*args, title: Optional[str]=None, footer: Any=modal_button("Dismiss"),
          size: Literal["m", "s", "l", "xl"]="m", easy_close: bool=False, fade: bool=True, **kwargs) -> tag:

      if title:
          title = div(tags.h4(title, _class_="modal-title"), _class_="modal-header")

      if footer:
          footer = div(footer, _class_="modal-footer")

      dialog = div(
          div(
              title,
              div(*args, _class_="modal-body", **kwargs),
              footer,
              _class_="modal-content"
          ),
          _class_="modal-dialog" + ({"s": " modal-sm", "l": " modal-lg", "xl": " modal-xl"}.get(size, ''))
      )

      # jQuery plugin doesn't work in Bootstrap 5, but vanilla JS doesn't work in Bootstrap 4 :sob:
      js = "\n".join([
          "if (window.bootstrap && !window.bootstrap.Modal.VERSION.match(/^4\\. /)) {",
          "  var modal=new bootstrap.Modal(document.getElementById('shiny-modal'))",
          "  modal.show()",
          "} else {",
          "  $('#shiny-modal').modal().focus()",
          "}"
      ])

      backdrop = None if easy_close else "static"
      keyboard = None if easy_close else "false"

      return div(
          dialog,
          tags.script(html(js)),
          id="shiny-modal",
          _class_="modal fade" if fade else "modal",
          tabindex="-1",
          data_backdrop=backdrop,
          data_bs_backdrop=backdrop,
          data_keyboard=keyboard,
          data_bs_keyboard=keyboard
      )


def modal_show(modal: tag, session: Optional[ShinySession] = None):
    if session is None:
        session = get_current_session()
    ui = process_deps(modal)
    msg = {"html": ui['html'], "deps": ui['dependencies']}
    return run_coro_sync(session.send_message({"modal": {"type": "show", "message": msg}}))


def modal_remove(session: Optional[ShinySession] = None):
    if session is None:
        session = get_current_session()
    return run_coro_sync(session.send_message({"modal": {"type": "remove", "message": None}}))
