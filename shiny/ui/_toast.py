from __future__ import annotations

__all__ = ("toast", "toast_header", "show_toast", "hide_toast")

import warnings
from typing import TYPE_CHECKING, Any, Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, TagList, TagNode, div, tags

from .._docstring import add_example
from .._typing_extensions import NotRequired
from .._utils import rand_hex
from ..session import require_active_session
from ..session._utils import RenderedDeps
from ._html_deps_shinyverse import components_dependencies
from ._tag import consolidate_attrs

if TYPE_CHECKING:
    from ..session import Session


class ToastPayload(RenderedDeps):
    id: str
    position: str
    autohide: bool
    duration: NotRequired[float]


# ==============================================================================
# Toast
# ==============================================================================


class Toast:
    """A toast notification (internal class)."""

    def __init__(
        self,
        body: TagList,
        header: Optional[ToastHeader | TagNode] = None,
        icon: Optional[TagNode] = None,
        id: Optional[str] = None,
        type: Optional[str] = None,
        duration: Optional[float] = 5000,
        position: str = "top-right",
        closable: bool = True,
        attribs: Optional[dict[str, Any]] = None,
    ):
        self.body = body
        self.header = header
        self.icon = icon
        self.id = id
        self.type = type if type != "error" else "danger"
        self.duration = duration
        self.autohide = duration is not None and duration > 0
        self.position = _normalize_toast_position(position)
        self.closable = closable
        self.attribs = attribs if attribs is not None else {}

    def as_payload(self, session: Session) -> ToastPayload | None:
        """Create the Shiny custom message payload for this toast."""
        # Return None if toast has no content
        if not self.body and self.header is None:
            return None

        id = self.id or _toast_random_id()
        toasted = session._process_ui(self.tagify(id=id))

        payload: ToastPayload = {
            "html": toasted["html"],
            "deps": toasted["deps"],
            "id": id,
            "position": self.position,
            "autohide": self.autohide,
        }

        if self.duration is not None:
            payload["duration"] = self.duration

        return payload

    def tagify(self, id: Optional[str] = None) -> Tag:
        """Convert to HTML Tag object."""
        # Danger type requires more assertive accessibility attributes
        if self.type == "danger":
            role = "alert"
            aria_live = "assertive"
        else:
            role = "status"
            aria_live = "polite"

        classes = ["toast"]
        if self.type:
            classes.append(f"text-bg-{self.type}")

        contents: list[TagChild] = []

        close_button = tags.button(
            type="button",
            class_="btn-close",
            data_bs_dismiss="toast",
            aria_label="Close",
        )

        if self.header is not None:
            if isinstance(self.header, (ToastHeader, TagNode)):
                header = self.header
            else:
                header = toast_header(title=self.header)

            if isinstance(header, ToastHeader):
                header_tag = header.tagify(
                    close_button=close_button if self.closable else None
                )
            else:
                header_tag = div(
                    header,
                    close_button if self.closable else None,
                    class_="toast-header",
                )

            contents.append(header_tag)

        # Close button placement: header if present, otherwise body
        body_has_close_btn = self.header is None and self.closable

        if not body_has_close_btn and self.icon is None:
            body_tag = div({"class": "toast-body"}, self.body)
        else:
            body_contents: list[TagChild] = []

            if self.icon is not None:
                body_contents.append(tags.span(self.icon, class_="toast-body-icon"))

            body_contents.append(
                div({"class": "toast-body-content flex-grow-1"}, self.body)
            )

            if body_has_close_btn:
                body_contents.append(close_button)

            body_tag = div({"class": "toast-body d-flex gap-2"}, *body_contents)

        contents.append(body_tag)

        return div(
            {
                "class": " ".join(classes),
                "id": id or self.id or _toast_random_id(),
            },
            *contents,
            components_dependencies(),
            role=role,
            aria_live=aria_live,
            aria_atomic="true",
            data_bs_autohide="true" if self.autohide else "false",
            **self.attribs,
        )


