from __future__ import annotations

__all__ = (
    "Offcanvas",
    "offcanvas",
    "show_offcanvas",
    "hide_offcanvas",
    "toggle_offcanvas",
)

import warnings
from typing import TYPE_CHECKING, Literal, Optional, Union

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, TagList, tags

from .._docstring import add_example, no_example
from .._namespaces import resolve_id_or_none
from .._utils import rand_hex
from ..session import require_active_session
from ._html_deps_shinyverse import components_dependencies
from ._tag import consolidate_attrs
from .css import as_css_unit

if TYPE_CHECKING:
    from htmltools import Tagified

    from ..session import Session

# Maps user-supplied placement (including start/end aliases) to Bootstrap class suffix.
# The BS class is stored on Offcanvas and used directly in tagify().
_PLACEMENT_BS: dict[str, str] = {
    "right": "end",
    "end": "end",
    "left": "start",
    "start": "start",
    "top": "top",
    "bottom": "bottom",
}

_HORIZONTAL_PLACEMENTS: frozenset[str] = frozenset({"start", "end"})


@no_example()
class Offcanvas:
    """
    An offcanvas panel object.

    Class returned from :func:`~shiny.ui.offcanvas`. Do not use this class
    directly. Instead, pass the :func:`~shiny.ui.offcanvas` object to a layout
    function or display it with :func:`~shiny.ui.show_offcanvas`.

    Parameters
    ----------
    children
        The body content for the offcanvas panel.
    attrs
        Additional HTML attributes for the root element.
    title
        A title displayed in the offcanvas header.
    footer
        UI content for the footer area.
    trigger
        A UI element that toggles the offcanvas when clicked.
    id
        An optional ID for the offcanvas element.
    placement
        Which side of the screen the offcanvas slides in from.
    width
        CSS width (for left/right placement).
    height
        CSS height (for top/bottom placement).
    close_button
        Whether to include a close button in the header.
    backdrop
        Bootstrap backdrop behavior.
    scroll
        Whether to allow body scrolling when the offcanvas is open.
    keyboard
        Whether to close on Escape key.
    """

    def __init__(
        self,
        *,
        children: list[TagChild],
        attrs: TagAttrs,
        title: TagChild,
        footer: TagChild,
        trigger: TagChild,
        id: Optional[str],
        placement: str,
        width: Optional[str],
        height: Optional[str],
        close_button: bool,
        backdrop: Union[bool, Literal["static"]],
        scroll: bool,
        keyboard: bool,
    ) -> None:
        self.children = children
        self.attrs = attrs
        self.title = title
        self.footer = footer
        self.trigger = trigger
        self.id = id
        self.placement = placement
        self.width = width
        self.height = height
        self.close_button = close_button
        self.backdrop: Union[bool, Literal["static"]] = backdrop
        self.scroll = scroll
        self.keyboard = keyboard

    def tagify(self) -> Tagified:
        if self.id is None and self.trigger is None:
            raise ValueError(
                "An `offcanvas()` requires either `id` or `trigger` to be set."
            )

        has_aria_label = "aria-label" in self.attrs or "aria-labelledby" in self.attrs
        if self.title is None and not has_aria_label:
            warnings.warn(
                "An `offcanvas()` without a `title` should have an `aria-label` or "
                "`aria-labelledby` attribute for accessibility.",
                stacklevel=2,
            )

        the_id = self.id if self.id is not None else rand_hex(8)

        class_ = f"offcanvas offcanvas-{self.placement}"

        backdrop_attr: Optional[str] = None
        if self.backdrop is False:
            backdrop_attr = "false"
        elif self.backdrop == "static":
            backdrop_attr = "static"

        scroll_attr: Optional[str] = "true" if self.scroll else None
        keyboard_attr: Optional[str] = "false" if not self.keyboard else None

        style_parts: list[str] = []
        if self.width is not None:
            style_parts.append(f"--bs-offcanvas-width: {self.width}")
        if self.height is not None:
            style_parts.append(f"--bs-offcanvas-height: {self.height}")
        style = "; ".join(style_parts) if style_parts else None

        header_children: list[TagChild] = []
        if self.title is not None:
            header_children.append(
                tags.div(
                    self.title,
                    class_="offcanvas-title",
                    id=f"{the_id}-title",
                )
            )
        if self.close_button:
            header_children.append(
                tags.button(
                    type="button",
                    class_="btn-close",
                    data_bs_dismiss="offcanvas",
                    aria_label="Close",
                )
            )

        header: Optional[Tag] = None
        if header_children:
            header = tags.header(*header_children, class_="offcanvas-header")

        body = tags.div(*self.children, class_="offcanvas-body")

        footer_el: Optional[Tag] = None
        if self.footer is not None:
            footer_el = tags.footer(self.footer, class_="offcanvas-footer")

        aria_labelledby = f"{the_id}-title" if self.title is not None else None

        offcanvas_el = Tag(
            "bslib-offcanvas",
            components_dependencies(),
            header,
            body,
            footer_el,
            self.attrs,
            id=the_id,
            class_=class_,
            tabindex="-1",
            aria_labelledby=aria_labelledby,
            data_bs_backdrop=backdrop_attr,
            data_bs_scroll=scroll_attr,
            data_bs_keyboard=keyboard_attr,
            style=style,
        )

        if self.trigger is not None:
            trigger = self.trigger
            if isinstance(trigger, str):
                trigger = tags.span(trigger)

            if isinstance(trigger, TagList):
                last = trigger[-1]
                if isinstance(last, Tag):
                    last.attrs["data-bs-toggle"] = "offcanvas"
                    last.attrs["data-bs-target"] = f"#{the_id}"
                    last.attrs["aria-controls"] = the_id
                elif isinstance(last, str):
                    trigger[-1] = tags.span(
                        last,
                        **{
                            "data-bs-toggle": "offcanvas",
                            "data-bs-target": f"#{the_id}",
                            "aria-controls": the_id,
                        },
                    )
                else:
                    raise ValueError(
                        "The last element of a `TagList` trigger must be a `Tag` or "
                        f"`str`, not {type(last).__name__!r}."
                    )
            elif isinstance(trigger, Tag):
                trigger.attrs["data-bs-toggle"] = "offcanvas"
                trigger.attrs["data-bs-target"] = f"#{the_id}"
                trigger.attrs["aria-controls"] = the_id
            else:
                raise ValueError(
                    "`trigger` must be a `Tag`, `TagList`, or `str`, "
                    f"not {type(trigger).__name__!r}."
                )

            return TagList(trigger, offcanvas_el).tagify()

        return offcanvas_el.tagify()


