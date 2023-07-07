from __future__ import annotations

import random
from typing import Literal, Optional, TypeVar

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css, tags

from ... import Session
from ..._utils import drop_none
from ...session import require_active_session
from ...types import MISSING, MISSING_TYPE
from ._css_unit import CssUnit, as_css_unit
from ._htmldeps import accordion_dependency
from ._utils import consolidate_attrs

__all__ = (
    "accordion",
    "accordion_panel",
    "accordion_panel_close",
    "accordion_panel_insert",
    "accordion_panel_open",
    "accordion_panel_remove",
    "accordion_panel_set",
    "update_accordion_panel",
)


class AccordionPanel:
    """
    Internal class used to represent an accordion panel.

    This class is used to represent an accordion panel. It is not intended to be
    instantiated directly. Instead, use :func:`~shiny.experimental.ui.accordion_panel`.

    Parameters
    ----------
    *args
        Contents to the accordion panel body. Or tag attributes that are supplied to the
        returned :class:`~htmltools.Tag` object.
    data_value
        A character string that uniquely identifies this panel.
    icon
        A :class:`~htmltools.Tag` which is positioned just before the `title`.
    title
        A title to appear in the :func:`~shiny.experimental.ui.accordion_panel`'s header.
    id
        A unique id for this panel.
    **kwargs
        Tag attributes to the `accordion-body` div Tag.

    See Also
    --------
    * :func:`~shiny.experimental.ui.accordion`
    * :func:`~shiny.experimental.ui.accordion_panel_set`
    * :func:`~shiny.experimental.ui.accordion_panel_open`
    * :func:`~shiny.experimental.ui.accordion_panel_close`
    * :func:`~shiny.experimental.ui.accordion_panel_insert`
    * :func:`~shiny.experimental.ui.accordion_panel_remove`
    * :func:`~shiny.experimental.ui.update_accordion_panel`
    """

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
        """
        Resolve the :class:`~shiny.experimental.ui.AccordionPanel` into a
        :class:`~htmltools.Tag`.

        Returns
        -------
        :
            A :class:`~htmltools.Tag` object representing the
            :class:`~shiny.experimental.ui.AccordionPanel`.
        """
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
            # Always include an .accordion-icon container to simplify update_accordion_panel() logic
            tags.div({"class": "accordion-icon"}, self._icon),
            tags.div({"class": "accordion-title"}, self._title),
        )

        attrs, children = consolidate_attrs(*self._args, **self._kwargs)

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
                tags.div(
                    {"class": "accordion-body"},
                    attrs,
                    children,
                ),
            ),
        )

    def tagify(self) -> Tag:
        """
        Resolve the :class:`~shiny.experimental.ui.AccordionPanel` into a
        :class:`~htmltools.Tag`.

        Returns
        -------
        :
            A tagified `resolve()`d value.
        """
        return self.resolve().tagify()


# TODO-maindocs; @add_example()
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
    """
    Create a vertically collapsing accordion.

    Parameters
    ----------
    *args
        :class:`~shiny.experimental.ui.AccordionPanel` objects returned from
        :func:`~shiny.experimental.ui.accordion_panel`. Or tag attributes that are
        supplied to the returned :class:`~htmltools.Tag` object.
    id
        If provided, you can use `input.id()` in your server logic to determine which of
        the :func:`~shiny.experimental.ui.accordion_panel`s are currently active. The
        value will correspond to the :func:`~shiny.experimental.ui.accordion_panel`'s
        `value` argument.
    open
        A list of :func:`~shiny.experimental.ui.accordion_panel` values to open (i.e.,
        show) by default. The default value of `None` will open the first
        :func:`~shiny.experimental.ui.accordion_panel`. Use a value of `True` to open
        all (or `False` to open none) of the items. It's only possible to open more than
        one panel when `multiple=True`.
    multiple
        Whether multiple :func:`~shiny.experimental.ui.accordion_panel` can be open at
        once.
    class_
        Additional CSS classes to include on the accordion div.
    width
        Any valid CSS unit; for example, height="100%".
    height
        Any valid CSS unit; for example, height="100%".
    **kwargs
        Attributes to this tag.

    Returns
    -------
    :
        Accordion panel Tag object.


    References
    ----------
    [Bootstrap Accordion](https://getbootstrap.com/docs/5.2/components/accordion/)

    See Also
    --------
    * :func:`~shiny.experimental.ui.accordion_panel`
    * :func:`~shiny.experimental.ui.accordion_panel_set`
    * :func:`~shiny.experimental.ui.accordion_panel_open`
    * :func:`~shiny.experimental.ui.accordion_panel_close`
    * :func:`~shiny.experimental.ui.accordion_panel_insert`
    * :func:`~shiny.experimental.ui.accordion_panel_remove`
    * :func:`~shiny.experimental.ui.update_accordion_panel`
    """

    # TODO-bookmarking: Restore input here
    # open = restore_input(id = id, default = open)

    attrs, panels = consolidate_attrs(*args, class_=class_, **kwargs)
    for panel in panels:
        if not isinstance(panel, AccordionPanel):
            raise TypeError(
                "All `accordion(*args)` must be of type `AccordionPanel` which can be created using `accordion_panel()`"
            )

    is_open: list[bool] = []
    if open is None:
        is_open = [False for _ in panels]
    elif isinstance(open, bool):
        is_open = [open for _ in panels]
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
            "style": css(width=as_css_unit(width), height=as_css_unit(height)),
        },
        # just for ease of identifying autoclosing client-side
        {"class": "autoclose"} if not multiple else None,
        binding_class_value,
        accordion_dependency(),
        attrs,
        *panel_tags,
    )
    return tag