@add_example()
def toast(
    *args: TagChild | TagAttrs,
    header: Optional[str | ToastHeader | TagNode] = None,
    icon: Optional[TagNode] = None,
    id: Optional[str] = None,
    type: Optional[
        Literal[
            "primary",
            "secondary",
            "success",
            "info",
            "warning",
            "danger",
            "error",
            "light",
            "dark",
        ]
    ] = None,
    duration_s: Optional[int | float] = 5,
    position: str | list[str] | tuple[str, ...] = "top-right",
    closable: bool = True,
    **kwargs: TagAttrValue,
) -> Toast:
    """
    Create a toast notification object.

    Toast notifications are temporary, non-intrusive messages that appear on screen to
    provide feedback to users. They support multiple semantic types, flexible
    positioning, auto-hide with progress bars, and optional headers with icons.

    Parameters
    ----------
    *args
        Body content (HTML elements or strings).
    header
        Optional header content. Can be a string (auto-converted to header), or a
        toast header object from :func:`~shiny.ui.toast_header`.
    icon
        Optional icon element to display in the toast body.
    id
        Optional unique identifier. Auto-generated if None.
    type
        Semantic type for styling. Options are `"primary"`, `"secondary"`, `"success"`,
        `"info"`, `"warning"`, `"danger"`, `"error"` (alias for `"danger"`), `"light"`,
        `"dark"`.
    duration_s
        Auto-hide duration in seconds. Use `None` or `0` to disable auto-hide.
    position
        Screen position. Accepts `"top-left"`, `"top left"`, `["top", "left"]`, etc.
        Valid positions are combinations of (top/middle/bottom) × (left/center/right).
    closable
        Whether to add a close button, allowing the user to close the toast. Defaults to
        `True`. When `False` and auto-hide is disabled, the toast cannot be dismissed by
        the user; use only when appropriate and be certain to close the toast
        programmatically with :func:`~shiny.ui.hide_toast`.
    **kwargs
        Additional HTML attributes for the toast element.

    Returns
    -------
    :
        A toast notification object that can be passed to :func:`~shiny.ui.show_toast`.

    See Also
    --------
    * :func:`~shiny.ui.show_toast`
    * :func:`~shiny.ui.hide_toast`
    * :func:`~shiny.ui.toast_header`

    Example
    -------
    See :func:`~shiny.ui.show_toast`.
    """
    attrs, children = consolidate_attrs(*args, **kwargs)
    body = TagList(*children)

    if isinstance(header, str):
        header = toast_header(header)

    normalized_position = _normalize_toast_position(position)

    return Toast(
        body=body,
        header=header,
        icon=icon,
        id=id,
        type=type,
        duration=duration_s * 1000 if duration_s is not None else None,
        position=normalized_position,
        closable=closable,
        attribs=attrs,
    )


# ==============================================================================
# Toast Header
# ==============================================================================


class ToastHeader:
    """Internal class representing a toast header."""

    def __init__(
        self,
        title: TagNode,
        icon: Optional[TagNode] = None,
        status: Optional[str] = None,
        attribs: Optional[dict[str, Any]] = None,
    ):
        self.title = title
        self.icon = icon
        self.status = status
        self.attribs = attribs or {}

    def tagify(self, close_button: Optional[Tag] = None) -> Tag:
        """Convert to HTML Tag object.

        Parameters
        ----------
        closable
            Whether to include a close button in the header.
        """
        contents: list[TagChild] = []

        if self.icon is not None:
            contents.append(tags.span(self.icon, class_="toast-header-icon"))

        title_classes = "me-auto ms-2" if self.icon is not None else "me-auto"
        contents.append(tags.strong(self.title, class_=title_classes))

        if self.status is not None:
            contents.append(tags.small(self.status, class_="text-muted text-end"))

        if close_button is not None:
            contents.append(close_button)

        return div({"class": "toast-header"}, *contents, **self.attribs)


