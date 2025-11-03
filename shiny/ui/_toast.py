from __future__ import annotations

__all__ = ("toast", "toast_header", "show_toast", "hide_toast")

import warnings
from typing import TYPE_CHECKING, Any, Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, TagList, div, tags

from .._docstring import add_example, no_example
from .._utils import rand_hex
from ..session import require_active_session
from ._html_deps_shinyverse import components_dependencies
from ._tag import consolidate_attrs

if TYPE_CHECKING:
    from ..session import Session


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
    # Default position
    if position is None or position == "":
        return "bottom-right"

    # Convert list/tuple to space-separated string
    if isinstance(position, (list, tuple)):
        position = " ".join(str(p) for p in position)

    # Split by hyphens or spaces and normalize case
    parts = position.replace("-", " ").lower().split()

    # Valid components
    vertical_options = {"top", "middle", "bottom"}
    horizontal_options = {"left", "center", "right"}

    # Extract vertical and horizontal components
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

    # Validate we have both components
    if vertical is None:
        raise ValueError(
            f"Position must include a vertical component (top, middle, or bottom): {position}"
        )
    if horizontal is None:
        raise ValueError(
            f"Position must include a horizontal component (left, center, or right): {position}"
        )

    # Return in kebab-case format: vertical-horizontal
    return f"{vertical}-{horizontal}"


def _toast_random_id() -> str:
    """Generate random toast ID: bslib-toast-{random_hex}"""
    return f"bslib-toast-{rand_hex(8)}"


# ==============================================================================
# ToastHeader Class
# ==============================================================================


class ToastHeader:
    """Internal class representing a toast header."""

    def __init__(
        self,
        title: TagChild,
        icon: Optional[TagChild],
        status: Optional[str],
        attribs: dict[str, Any],
    ):
        self.title = title
        self.icon = icon
        self.status = status
        self.attribs = attribs

    def tagify(self, closable: bool = False) -> Tag:
        """Convert to HTML Tag object.

        Parameters
        ----------
        closable
            Whether to include a close button in the header.
        """
        # Build header contents
        contents: list[TagChild] = []

        # Add icon if present
        if self.icon is not None:
            contents.append(tags.span(self.icon, class_="toast-header-icon"))

        # Add title (always present, with margin)
        title_classes = "me-auto ms-2" if self.icon is not None else "me-auto"
        contents.append(tags.strong(self.title, class_=title_classes))

        # Add status if present
        if self.status is not None:
            contents.append(tags.small(self.status, class_="text-muted text-end"))

        # Add close button if closable
        if closable:
            contents.append(
                tags.button(
                    type="button",
                    class_="btn-close",
                    data_bs_dismiss="toast",
                    aria_label="Close",
                )
            )

        return div({"class": "toast-header"}, *contents, **self.attribs)


# ==============================================================================
# Toast Class
# ==============================================================================


class Toast:
    """Internal class representing a toast notification."""

    def __init__(
        self,
        body: TagList,
        header: Optional[ToastHeader | TagChild],
        icon: Optional[TagChild],
        id: Optional[str],
        type: Optional[str],
        duration: Optional[float],
        position: str,
        closable: bool,
        attribs: dict[str, Any],
    ):
        self.body = body
        self.header = header
        self.icon = icon
        self.id = id if id else _toast_random_id()
        self.type = self._normalize_type(type)
        self.duration = duration
        self.autohide = duration is not None and duration > 0
        self.position = _normalize_toast_position(position)
        self.closable = closable
        self.attribs = attribs

    def _normalize_type(self, type: Optional[str]) -> Optional[str]:
        """Normalize type, handling 'error' -> 'danger' alias."""
        if type == "error":
            return "danger"
        return type

    def tagify(self) -> Tag:
        """Convert to HTML Tag object."""
        # Determine accessibility attributes based on type
        if self.type == "danger":
            role = "alert"
            aria_live = "assertive"
        else:
            role = "status"
            aria_live = "polite"

        # Start building classes
        classes = ["toast"]
        if self.type:
            classes.append(f"text-bg-{self.type}")

        # Build toast contents
        contents: list[TagChild] = []

        # Close button for header (if needed)
        close_button = tags.button(
            type="button",
            class_="btn-close",
            data_bs_dismiss="toast",
            aria_label="Close",
        )

        # Build header if present
        if self.header is not None:
            # Check if header is already a ToastHeader or just text/tags
            if isinstance(self.header, str):
                # String header: convert to strong.me-auto
                header_content = tags.strong(self.header, class_="me-auto")
            elif isinstance(self.header, ToastHeader):
                # ToastHeader: use tagify with closable flag
                header_tag = self.header.tagify(closable=self.closable)
                contents.append(header_tag)
                header_content = None  # Already added
            else:
                # Otherwise pass through directly (assume user knows what they're doing)
                header_content = self.header

            # If we have header_content (not already added as ToastHeader), wrap it
            if header_content is not None:
                header_tag = div(
                    {"class": "toast-header"},
                    header_content,
                    close_button if self.closable else None,
                )
                contents.append(header_tag)

        # Build body with optional close button
        # * If header exists, close button goes in header
        # * If no header, close button goes in body (if closable)
        body_has_close_btn = self.header is None and self.closable

        if not body_has_close_btn and self.icon is None:
            # Simple body: no close button, no icon
            body_tag = div({"class": "toast-body"}, self.body)
        else:
            # Complex body: has close button and/or icon
            body_contents: list[TagChild] = []

            # Add icon if present
            if self.icon is not None:
                body_contents.append(tags.span(self.icon, class_="toast-body-icon"))

            # Add body content
            body_contents.append(
                div({"class": "toast-body-content flex-grow-1"}, self.body)
            )

            # Add close button if needed
            if body_has_close_btn:
                body_contents.append(close_button)

            body_tag = div({"class": "toast-body d-flex gap-2"}, *body_contents)

        contents.append(body_tag)

        # Build final toast tag
        return div(
            {"class": " ".join(classes), "id": self.id},
            *contents,
            components_dependencies(),
            role=role,
            aria_live=aria_live,
            aria_atomic="true",
            data_bs_autohide="true" if self.autohide else "false",
            **self.attribs,
        )


