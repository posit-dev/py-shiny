__all__ = (
    "modal_button",
    "modal",
    "modal_show",
    "modal_remove",
)

import sys
from typing import Optional, Any

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import tags, Tag, div, HTML, TagChildArg, TagAttrArg

from .._docstring import doc
from ..session import Session, require_active_session
from .._utils import run_coro_sync


@doc(
    """
    Creates a button that will dismiss a :func:`modal` (useful when customising the
    ``footer`` of :func:`modal`).
    """,
    parameters={"kwargs": "Attributes to be applied to the button."},
    returns="A UI element",
    note="See :func:`modal` for an example.",
    see_also=[
        ":func:`~shiny.ui.modal`",
        ":func:`~shiny.ui.modal_show`",
        ":func:`~shiny.ui.modal_remove`",
    ],
)
def modal_button(
    label: TagChildArg, icon: TagChildArg = None, **kwargs: TagChildArg
) -> Tag:
    return tags.button(
        icon,
        label,
        {"class": "btn btn-default"},
        type="button",
        data_dismiss="modal",
        data_bs_dismiss="modal",
        **kwargs
    )


@doc(
    """
    Creates the UI for a modal dialog, using Bootstrap's modal class. Modals are
    typically used for showing important messages, or for presenting UI that requires
    input from the user, such as a user name and/or password input.
    """,
    parameters={
        "args": "UI elements for the body of the modal.",
        "title": "An optional title for the modal dialog.",
        "footer": "UI for footer. Use `None` for no footer.",
        "size": 'One of "s" for small, "m" (the default) for medium, or "l" for large.',
        "easy_close": """
        If ``True``, the modal dialog can be dismissed by clicking outside the dialog box,
        or be pressing the Escape key. If ``False`` (the default), the modal dialog can't be
        dismissed in those ways; instead it must be dismissed by clicking on a
        ``modal_button()``, or from a call to ``modal_remove()`` on the server.
        """,
        "fade": """
        If ``False``, the modal dialog will have no fade-in animation (it will simply
        appear rather than fade in to view).
        """,
        "kwargs": "Attributes to be applied to the modal's body tag.",
    },
    returns="A UI element",
    see_also=[
        ":func:`~shiny.ui.modal_show`",
        ":func:`~shiny.ui.modal_remove`",
        ":func:`~shiny.ui.modal_button`",
    ],
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


@doc(
    "Show a modal dialog.",
    parameters={"modal": "Typically a :func:`modal` instance."},
    returns="None",
    note="See :func:`modal` for an example.",
    see_also=[
        ":func:`~shiny.ui.modal_remove`",
        ":func:`~shiny.ui.modal`",
    ],
)
def modal_show(modal: Tag, session: Optional[Session] = None) -> None:
    session = require_active_session(session)
    msg = session.process_ui(modal)
    run_coro_sync(session.send_message({"modal": {"type": "show", "message": msg}}))


@doc(
    "Remove a modal dialog.",
    returns="None",
    note="See :func:`modal` for an example.",
    see_also=[
        ":func:`~shiny.ui.modal_show`",
        ":func:`~shiny.ui.modal`",
    ],
)
def modal_remove(session: Optional[Session] = None) -> None:
    session = require_active_session(session)
    run_coro_sync(session.send_message({"modal": {"type": "remove", "message": None}}))
