from htmltools import tags, Tag, div, html, TagChildArg, TagAttrArg
from typing import Optional, Literal, Any
from .utils import run_coro_sync, process_deps
from .shinysession import ShinySession, get_current_session

# TODO: icons
def modal_button(label: str) -> Tag:
    return tags.button(
        # validateIcon(icon),
        label,
        type="button",
        class_="btn btn-default",
        data_dismiss="modal",
        data_bs_dismiss="modal",
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
            div(*args, class_="modal-body", **kwargs),
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
        tags.script(html(js)),
        id="shiny-modal",
        class_="modal fade" if fade else "modal",
        tabindex="-1",
        data_backdrop=backdrop,
        data_bs_backdrop=backdrop,
        data_keyboard=keyboard,
        data_bs_keyboard=keyboard,
    )


def modal_show(modal: Tag, session: Optional[ShinySession] = None):
    if session is None:
        session = get_current_session()
    if session is None:
        raise RuntimeError("No Shiny session found")
    ui = process_deps(modal)
    msg = {"html": ui["html"], "deps": ui["dependencies"]}
    return run_coro_sync(
        session.send_message({"modal": {"type": "show", "message": msg}})
    )


def modal_remove(session: Optional[ShinySession] = None):
    if session is None:
        session = get_current_session()
    return run_coro_sync(
        session.send_message({"modal": {"type": "remove", "message": None}})
    )