# ==============================================================================
# Public Constructor Functions
# ==============================================================================


def toast_header(
    title: TagChild,
    *args: TagChild | TagAttrs,
    icon: Optional[TagChild] = None,
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
        Optional icon element (e.g., from ui.tags.i() or icon library).
    status
        Optional status text (appears muted/right-aligned, e.g., "just now").
    **kwargs
        Additional HTML attributes for the header element.

    Returns
    -------
    :
        A toast header object.

    See Also
    --------
    * :func:`~shiny.ui.toast`
    * :func:`~shiny.ui.show_toast`
    """
    # Use consolidate_attrs to properly handle TagChild | TagAttrs
    attrs, children = consolidate_attrs(*args, **kwargs)

    # Combine title with additional children
    if children:
        title = TagList(title, *children)

    return ToastHeader(
        title=title,
        icon=icon,
        status=status,
        attribs=attrs,
    )


@add_example()
def toast(
    *args: TagChild | TagAttrs,
    header: Optional[str | ToastHeader | TagChild] = None,
    icon: Optional[TagChild] = None,
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
    provide feedback to users. They support multiple semantic types, flexible positioning,
    auto-hide with progress bars, and optional headers with icons.

    Parameters
    ----------
    *args
        Body content (HTML elements or strings). Named arguments become HTML attributes.
    header
        Optional header content. Can be a string (auto-converted to header), a
        ToastHeader object from :func:`~shiny.ui.toast_header`, or any TagChild.
    icon
        Optional icon element to display in the toast body (e.g., from ui.tags.i()
        or icon library). The icon appears in the body regardless of whether a header
        is present.
    id
        Optional unique identifier. Auto-generated if None.
    type
        Semantic type for styling. Options are "primary", "secondary", "success",
        "info", "warning", "danger", "error" (alias for "danger"), "light", "dark".
    duration_s
        Auto-hide duration in seconds. Use None or 0 to disable auto-hide.
    position
        Screen position. Accepts "top-left", "top left", ["top", "left"], etc.
        Valid positions are combinations of (top/middle/bottom) × (left/center/right).
    closable
        Whether to show close button.
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
    # Use consolidate_attrs to properly handle TagChild | TagAttrs
    attrs, children = consolidate_attrs(*args, **kwargs)

    # Process body content
    body = TagList(*children)

    # Convert string header to ToastHeader if needed
    if isinstance(header, str):
        header = toast_header(header)

    # Normalize position
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
# Show/Hide Functions
# ==============================================================================


@add_example()
def show_toast(
    toast: str | Toast,
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
        The toast ID (for use with :func:`~shiny.ui.hide_toast`).

    See Also
    --------
    * :func:`~shiny.ui.toast`
    * :func:`~shiny.ui.hide_toast`
    * :func:`~shiny.ui.toast_header`
    """
    session = require_active_session(session)

    # Convert string to toast if needed
    toast_obj: Toast
    if isinstance(toast, str):
        toast_obj = globals()["toast"](toast)
    else:
        toast_obj = toast

    # Warn if toast has no content
    if not toast_obj.body and toast_obj.header is None:
        warnings.warn("Toast has no content (empty body and no header)")

    # Generate toast HTML
    toast_tag = toast_obj.tagify()

    # Process UI to get HTML and dependencies
    processed = session._process_ui(toast_tag)

    # Build payload with flattened structure (no nested options)
    payload: dict[str, Any] = {
        "html": processed["html"],
        "deps": processed["deps"],
        "id": toast_obj.id,
        "position": toast_obj.position,
        "autohide": toast_obj.autohide,
    }

    # Add delay only if present
    if toast_obj.duration is not None:
        payload["duration"] = toast_obj.duration

    # Send message to client (as a custom message)
    session._send_message_sync({"custom": {"bslib.show-toast": payload}})

    return toast_obj.id


@no_example()
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

    Example
    -------
    See :func:`~shiny.ui.show_toast`.
    """
    session = require_active_session(session)

    # Extract ID from Toast object if needed
    if isinstance(id, Toast):
        id = id.id

    # Send message to client
    session._send_message_sync({"custom": {"bslib.hide-toast": {"id": id}}})

    return id