@add_example()
def offcanvas(
    *args: TagChild,
    title: TagChild = None,
    footer: TagChild = None,
    trigger: TagChild = None,
    id: Optional[str] = None,
    placement: Literal["right", "left", "top", "bottom"] = "right",
    width: Optional[Union[int, float, str]] = None,
    height: Optional[Union[int, float, str]] = None,
    close_button: bool = True,
    backdrop: Union[bool, Literal["static"]] = True,
    scroll: bool = False,
    keyboard: bool = True,
    **kwargs: TagAttrValue,
) -> Offcanvas:
    """
    Create an offcanvas panel.

    An offcanvas panel slides in from the edge of the screen and is used to
    display additional content without navigating away from the page. It can be
    shown programmatically via :func:`~shiny.ui.show_offcanvas` or triggered
    by a UI element passed to ``trigger``.

    Parameters
    ----------
    *args
        UI elements for the body of the offcanvas panel.
    title
        A title displayed in the offcanvas header. When provided, it is also
        used as the accessible label for the panel via ``aria-labelledby``.
    footer
        UI content for the footer area of the offcanvas panel.
    trigger
        A UI element that toggles the offcanvas when clicked (e.g., an action
        button). The trigger and offcanvas are returned as siblings in a
        :class:`~htmltools.TagList`.
    id
        A string ID for the offcanvas element. Required if you want to use
        :func:`~shiny.ui.hide_offcanvas` or :func:`~shiny.ui.toggle_offcanvas`.
    placement
        Which side of the screen the panel slides in from: ``"right"``
        (default), ``"left"``, ``"top"``, or ``"bottom"``.
    width
        A CSS length unit for the panel width. Only applies to ``"left"`` and
        ``"right"`` placement.
    height
        A CSS length unit for the panel height. Only applies to ``"top"`` and
        ``"bottom"`` placement.
    close_button
        Whether to include a close button in the offcanvas header.
    backdrop
        Controls the Bootstrap backdrop behavior. ``True`` (default) shows a
        backdrop and allows clicking outside to close; ``"static"`` shows a
        backdrop but does not close on outside click; ``False`` shows no backdrop.
    scroll
        Whether to allow the page body to scroll when the offcanvas is open.
    keyboard
        Whether pressing the Escape key closes the offcanvas.
    **kwargs
        Additional HTML attributes applied to the root ``<bslib-offcanvas>`` element.

    Returns
    -------
    :
        An :class:`~shiny.ui.Offcanvas` object.

    See Also
    --------
    * :func:`~shiny.ui.show_offcanvas`
    * :func:`~shiny.ui.hide_offcanvas`
    * :func:`~shiny.ui.toggle_offcanvas`
    """
    attrs, children = consolidate_attrs(*args, **kwargs)

    if placement not in _PLACEMENT_BS:
        raise ValueError(
            f"`placement` must be one of 'right', 'left', 'top', or 'bottom', "
            f"not '{placement}'."
        )

    bs_placement = _PLACEMENT_BS[placement]

    resolved_id = resolve_id_or_none(id)

    width_css: Optional[str] = None
    height_css: Optional[str] = None

    if width is not None:
        if bs_placement not in _HORIZONTAL_PLACEMENTS:
            warnings.warn(
                "`width` is only valid for `placement='left'` or `placement='right'`. "
                "It will be ignored.",
                stacklevel=2,
            )
        else:
            width_css = as_css_unit(width)

    if height is not None:
        if bs_placement in _HORIZONTAL_PLACEMENTS:
            warnings.warn(
                "`height` is only valid for `placement='top'` or `placement='bottom'`. "
                "It will be ignored.",
                stacklevel=2,
            )
        else:
            height_css = as_css_unit(height)

    return Offcanvas(
        children=children,
        attrs=attrs,
        title=title,
        footer=footer,
        trigger=trigger,
        id=resolved_id,
        placement=bs_placement,
        width=width_css,
        height=height_css,
        close_button=close_button,
        backdrop=backdrop,
        scroll=scroll,
        keyboard=keyboard,
    )