# TODO-maindocs; @add_example()
def accordion_panel(
    title: TagChild,
    *args: TagChild | TagAttrs,
    value: Optional[str] | MISSING_TYPE = MISSING,
    icon: Optional[TagChild] = None,
    **kwargs: TagAttrValue,
) -> AccordionPanel:
    """
    Single accordion panel.

    Parameters
    ----------
    title
        A title to appear in the :func:`~shiny.experimental.ui.accordion_panel`'s header.
    *args
        Contents to the accordion panel body. Or tag attributes that are supplied to the
        returned :class:`~htmltools.Tag` object.
    value
        A character string that uniquely identifies this panel. If `MISSING`, the
        `title` will be used.
    icon
        A :class:`~htmltools.Tag` which is positioned just before the `title`.
    **kwargs
        Tag attributes to the `accordion-body` div Tag.

    Returns
    -------
    :
        `AccordionPanel` object.


    References
    ----------
    [Bootstrap Accordion](https://getbootstrap.com/docs/5.2/components/accordion/)

    See Also
    --------
    * :func:`~shiny.experimental.ui.accordion`
    * :func:`~shiny.experimental.ui.accordion_panel_set`
    * :func:`~shiny.experimental.ui.accordion_panel_open`
    * :func:`~shiny.experimental.ui.accordion_panel_close`
    * :func:`~shiny.experimental.ui.accordion_panel_insert`
    * :func:`~shiny.experimental.ui.accordion_panel_remove`
    * :func:`~shiny.experimental.ui.update_accordion_panel`
    """

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
        *args,
        data_value=value,
        icon=icon,
        title=title,
        id=id,
        **kwargs,
    )


# Send message before the next flush since things like remove/insert may
# remove/create input/output values. Also do this for set/open/close since,
# you might want to open a panel after inserting it.
def _send_panel_message(
    id: str,
    session: Session | None,
    **kwargs: object,
) -> None:
    message = drop_none(kwargs)
    session = require_active_session(session)
    session.on_flush(lambda: session.send_input_message(id, message), once=True)


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
        _assert_list_str(values)

    _send_panel_message(
        id,
        session,
        method=method,
        values=values,
    )


# TODO-maindocs; @add_example()
def accordion_panel_set(
    id: str,
    values: bool | str | list[str],
    session: Optional[Session] = None,
) -> None:
    """
    Dynamically set accordions panel state

    Dynamically (i.e., programmatically) update/modify :func:`~shiny.experimental.ui.accordion`s in a Shiny app.
    These functions require an `id` to be provided to the :func:`~shiny.experimental.ui.accordion` and must also be
    called within an active Shiny session.

    Parameters
    ----------
    id
        A string that matches an existing :func:`~shiny.experimental.ui.accordion`'s `id`.
    values
        either a string or list of strings (used to identify particular
        :func:`~shiny.experimental.ui.accordion_panel`(s) by their `value`) or a `bool` to set the state of all
        panels.
    session
        A shiny session object (the default should almost always be used).

    References
    ----------
    [Bootstrap Accordion](https://getbootstrap.com/docs/5.2/components/accordion/)

    See Also
    --------
    * :func:`~shiny.experimental.ui.accordion`
    * :func:`~shiny.experimental.ui.accordion_panel`
    * :func:`~shiny.experimental.ui.accordion_panel_open`
    * :func:`~shiny.experimental.ui.accordion_panel_close`
    * :func:`~shiny.experimental.ui.accordion_panel_insert`
    * :func:`~shiny.experimental.ui.accordion_panel_remove`
    * :func:`~shiny.experimental.ui.update_accordion_panel`
    """
    _accordion_panel_action(id=id, method="set", values=values, session=session)