def toast_header(
    title: TagNode,
    *args: TagChild | TagAttrs,
    icon: Optional[TagNode] = None,
    status: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> ToastHeader:
    """
    Create a structured toast header.

    Parameters
    ----------
    title
        Header title text or HTML element.
    *args
        Additional content to append to title.
    icon
        Optional icon element.
    status
        Optional status text (appears muted/right-aligned, e.g., "just now").
    **kwargs
        Additional HTML attributes for the header element.

    Returns
    -------
    :
        A toast header object.

    Examples
    --------

    See :func:`~shiny.ui.toast` for a complete example, including a toast with a
    header.

    See Also
    --------
    * :func:`~shiny.ui.toast`
    * :func:`~shiny.ui.show_toast`
    """
    attrs, children = consolidate_attrs(*args, **kwargs)

    if children:
        title = TagList(title, *children)

    return ToastHeader(
        title=title,
        icon=icon,
        status=status,
        attribs=attrs,
    )


# ==============================================================================
# Show/Hide Functions
# ==============================================================================


def show_toast(
    toast: str | Toast | Tag | TagList,
    *,
    session: Optional[Session] = None,
) -> str:
    """
    Display a toast notification.

    Toast notifications are temporary, non-intrusive messages that appear on screen.
    They can be used to provide feedback about actions, display brief messages, or
    show status updates without interrupting the user's workflow.

    Parameters
    ----------
    toast
        A toast object from :func:`~shiny.ui.toast`, or a plain string (auto-converted to toast).
    session
        Shiny session object. If not provided, the session is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        The toast ID (for use with :func:`~shiny.ui.hide_toast`), or an empty string if
        the toast has no content (and no action is taken).

    Examples
    --------

    See :func:`~shiny.ui.toast` for a complete example, including showing and hiding
    toast notifications.

    See Also
    --------
    * :func:`~shiny.ui.toast`
    * :func:`~shiny.ui.hide_toast`
    * :func:`~shiny.ui.toast_header`
    """
    session = require_active_session(session)

    the_toast: Toast
    if isinstance(toast, Toast):
        the_toast = toast
    elif isinstance(toast, TagList):
        the_toast = Toast(toast)
    else:
        the_toast = Toast(TagList(toast))

    payload = the_toast.as_payload(session)
    if payload is None:
        warnings.warn("Toast has no content (empty body and no header)", stacklevel=2)
        return ""

    session._send_message_sync({"custom": {"bslib.show-toast": payload}})

    return payload["id"]


def hide_toast(
    id: str | Toast,
    *,
    session: Optional[Session] = None,
) -> str:
    """
    Programmatically hide a toast notification.

    Parameters
    ----------
    id
        Toast ID (returned by :func:`~shiny.ui.show_toast`) or a Toast object with an id.
    session
        Shiny session object. If not provided, the session is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        The toast ID that was hidden.

    See Also
    --------
    * :func:`~shiny.ui.show_toast`
    * :func:`~shiny.ui.toast`


    Examples
    --------

    See :func:`~shiny.ui.toast` for a complete example, including showing and hiding
    toast notifications.
    """
    session = require_active_session(session)

    the_id: str | None

    if isinstance(id, Toast):
        the_id = id.id
    else:
        the_id = id

    if the_id is None:
        raise ValueError("Cannot hide toast without an ID")

    session._send_message_sync({"custom": {"bslib.hide-toast": {"id": the_id}}})

    return the_id


# ==============================================================================
# Helper Functions
# ==============================================================================


def _normalize_toast_position(
    position: str | list[str] | tuple[str, ...] | None,
) -> str:
    """
    Normalize position to kebab-case format.

    Accepts: "top-left", "top left", ["top", "left"], ["left", "top"], etc.
    Returns: "top-left" (always kebab-case)
    Validates: Must have one vertical (top/middle/bottom) and one horizontal (left/center/right)
    """
    if position is None or position == "":
        return "bottom-right"

    if isinstance(position, (list, tuple)):
        position = " ".join(str(p) for p in position)

    parts = position.replace("-", " ").lower().split()

    vertical_options = {"top", "middle", "bottom"}
    horizontal_options = {"left", "center", "right"}

    vertical = None
    horizontal = None

    for part in parts:
        if part in vertical_options:
            if vertical is not None:
                raise ValueError(
                    f"Position cannot have multiple vertical components: {position}"
                )
            vertical = part
        elif part in horizontal_options:
            if horizontal is not None:
                raise ValueError(
                    f"Position cannot have multiple horizontal components: {position}"
                )
            horizontal = part
        else:
            raise ValueError(
                f"Invalid position component '{part}'. "
                f"Valid vertical: {', '.join(sorted(vertical_options))}. "
                f"Valid horizontal: {', '.join(sorted(horizontal_options))}."
            )

    if vertical is None:
        raise ValueError(
            f"Position must include a vertical component (top, middle, or bottom): {position}"
        )
    if horizontal is None:
        raise ValueError(
            f"Position must include a horizontal component (left, center, or right): {position}"
        )

    return f"{vertical}-{horizontal}"


def _toast_random_id() -> str:
    """Generate random toast ID: bslib-toast-{random_hex}"""
    return f"bslib-toast-{rand_hex(8)}"
