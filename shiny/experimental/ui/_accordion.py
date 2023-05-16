from __future__ import annotations

import random
from typing import Optional, TypeVar

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css, tags

from ..._typing_extensions import Literal
from ..._utils import drop_none
from ...session import Session, require_active_session
from ...types import MISSING, MISSING_TYPE
from ._css import CssUnit, validate_css_unit
from ._htmldeps import accordion_dependency
from ._utils import consolidate_attrs


class AccordionPanel:
    _args: tuple[TagChild | TagAttrs, ...]
    _kwargs: dict[str, TagAttrValue]

    _data_value: str  # Read within `accordion()`
    _icon: TagChild | None
    _title: TagChild | None
    _id: str | None

    _is_open: bool  # Set within `accordion()`
    _is_multiple: bool  # Set within `accordion()`

    def __init__(
        self,
        *args: TagChild | TagAttrs,
        data_value: str,
        icon: TagChild | None,
        title: TagChild | None,
        id: str | None,
        **kwargs: TagAttrValue,
    ):
        self._args = args
        self._data_value = data_value
        self._icon = icon
        self._title = title
        self._id = id
        self._kwargs = kwargs
        self._is_multiple = False
        self._is_open = True

    def resolve(self) -> Tag:
        btn_attrs = {}
        if self._is_open:
            btn_attrs["aria-expanded"] = "true"
        else:
            btn_attrs["class"] = "collapsed"
            btn_attrs["aria-expanded"] = "false"

        if not self._is_multiple:
            btn_attrs["data-bs-parent"] = f"#{self._id}"

        btn = tags.button(
            {
                "class": "accordion-button",
                "type": "button",
                "data-bs-toggle": "collapse",
                "data-bs-target": f"#{self._id}",
                "aria-controls": self._id,
            },
            btn_attrs,
            # Always include an .accordion-icon container to simplify accordion_panel_update() logic
            tags.div({"class": "accordion-icon"}, self._icon),
            tags.div({"class": "accordion-title"}, self._title),
        )

        return tags.div(
            {
                "class": "accordion-item",
                "data-value": self._data_value,
            },
            # Use a <span.h2> instead of <h2> so that it doesn't get included in rmd/pkgdown/qmd TOC
            # TODO-bslib: can we provide a way to put more stuff in the header? Like maybe some right-aligned controls?
            tags.span(
                {"class": "accordion-header h2"},
                btn,
            ),
            tags.div(
                {
                    "id": self._id,
                    "class": "accordion-collapse collapse",
                },
                {"class": "show"} if self._is_open else None,
                tags.div({"class": "accordion-body"}, *self._args, **self._kwargs),
            ),
        )

    def tagify(self) -> Tag:
        return self.resolve().tagify()