# TODO-maindocs; @add_example()
def accordion_panel_open(
    id: str,
    values: bool | str | list[str],
    session: Optional[Session] = None,
) -> None:
    """
    Open a set of :func:`~shiny.experimental.ui.accordion_panel`s.

    Parameters
    ----------
    id
        A string that matches an existing :func:`~shiny.experimental.ui.accordion`'s `id`.
    values
        either a string or list of strings (used to identify particular
        :func:`~shiny.experimental.ui.accordion_panel`(s) by their `value`) or a `bool` to set the state of all
        panels.
    session
        A shiny session object (the default should almost always be used).

    References
    ----------
    [Bootstrap Accordion](https://getbootstrap.com/docs/5.2/components/accordion/)

    See Also
    --------
    * :func:`~shiny.experimental.ui.accordion`
    * :func:`~shiny.experimental.ui.accordion_panel`
    * :func:`~shiny.experimental.ui.accordion_panel_set`
    * :func:`~shiny.experimental.ui.accordion_panel_close`
    * :func:`~shiny.experimental.ui.accordion_panel_insert`
    * :func:`~shiny.experimental.ui.accordion_panel_remove`
    * :func:`~shiny.experimental.ui.update_accordion_panel`
    """
    _accordion_panel_action(id=id, method="open", values=values, session=session)


# TODO-maindocs; @add_example()
def accordion_panel_close(
    id: str,
    values: bool | str | list[str],
    session: Optional[Session] = None,
) -> None:
    """
    Close a set of accordion panels in an :func:`~shiny.experimental.ui.accordion`.

    Parameters
    ----------
    id
        A string that matches an existing :func:`~shiny.experimental.ui.accordion`'s `id`.
    values
        either a string or list of strings (used to identify particular
        :func:`~shiny.experimental.ui.accordion_panel`(s) by their `value`) or a `bool` to set the state of all
        panels.
    session
        A shiny session object (the default should almost always be used).

    References
    ----------
    [Bootstrap Accordion](https://getbootstrap.com/docs/5.2/components/accordion/)

    See Also
    --------
    * :func:`~shiny.experimental.ui.accordion`
    * :func:`~shiny.experimental.ui.accordion_panel`
    * :func:`~shiny.experimental.ui.accordion_panel_set`
    * :func:`~shiny.experimental.ui.accordion_panel_open`
    * :func:`~shiny.experimental.ui.accordion_panel_insert`
    * :func:`~shiny.experimental.ui.accordion_panel_remove`
    * :func:`~shiny.experimental.ui.update_accordion_panel`
    """
    _accordion_panel_action(id=id, method="close", values=values, session=session)


# TODO-maindocs; @add_example()
def accordion_panel_insert(
    id: str,
    panel: AccordionPanel,
    target: Optional[str] = None,
    position: Literal["after", "before"] = "after",
    session: Optional[Session] = None,
) -> None:
    """
    Insert an :func:`~shiny.experimental.ui.accordion_panel`

    Parameters
    ----------
    id
        A string that matches an existing :func:`~shiny.experimental.ui.accordion`'s `id`.
    panel
        An :func:`~shiny.experimental.ui.accordion_panel` object to insert.
    target
        The `value` of an existing panel to insert next to.
    position
        Should `panel` be added before or after the target? When `target=None`,
        `"after"` will append after the last panel and `"before"` will prepend before
        the first panel.
    session
        A shiny session object (the default should almost always be used).

    References
    ----------
    [Bootstrap Accordion](https://getbootstrap.com/docs/5.2/components/accordion/)

    See Also
    --------
    * :func:`~shiny.experimental.ui.accordion`
    * :func:`~shiny.experimental.ui.accordion_panel`
    * :func:`~shiny.experimental.ui.accordion_panel_set`
    * :func:`~shiny.experimental.ui.accordion_panel_open`
    * :func:`~shiny.experimental.ui.accordion_panel_close`
    * :func:`~shiny.experimental.ui.accordion_panel_remove`
    * :func:`~shiny.experimental.ui.update_accordion_panel`
    """

    if position not in ("after", "before"):
        raise ValueError("`position` must be either 'after' or 'before'")
    session = require_active_session(session)
    _send_panel_message(
        id,
        session,
        method="insert",
        panel=session._process_ui(panel.resolve()),
        target=None if target is None else _assert_str(target),
        position=position,
    )


