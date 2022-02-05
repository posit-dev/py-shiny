import sys
from typing import Optional, Any

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import tags, Tag, div, HTML, TagChildArg, TagAttrArg

from ..utils import run_coro_sync
from ..session import Session, _require_active_session, _process_deps


def modal_button(label: str, icon: TagChildArg = None, **kwargs: TagChildArg) -> Tag:
    return tags.button(
        icon,
        label,
        {"class": "btn btn-default"},
        type="button",
        data_dismiss="modal",
        data_bs_dismiss="modal",
        **kwargs
    )


def modal(
    *args: TagChildArg,
    title: Optional[str] = None,
    footer: Any = modal_button("Dismiss"),
    size: Literal["m", "s", "l", "xl"] = "m",
    easy_close: bool = False,
    fade: bool = True,
    **kwargs: TagAttrArg
) -> Tag:

    title_div = None
    if title:
        title_div = div(tags.h4(title, class_="modal-title"), class_="modal-header")

    if footer:
        footer = div(footer, class_="modal-footer")

    dialog = div(
        div(
            title_div,
            div({"class": "modal-body"}, *args, **kwargs),
            footer,
            class_="modal-content",
        ),
        class_="modal-dialog"
        + ({"s": " modal-sm", "l": " modal-lg", "xl": " modal-xl"}.get(size, "")),
    )

    # jQuery plugin doesn't work in Bootstrap 5, but vanilla JS doesn't work in Bootstrap 4 :sob:
    js = "\n".join(
        [
            "if (window.bootstrap && !window.bootstrap.Modal.VERSION.match(/^4\\. /)) {",
            "  var modal=new bootstrap.Modal(document.getElementById('shiny-modal'))",
            "  modal.show()",
            "} else {",
            "  $('#shiny-modal').modal().focus()",
            "}",
        ]
    )

    backdrop = None if easy_close else "static"
    keyboard = None if easy_close else "false"

    return div(
        dialog,
        tags.script(HTML(js)),
        id="shiny-modal",
        class_="modal fade" if fade else "modal",
        tabindex="-1",
        data_backdrop=backdrop,
        data_bs_backdrop=backdrop,
        data_keyboard=keyboard,
        data_bs_keyboard=keyboard,
    )


def modal_show(modal: Tag, session: Optional[Session] = None) -> None:
    session = _require_active_session(session)
    msg = _process_deps(modal)
    run_coro_sync(session.send_message({"modal": {"type": "show", "message": msg}}))


def modal_remove(session: Optional[Session] = None) -> None:
    session = _require_active_session(session)
    run_coro_sync(session.send_message({"modal": {"type": "remove", "message": None}}))