# Create a vertically collapsing accordion
#
# @param ... Named arguments become attributes on the `<div class="accordion">`
#   element. Unnamed arguments should be `accordion_panel()`s.
# @param id If provided, you can use `input$id` in your server logic to
#   determine which of the `accordion_panel()`s are currently active. The value
#   will correspond to the `accordion_panel()`'s `value` argument.
# @param open A character vector of `accordion_panel()` `value`s to open
#   (i.e., show) by default. The default value of `NULL` will open the first
#   `accordion_panel()`. Use a value of `TRUE` to open all (or `FALSE` to
#   open none) of the items. It's only possible to open more than one panel
#   when `multiple=TRUE`.
# @param multiple Whether multiple `accordion_panel()` can be `open` at once.
# @param class Additional CSS classes to include on the accordion div.
# @param width,height Any valid CSS unit; for example, height="100%".
#
# @references <https://getbootstrap.com/docs/5.2/components/accordion/>
#
# @export
# @seealso [accordion_panel_set()]
# @examples
#
# items <- lapply(LETTERS, function(x) {
#   accordion_panel(paste("Section", x), paste("Some narrative for section", x))
# })
#
# # First shown by default
# accordion(!!!items)
# # Nothing shown by default
# accordion(!!!items, open = FALSE)
# # Everything shown by default
# accordion(!!!items, open = TRUE)
#
# # Show particular sections
# accordion(!!!items, open = "Section B")
# accordion(!!!items, open = c("Section A", "Section B"))
#
# # Provide an id to create a shiny input binding
# if (interactive()) {
#   library(shiny)
#
#   ui <- page_fluid(
#     accordion(!!!items, id = "acc")
#   )
#
#   server <- function(input, output) {
#     observe(print(input$acc))
#   }
#
#   shinyApp(ui, server)
# }
#
def accordion(
    *args: AccordionPanel | TagAttrs,
    id: Optional[str] = None,
    open: Optional[bool | str | list[str]] = None,
    multiple: bool = True,
    class_: Optional[str] = None,
    width: Optional[CssUnit] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    # TODO-bookmarking: Restore input here
    # open = restore_input(id = id, default = open)

    attrs, panels = consolidate_attrs(*args)
    for panel in panels:
        if not isinstance(panel, AccordionPanel):
            raise TypeError(
                "All `accordion(*args)` must be of type `AccordionPanel` which can be created using `accordion_panel()`"
            )

    is_open: list[bool] = []
    if open is None:
        is_open = [False for _ in panels]
    elif isinstance(open, bool):
        is_open = [True for _ in panels]
    else:
        if not isinstance(open, list):
            open = [open]
        #
        is_open = [panel._data_value in open for panel in panels]

    # Open the first panel by default
    if open is not False and len(is_open) > 0 and not any(is_open):
        is_open[0] = True

    if (not multiple) and sum(is_open) > 1:
        raise ValueError("Can't select more than one panel when `multiple = False`")

    # Since multiple=False requires an id, we always include one,
    # but only create a binding when it is provided
    binding_class_value: TagAttrs | None = None
    if id is None:
        id = f"bslib-accordion-{random.randint(1000, 10000)}"
        binding_class_value = None
    else:
        binding_class_value = {"class": "bslib-accordion-input"}

    for panel, open in zip(panels, is_open):
        panel._is_multiple = multiple
        panel._is_open = open

    panel_tags = [panel.resolve() for panel in panels]

    tag = tags.div(
        {
            "id": id,
            "class": "accordion",
            "style": css(
                width=validate_css_unit(width), height=validate_css_unit(height)
            ),
        },
        # just for ease of identifying autoclosing client-side
        {"class": "autoclose"} if not multiple else None,
        binding_class_value,
        {"class": class_} if class_ else None,
        accordion_dependency(),
        *attrs,
        *panel_tags,
        **kwargs,
    )
    return tag


# @rdname accordion
# @param title A title to appear in the `accordion_panel()`'s header.
# @param value A character string that uniquely identifies this panel.
# @param icon A [htmltools::tag] child (e.g., [bsicons::bs_icon()]) which is positioned just before the `title`.
# @export
def accordion_panel(
    title: TagChild,
    *body: TagChild | TagAttrs,
    value: Optional[str] | MISSING_TYPE = MISSING,
    icon: Optional[TagChild] = None,
    **attrs: TagAttrValue,
) -> AccordionPanel:
    if value is MISSING:
        if isinstance(title, str):
            value = title
        else:
            raise ValueError("If `title` is not a string, `value` must be provided")
        value = title
    if not isinstance(value, str):
        raise TypeError("`value` must be a string")

    id = f"bslib-accordion-panel-{random.randint(1000, 10000)}"

    return AccordionPanel(
        *body,
        data_value=value,
        icon=icon,
        title=title,
        id=id,
        **attrs,
    )


# Send message before the next flush since things like remove/insert may
# remove/create input/output values. Also do this for set/open/close since,
# you might want to open a panel after inserting it.
def send_panel_message(
    id: str,
    session: Session | None,
    **kwargs: object,
) -> None:
    message = drop_none(kwargs)
    session = require_active_session(session)
    session.on_flush(lambda: session.send_input_message(id, message), once=True)


# Dynamically update accordions
#
# Dynamically (i.e., programmatically) update/modify [`accordion()`]s in a
# Shiny app. These functions require an `id` to be provided to the
# `accordion()` and must also be called within an active Shiny session.
#
# @param id an character string that matches an existing [accordion()]'s `id`.
# @param values either a character string (used to identify particular
#   [accordion_panel()](s) by their `value`) or `TRUE` (i.e., all `values`).
# @param session a shiny session object (the default should almost always be
#   used).
#
# @describeIn accordion_panel_set same as `accordion_panel_open()`, except it
#   also closes any currently open panels.
# @export
def _accordion_panel_action(
    *,
    id: str,
    method: str,
    values: bool | str | list[str],
    session: Session | None,
) -> None:
    if not isinstance(values, bool):
        if not isinstance(values, list):
            values = [values]
        assert_list_str(values)

    send_panel_message(
        id,
        session,
        method=method,
        values=values,
    )


def accordion_panel_set(
    id: str,
    values: bool | str | list[str],
    session: Optional[Session] = None,
) -> None:
    _accordion_panel_action(id=id, method="set", values=values, session=session)


# @describeIn accordion_panel_set open [accordion_panel()]s.
# @export
def accordion_panel_open(
    id: str,
    values: bool | str | list[str],
    session: Optional[Session] = None,
) -> None:
    _accordion_panel_action(id=id, method="open", values=values, session=session)


# @describeIn accordion_panel_set close [accordion_panel()]s.
# @export
def accordion_panel_close(
    id: str,
    values: bool | str | list[str],
    session: Optional[Session] = None,
) -> None:
    _accordion_panel_action(id=id, method="close", values=values, session=session)


# @param panel an [accordion_panel()].
# @param target The `value` of an existing panel to insert next to. If
#   removing: the `value` of the [accordion_panel()] to remove.
# @param position Should `panel` be added before or after the target? When
#   `target` is `NULL` (the default), `"after"` will append after the last
#   panel and `"before"` will prepend before the first panel.
#
# @describeIn accordion_panel_set insert a new [accordion_panel()]
# @export
def accordion_panel_insert(
    id: str,
    panel: AccordionPanel,
    target: Optional[str] = None,
    position: Literal["after", "before"] = "after",
    session: Optional[Session] = None,
) -> None:
    if position not in ("after", "before"):
        raise ValueError("`position` must be either 'after' or 'before'")
    session = require_active_session(session)
    send_panel_message(
        id,
        session,
        method="insert",
        panel=session._process_ui(panel.resolve()),
        target=None if target is None else assert_str(target),
        position=position,
    )


# @describeIn accordion_panel_set remove [accordion_panel()]s.
# @export
def accordion_panel_remove(
    id: str,
    target: str | list[str],
    session: Optional[Session] = None,
) -> None:
    if not isinstance(target, list):
        target = [target]

    send_panel_message(
        id,
        session,
        method="remove",
        target=assert_list_str(target),
    )


# @describeIn accordion_panel_set update a [accordion_panel()].
# @inheritParams accordion_panel
# @export
def accordion_panel_update(
    id: str,
    target: str,
    *body: TagChild,
    title: TagChild | None | MISSING_TYPE = MISSING,
    value: str | None | MISSING_TYPE = MISSING,
    icon: TagChild | None | MISSING_TYPE = MISSING,
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)
    T = TypeVar("T")

    def missing_none_x(x: T | None | MISSING_TYPE) -> T | Literal[""] | None:
        if isinstance(x, MISSING_TYPE):
            return None
        if x is None:
            return ""
        return x

    title = missing_none_x(title)
    value = missing_none_x(value)
    icon = missing_none_x(icon)
    send_panel_message(
        id,
        session,
        method="update",
        target=assert_str(target),
        value=None if value is None else assert_str(value),
        body=None if len(body) == 0 else session._process_ui(body),
        title=None if title is None else session._process_ui(title),
        icon=None if icon is None else session._process_ui(icon),
    )


def assert_str(x: str) -> str:
    if not isinstance(x, str):
        raise TypeError(f"Expected str, got {type(x)}")
    return x


def assert_list_str(x: list[str]) -> list[str]:
    if not isinstance(x, list):
        raise TypeError(f"Expected list, got {type(x)}")
    for i, x_i in enumerate(x):
        if not isinstance(x_i, str):
            raise TypeError(f"Expected str in x[{i}], got {type(x_i)}")
    return x