# TODO-maindocs; @add_example()
def accordion_panel_remove(
    id: str,
    target: str | list[str],
    session: Optional[Session] = None,
) -> None:
    """
    Remove an :func:`~shiny.experimental.ui.accordion_panel`

    Parameters
    ----------
    id
        A string that matches an existing :func:`~shiny.experimental.ui.accordion`'s `id`.
    target
        The `value` of an existing panel to remove.
    session
        A shiny session object (the default should almost always be used).

    References
    ----------
    [Bootstrap Accordion](https://getbootstrap.com/docs/5.2/components/accordion/)

    See Also
    --------
    * :func:`~shiny.experimental.ui.accordion`
    * :func:`~shiny.experimental.ui.accordion_panel`
    * :func:`~shiny.experimental.ui.accordion_panel_set`
    * :func:`~shiny.experimental.ui.accordion_panel_open`
    * :func:`~shiny.experimental.ui.accordion_panel_close`
    * :func:`~shiny.experimental.ui.accordion_panel_insert`
    * :func:`~shiny.experimental.ui.update_accordion_panel`
    """
    if not isinstance(target, list):
        target = [target]

    _send_panel_message(
        id,
        session,
        method="remove",
        target=_assert_list_str(target),
    )


T = TypeVar("T")


def _missing_none_x(x: T | None | MISSING_TYPE) -> T | Literal[""] | None:
    if isinstance(x, MISSING_TYPE):
        return None
    if x is None:
        return ""
    return x


# TODO-maindocs; @add_example()
def update_accordion_panel(
    id: str,
    target: str,
    *body: TagChild,
    title: TagChild | None | MISSING_TYPE = MISSING,
    value: str | None | MISSING_TYPE = MISSING,
    icon: TagChild | None | MISSING_TYPE = MISSING,
    session: Optional[Session] = None,
) -> None:
    """
    Dynamically update accordions panel contents

    Dynamically (i.e., programmatically) update/modify :func:`~shiny.experimental.ui.accordion` panels in a Shiny app.
    These functions require an `id` to be provided to the :func:`~shiny.experimental.ui.accordion` and must also be
    called within an active Shiny session.

    Parameters
    ----------
    id
        A string that matches an existing :func:`~shiny.experimental.ui.accordion`'s `id`.
    target
        The `value` of an existing panel to update.
    *body
        If provided, the new body contents of the panel.
    title
        If not missing, the new title of the panel.
    value
        If not missing, the new value of the panel.
    icon
        If not missing, the new icon of the panel.
    session
        A shiny session object (the default should almost always be used).

    References
    ----------
    [Bootstrap Accordion](https://getbootstrap.com/docs/5.2/components/accordion/)

    See Also
    --------
    * :func:`~shiny.experimental.ui.accordion`
    * :func:`~shiny.experimental.ui.accordion_panel`
    * :func:`~shiny.experimental.ui.accordion_panel_set`
    * :func:`~shiny.experimental.ui.accordion_panel_open`
    * :func:`~shiny.experimental.ui.accordion_panel_close`
    * :func:`~shiny.experimental.ui.accordion_panel_insert`
    * :func:`~shiny.experimental.ui.accordion_panel_remove`
    """

    session = require_active_session(session)

    title = _missing_none_x(title)
    value = _missing_none_x(value)
    icon = _missing_none_x(icon)
    _send_panel_message(
        id,
        session,
        method="update",
        target=_assert_str(target),
        value=None if value is None else _assert_str(value),
        body=None if len(body) == 0 else session._process_ui(body),
        title=None if title is None else session._process_ui(title),
        icon=None if icon is None else session._process_ui(icon),
    )


def _assert_str(x: str) -> str:
    if not isinstance(x, str):
        raise TypeError(f"Expected str, got {type(x)}")
    return x


def _assert_list_str(x: list[str]) -> list[str]:
    if not isinstance(x, list):
        raise TypeError(f"Expected list, got {type(x)}")
    for i, x_i in enumerate(x):
        if not isinstance(x_i, str):
            raise TypeError(f"Expected str in x[{i}], got {type(x_i)}")
    return x