@add_example()
def show_offcanvas(
    offcanvas: Offcanvas,
    *,
    session: Optional[Session] = None,
) -> str:
    """
    Show an offcanvas panel.

    Programmatically displays an :func:`~shiny.ui.offcanvas` panel in the
    user's session by inserting its HTML into the page.

    Parameters
    ----------
    offcanvas
        An :class:`~shiny.ui.Offcanvas` object created by :func:`~shiny.ui.offcanvas`.
    session
        The :class:`~shiny.Session` to show the panel in. If not provided,
        the session is inferred via :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        The local (pre-namespace) ID of the displayed panel.

    Note
    ----
    If a panel with the same ``id`` is already present on the page,
    ``show_offcanvas()`` simply reveals it — the content is not re-rendered.
    To update an id'd panel's content, update the reactive outputs it contains
    rather than calling ``show_offcanvas()`` again.

    See Also
    --------
    * :func:`~shiny.ui.offcanvas`
    * :func:`~shiny.ui.hide_offcanvas`
    * :func:`~shiny.ui.toggle_offcanvas`
    """
    the_session = require_active_session(session)

    local_id = offcanvas.id if offcanvas.id is not None else rand_hex(8)
    temporary = offcanvas.id is None
    namespaced_id = the_session.ns(local_id)

    offcanvas_with_id = Offcanvas(
        children=offcanvas.children,
        attrs=offcanvas.attrs,
        title=offcanvas.title,
        footer=offcanvas.footer,
        trigger=None,
        id=namespaced_id,
        placement=offcanvas.placement,
        width=offcanvas.width,
        height=offcanvas.height,
        close_button=offcanvas.close_button,
        backdrop=offcanvas.backdrop,
        scroll=offcanvas.scroll,
        keyboard=offcanvas.keyboard,
    )

    rendered = offcanvas_with_id.tagify()
    processed = the_session._process_ui(rendered)

    payload = {
        "html": processed["html"],
        "deps": processed["deps"],
        "id": namespaced_id,
        "temporary": temporary,
    }

    the_session._send_message_sync({"custom": {"bslib.show-offcanvas": payload}})

    return local_id


@add_example(ex_dir="../api-examples/offcanvas")
def hide_offcanvas(
    id: Union[str, Offcanvas],
    *,
    session: Optional[Session] = None,
) -> None:
    """
    Hide an offcanvas panel.

    Parameters
    ----------
    id
        The ID of the offcanvas panel (a string) or an :class:`~shiny.ui.Offcanvas`
        object with an ``id`` set.
    session
        The :class:`~shiny.Session` to use. If not provided, the session is
        inferred via :func:`~shiny.session.get_current_session`.

    See Also
    --------
    * :func:`~shiny.ui.offcanvas`
    * :func:`~shiny.ui.show_offcanvas`
    * :func:`~shiny.ui.toggle_offcanvas`
    """
    if isinstance(id, Offcanvas):
        if id.id is None:
            raise ValueError(
                "Cannot hide an `offcanvas()` without an `id`. "
                "Provide an `id` when creating the offcanvas."
            )
        the_id = id.id
    else:
        the_id = id

    the_session = require_active_session(session)

    def callback() -> None:
        the_session.send_input_message(the_id, {"method": "hide"})

    the_session.on_flush(callback, once=True)


@add_example(ex_dir="../api-examples/offcanvas")
def toggle_offcanvas(
    id: str,
    show: Optional[bool] = None,
    *,
    session: Optional[Session] = None,
) -> None:
    """
    Toggle an offcanvas panel's visibility.

    Parameters
    ----------
    id
        The ID of the offcanvas panel.
    show
        If ``None`` (default), toggle the current state. If ``True``, show the
        panel. If ``False``, hide the panel.
    session
        The :class:`~shiny.Session` to use. If not provided, the session is
        inferred via :func:`~shiny.session.get_current_session`.

    See Also
    --------
    * :func:`~shiny.ui.offcanvas`
    * :func:`~shiny.ui.show_offcanvas`
    * :func:`~shiny.ui.hide_offcanvas`
    """
    if show is None:
        value = "toggle"
    elif show:
        value = "show"
    else:
        value = "hide"

    the_session = require_active_session(session)

    def callback() -> None:
        the_session.send_input_message(id, {"method": "toggle", "value": value})

    the_session.on_flush(callback, once=True)
