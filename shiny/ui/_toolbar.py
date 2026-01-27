from __future__ import annotations

__all__ = (
    "toolbar",
    "toolbar_input_button",
    "toolbar_input_select",
    "toolbar_divider",
    "toolbar_spacer",
    "update_toolbar_input_button",
    "update_toolbar_input_select",
)

import warnings
from typing import Literal, Optional

from htmltools import Tag, TagAttrValue, TagChild, css, div, span, tags

from .._docstring import add_example
from .._utils import drop_none, private_random_int
from ..bookmark import restore_input
from ..module import resolve_id
from ..session import Session, require_active_session
from ..types import MISSING, MISSING_TYPE
from ._html_deps_shinyverse import components_dependencies
from ._input_select import (
    SelectChoicesArg,
    _find_first_option,
    _normalize_choices,
    _render_choices,
)
from ._tooltip import tooltip as ui_tooltip
from .css import CssUnit, as_css_unit


@add_example()
def toolbar(
    *args: TagChild,
    align: Literal["right", "left"] = "right",
    gap: Optional[CssUnit] = None,
    width: Optional[CssUnit] = None,
) -> Tag:
    """
    Create a toolbar container.

    A toolbar which can contain buttons, inputs, and other UI elements in a small
    form suitable for inclusion in card headers, footers, and other small places.

    Parameters
    ----------
    *args
        UI elements for the toolbar.
    align
        Determines if toolbar should be aligned to the `"right"` or `"left"`.
    gap
        A CSS length unit defining the gap (i.e., spacing) between elements in the
        toolbar. Defaults to `0` (no gap).
    width
        CSS width of the toolbar. Defaults to None, which will automatically set
        `width: 100%` when the toolbar is a direct child of a label element (e.g., when
        used in input labels).
        For :func:`~shiny.ui.toolbar_spacer`, to push elements
        effectively, the toolbar needs `width="100%"` to expand and create space. Set
        this explicitly if you need to control the width in other contexts.

    Returns
    -------
    :
        A UI element

    See Also
    --------
    * :func:`~shiny.ui.toolbar_input_button`
    * :func:`~shiny.ui.toolbar_input_select`
    * :func:`~shiny.ui.toolbar_divider`
    * :func:`~shiny.ui.toolbar_spacer`

    Examples
    --------
    ```python
    from shiny import ui

    ui.toolbar(
        align="right",
        ui.toolbar_input_button(id="see", icon=icon("eye"), label="View"),
        ui.toolbar_input_button(id="save", icon=icon("save"), label="Save"),
        ui.toolbar_input_button(id="edit", icon=icon("pencil"), label="Edit")
    )
    ```
    """
    gap_css = as_css_unit(gap) if gap is not None else None
    width_css = as_css_unit(width) if width is not None else None

    tag = div(
        {"class": "bslib-toolbar bslib-gap-spacing", "data-align": align},
        *args,
        components_dependencies(),
        style=css(gap=gap_css, width=width_css),
    )

    return tag


@add_example()
def toolbar_divider(
    width: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
) -> Tag:
    """
    Create a visual divider for toolbars.

    Creates a visual divider line with customizable width and spacing between
    toolbar elements.

    Parameters
    ----------
    width
        A CSS length unit specifying the width of the divider line. Defaults to
        `"2px"` for a sensible dividing line. Pass `"0px"` for no divider line.
    gap
        A CSS length unit defining the spacing around the divider. Defaults to
        `"1rem"` for sensible fixed spacing.

    Returns
    -------
    :
        A UI element

    See Also
    --------
    * :func:`~shiny.ui.toolbar`
    * :func:`~shiny.ui.toolbar_spacer`

    Examples
    --------
    ```python
    from shiny import ui

    ui.toolbar(
        ui.toolbar_input_button(id="left1", label="Left"),
        ui.toolbar_divider(),
        ui.toolbar_input_button(id="right1", label="Right")
    )
    ```

    ```python
    from shiny import ui

    ui.toolbar(
        ui.toolbar_input_button(id="a", label="A"),
        ui.toolbar_divider(width="5px", gap="20px"),
        ui.toolbar_input_button(id="b", label="B")
    )
    ```
    """
    width_css = as_css_unit(width) if width is not None else None
    gap_css = as_css_unit(gap) if gap is not None else None

    # Build style string manually to preserve CSS custom property names with underscores
    style_parts: list[str] = []
    if gap_css is not None:
        style_parts.append(f"--_divider-gap: {gap_css}")
    if width_css is not None:
        style_parts.append(f"--_divider-width: {width_css}")

    style_str = "; ".join(style_parts) if style_parts else None

    return div(
        {
            "class": "bslib-toolbar-divider",
            "aria-hidden": "true",
            "style": style_str,
        },
    )


@add_example()
def toolbar_spacer() -> Tag:
    """
    Create a spacer for toolbars.

    Creates a flexible spacer that pushes subsequent toolbar elements to the opposite
    end of the toolbar. This is useful for creating split toolbars with items on both
    the left and right sides.

    Note
    ----
    For the spacer to push elements effectively, the parent toolbar needs `width="100%"`.
    Set this using the `width` parameter on :func:`~shiny.ui.toolbar`. When the toolbar
    is a direct child of a label element (e.g., when used in input labels), this is
    set automatically.

    Returns
    -------
    :
        A UI element

    See Also
    --------
    * :func:`~shiny.ui.toolbar`
    * :func:`~shiny.ui.toolbar_divider`

    Examples
    --------
    ```python
    from shiny import ui

    # Items on both left and right - set width="100%"
    ui.card(
        ui.card_header(
            "My Card",
            ui.toolbar(
                ui.toolbar_input_button(id="save", label="Save"),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(id="settings", label="Settings"),
                width="100%"
            )
        )
    )
    ```

    ```python
    from shiny import ui

    # Multiple items on each side with spacer
    ui.toolbar(
        ui.toolbar_input_button(id="undo", label="Undo"),
        ui.toolbar_input_button(id="redo", label="Redo"),
        ui.toolbar_spacer(),
        ui.toolbar_input_button(id="help", label="Help"),
        width="100%"
    )
    ```
    """
    return div({"class": "bslib-toolbar-spacer", "aria-hidden": "true"})


@add_example()
def toolbar_input_button(
    id: str,
    label: TagChild,
    *,
    icon: Optional[TagChild] = None,
    show_label: bool = False,
    tooltip: bool | str | MISSING_TYPE = MISSING,
    disabled: bool = False,
    border: bool = False,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a toolbar button input.

    A button designed to fit well in small places such as in a toolbar.

    Parameters
    ----------
    id
        The input ID.
    label
        The input label. By default, `label` is not shown but is used by `tooltip`.
        Set `show_label = True` to show the label (see `tooltip` for details on how
        this affects the tooltip behavior).
    icon
        An icon. If provided without `show_label = True`, only the icon will be
        visible.
    show_label
        Whether to show the label text. If `False` (the default), only the icon is
        shown (if provided). If `True`, the label text is shown alongside the icon.
        Note that `show_label` can be dynamically updated using
        :func:`~shiny.ui.update_toolbar_input_button`.
    tooltip
        Tooltip text to display when hovering over the input. Can be:
        * `True` (default when `show_label = False`) - shows a tooltip with the
          `label` text
        * `False` (default when `show_label = True`) - no tooltip
        * A character string - shows a tooltip with custom text

        Defaults to `!show_label`. When a tooltip is created, it will have an ID of
        `"{id}_tooltip"` which can be used to update the tooltip text via
        :func:`~shiny.ui.update_tooltip`.
    disabled
        If `True`, the button will not be clickable. Use
        :func:`~shiny.ui.update_toolbar_input_button` to dynamically enable/disable
        the button.
    border
        Whether to show a border around the button.
    **kwargs
        Additional attributes to pass to the button.

    Returns
    -------
    :
        A UI element

    Notes
    ------
    ::: {.callout-note title="Updating toolbar buttons"}
    Use :func:`~shiny.ui.update_toolbar_input_button` to change the label, label
    visibility, icon, and disabled state of the button from the server.

    Note that you cannot change the `tooltip` or `border` parameters after the button
    has been created, as these affect the button's structure and ARIA attributes. Please
    use :func:`~shiny.ui.update_tooltip` to update tooltip text.

    When a tooltip is created for the select input, it will have an ID of
    `"{id}_tooltip"` which can be used to update the tooltip text dynamically
    via :func:`~shiny.ui.update_tooltip`.
    :::

    See Also
    --------
    * :func:`~shiny.ui.toolbar`
    * :func:`~shiny.ui.update_toolbar_input_button`
    * :func:`~shiny.ui.input_action_button`

    Examples
    --------
    ```python
    from shiny import ui

    # Icon-only with tooltip
    ui.toolbar_input_button(id="save", icon=icon("save"), label="Save")
    ```

    ```python
    from shiny import ui

    # Label and icon
    ui.toolbar_input_button(
        id="edit",
        icon=icon("pencil"),
        label="Edit",
        show_label=True
    )
    ```
    """

    if "_add_ws" not in kwargs:
        kwargs["_add_ws"] = True

    # Determine button type
    if icon is None:
        if not show_label:
            raise ValueError("If `show_label` is False, `icon` must be provided.")
        btn_type = "label"
    else:
        btn_type = "both" if show_label else "icon"

    # Validate that label has text for accessibility
    label_text = _extract_text(label)
    if not label_text.strip():
        warnings.warn(
            "Consider providing a non-empty string label for accessibility.",
            stacklevel=2,
        )

    # Compute tooltip default: !show_label
    if isinstance(tooltip, MISSING_TYPE):
        tooltip = not show_label

    resolved_id = resolve_id(id)
    label_id = f"btn-label-{private_random_int(1000, 10000)}"

    # Create label element (hidden if show_label is False)
    label_elem = span(
        label,
        id=label_id,
        class_="bslib-toolbar-label",
        hidden="" if not show_label else None,
    )

    # Wrap icon to ensure it's always treated as decorative
    icon_elem = (
        span(
            icon,
            {"class": "bslib-toolbar-icon", "aria-hidden": "true"},
            style=css(
                pointer_events="none",
                display="inline-flex",
                align_items="center",
                vertical_align="middle",
            ),
        )
        if icon is not None
        else None
    )

    border_class = "border-0" if not border else "border-1"
    button = tags.button(
        icon_elem,
        label_elem,
        {
            "id": resolved_id,
            "type": "button",
            "class": f"bslib-toolbar-input-button btn btn-default btn-sm action-button {border_class}",
            "data-type": btn_type,
            "aria-labelledby": label_id,
        },
        kwargs,
        disabled="" if disabled else None,
    )

    # Handle tooltip
    tooltip_text: Optional[TagChild] = None
    if tooltip is True:
        tooltip_text = label
    elif isinstance(tooltip, str):
        tooltip_text = tooltip
    # If tooltip is False, tooltip_text remains None

    if tooltip_text is not None:
        button = ui_tooltip(
            button,
            tooltip_text,
            id=f"{resolved_id}_tooltip",
            placement="bottom",
        )

    return button


def _extract_text(x: TagChild) -> str:
    """Extract text content from a TagChild for validation."""
    if isinstance(x, str):
        return x
    if isinstance(x, (list, tuple)):
        return " ".join(_extract_text(item) for item in x)
    if isinstance(x, Tag):
        if hasattr(x, "children"):
            return _extract_text(x.children)
    return ""


@add_example()
def update_toolbar_input_button(
    id: str,
    *,
    label: Optional[TagChild] = None,
    show_label: Optional[bool] = None,
    icon: Optional[TagChild] = None,
    disabled: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    """
    Update a toolbar button input on the client.

    Change the value or appearance of a toolbar button input from the server.

    Parameters
    ----------
    id
        The input ID.
    label
        The new label for the button.
    show_label
        Whether to show the label text.
    icon
        The new icon for the button.
    disabled
        Whether the button should be disabled.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Details
    -------
    This update function works similarly to :func:`~shiny.ui.update_action_button`,
    but is specifically designed for :func:`~shiny.ui.toolbar_input_button`. It
    allows you to update the button's label, icon, and disabled state from the server.

    Note that you cannot change `tooltip` or `border` parameters after the button has
    been created, as these affect the button's structure and ARIA attributes. Please use
    :func:`~shiny.ui.update_tooltip` to update tooltip text.

    When a tooltip is created for the select input, it will have an ID of
    `"{id}_tooltip"` which can be used to update the tooltip text dynamically
    via :func:`~shiny.ui.update_tooltip`.

    See Also
    --------
    * :func:`~shiny.ui.toolbar_input_button`
    * :func:`~shiny.ui.update_action_button`

    Examples
    --------
    ```python
    from shiny import App, reactive, ui

    app_ui = ui.page_fluid(
        ui.toolbar(
            align="right",
            ui.toolbar_input_button("btn", label="Click me", icon=icon("play"))
        ),
        ui.output_text_verbatim("count")
    )

    def server(input, output, session):
        @output
        @render.text
        def count():
            return str(input.btn())

        @reactive.effect
        @reactive.event(input.btn)
        def _():
            if input.btn() == 1:
                ui.update_toolbar_input_button(
                    "btn",
                    label="Clicked!",
                    icon=icon("check")
                )

    app = App(app_ui, server)
    ```
    """
    session = require_active_session(session)

    # Validate label if provided
    if label is not None:
        label_text = _extract_text(label)
        if not label_text.strip():
            warnings.warn(
                "Consider providing a non-empty string label for accessibility.",
                stacklevel=2,
            )

    # Process label and icon through session
    label_processed = session._process_ui(label) if label is not None else None
    icon_processed = session._process_ui(icon) if icon is not None else None

    message = drop_none(
        {
            "label": label_processed,
            "showLabel": show_label,
            "icon": icon_processed,
            "disabled": disabled,
        }
    )

    session.send_input_message(id, message)


@add_example()
def toolbar_input_select(
    id: str,
    label: str,
    choices: SelectChoicesArg,
    *,
    selected: Optional[str] = None,
    icon: Optional[TagChild] = None,
    show_label: bool = False,
    tooltip: bool | str | MISSING_TYPE = MISSING,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a toolbar select input.

    Create a select list input control that can be used to choose a single item
    from a list of values, suitable for use within a toolbar.

    Parameters
    ----------
    id
        The input ID.
    label
        The input label. Must be a non-empty string for accessibility. By default,
        `label` is not shown but is used by `tooltip`. Set `show_label = True` to
        show the label.
    choices
        Either a list of choices or a dictionary mapping choice values to labels.
        Note that if a dictionary is provided, the keys are used as the (input)
        values and the values are labels displayed to the user. A dictionary of
        dictionaries is also supported, and in that case, the top-level keys are
        treated as ``<optgroup>`` labels.
    selected
        The initially selected value. If not provided, the first choice will be
        selected by default.
    icon
        An icon to display alongside the select input.
    show_label
        Whether to show the label text. If `False` (the default), the label is
        visually hidden but still available to screen readers.
    tooltip
        Tooltip text to display when hovering over the input. Can be:
        * `True` (default when `show_label = False`) - shows a tooltip with the
          `label` text
        * `False` (default when `show_label = True`) - no tooltip
        * A character string - shows a tooltip with custom text
    **kwargs
        Additional named attributes passed to the outer container div.

    Returns
    -------
    :
        A UI element

    Notes
    ------
    ::: {.callout-note title="Updating toolbar select inputs"}
    You can update the appearance and choices of a toolbar select input. This function
    works similarly to :func:`shiny::updateSelectInput`, but is specifically
    designed for `toolbar_input_select`. It allows you to update the select's label,
    icon, choices, selected value, and label visibility from the server.

    Note that you cannot enable or disable the `tooltip` parameter after the
    select has been created, as this affects the select's structure and ARIA
    attributes. Please use :func:`~shiny.ui.update_tooltip` to update tooltip text.

    When a tooltip is created for the select input, it will have an ID of
    `"{id}_tooltip"` which can be used to update the tooltip text dynamically
    via :func:`~shiny.ui.update_tooltip`.
    :::

    See Also
    --------
    * :func:`~shiny.ui.toolbar`
    * :func:`~shiny.ui.update_toolbar_input_select`
    * :func:`~shiny.ui.input_select`

    Examples
    --------
    ```python
    from shiny import ui

    ui.toolbar(
        align="right",
        ui.toolbar_input_select(
            id="select",
            label="Choose option",
            choices=["Option 1", "Option 2", "Option 3"],
            selected="Option 2"
        )
    )
    ```

    ```python
    from shiny import ui

    # With icon and tooltip
    ui.toolbar(
        align="right",
        ui.toolbar_input_select(
            id="filter",
            label="Filter",
            choices=["All", "Active", "Archived"],
            icon=icon("filter"),
            tooltip="Filter the data"
        )
    )
    ```

    ```python
    from shiny import ui

    # Grouped choices
    ui.toolbar(
        align="right",
        ui.toolbar_input_select(
            id="grouped",
            label="Select item",
            choices={
                "Group A": {"a1": "Choice A1", "a2": "Choice A2"},
                "Group B": {"b1": "Choice B1", "b2": "Choice B2"}
            }
        )
    )
    ```
    """
    # Validate that label is a non-empty string
    if not isinstance(label, str) or not label.strip():
        raise ValueError("`label` must be a non-empty string.")

    # Set tooltip default based on show_label (matches bslib R behavior)
    if tooltip is MISSING:
        tooltip = not show_label

    resolved_id = resolve_id(id)

    # Restore input for bookmarking
    selected = restore_input(resolved_id=resolved_id, default=selected)

    choices_normalized = _normalize_choices(choices)

    # Set selected to first choice if no default or restored value
    if selected is None:
        selected = _find_first_option(choices_normalized)

    # Select element gets its own ID for label association
    select_id = f"{resolved_id}-select"

    select_tag = tags.select(
        _render_choices(choices_normalized, selected),
        {
            "id": select_id,
            "class": "form-select form-select-sm bslib-toolbar-select",
            "data-shiny-no-bind-input": True,
        },
    )

    # Always create icon element for consistent DOM structure (even if empty)
    # This allows dynamic icon updates via update_toolbar_input_select()
    icon_elem = span(
        icon,
        {
            "class": "bslib-toolbar-icon",
            "aria-hidden": "true",
            "role": "none",
            "tabindex": "-1",
        },
        style="pointer-events: none",
    )

    # Create label element
    label_span_classes = "bslib-toolbar-label"
    if not show_label:
        label_span_classes += " visually-hidden"

    label_elem = tags.label(
        icon_elem,
        span(
            label,
            class_=label_span_classes,
        ),
        {
            "id": f"{resolved_id}-label",
            "class": "control-label",
            "for": select_id,
        },
        # Added to fix icon alignment issue because icon svg padding
        style=css(
            display="inline-flex",
            align_items="center",
        ),
    )

    tooltip_text: Optional[TagChild] = None
    if tooltip is True:
        # Hide from screen readers since it repeats the label content
        tooltip_text = span(label, {"aria-hidden": "true"})
    elif isinstance(tooltip, str):
        tooltip_text = tooltip

    if tooltip_text is not None:
        select_tag = ui_tooltip(
            select_tag,
            tooltip_text,
            id=f"{resolved_id}_tooltip",
            placement="bottom",
        )

    return div(
        label_elem,
        select_tag,
        {
            "id": resolved_id,
            "class": "bslib-toolbar-input-select shiny-input-container",
        },
        kwargs,
    )


@add_example()
def update_toolbar_input_select(
    id: str,
    *,
    label: Optional[str] = None,
    show_label: Optional[bool] = None,
    choices: Optional[SelectChoicesArg] = None,
    selected: Optional[str] = None,
    icon: Optional[TagChild] = None,
    session: Optional[Session] = None,
) -> None:
    """
    Update a toolbar select input on the client.

    Change the value or appearance of a toolbar select input from the server.

    Parameters
    ----------
    id
        The input ID.
    label
        The new label for the select input.
    show_label
        Whether to show the label text.
    choices
        The new choices for the select input.
    selected
        The new selected value.
    icon
        The new icon for the select input.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Details
    -------
    This update function works similarly to :func:`~shiny.ui.update_select_input`,
    but is specifically designed for :func:`~shiny.ui.toolbar_input_select`. It
    allows you to update the select's label, icon, choices, selected value(s), and
    label visibility from the server.

    Note that you cannot enable or disable the `tooltip` parameter after the
    select has been created, as this affects the select's structure and ARIA
    attributes. Please use :func:`~shiny.ui.update_tooltip` to update tooltip text.

    When a tooltip is created for the select input, it will have an ID of
    `"{id}_tooltip"` which can be used to update the tooltip text dynamically
    via :func:`~shiny.ui.update_tooltip`.

    See Also
    --------
    * :func:`~shiny.ui.toolbar_input_select`
    * :func:`~shiny.ui.update_select`

    Examples
    --------
    ```python
    from shiny import App, reactive, ui

    app_ui = ui.page_fluid(
        ui.toolbar(
            align="right",
            ui.toolbar_input_select(
                "select",
                label="Choose",
                choices=["A", "B", "C"]
            )
        ),
        ui.output_text_verbatim("value")
    )

    def server(input, output, session):
        @output
        @render.text
        def value():
            return str(input.select())

        @reactive.effect
        @reactive.event(input.select)
        def _():
            if input.select() == "A":
                ui.update_toolbar_input_select(
                    "select",
                    label="Pick one",
                    choices=["X", "Y", "Z"],
                    selected="Y"
                )

    app = App(app_ui, server)
    ```
    """
    session = require_active_session(session)

    # Process label and icon through session
    label_processed = session._process_ui(label) if label is not None else None
    icon_processed = session._process_ui(icon) if icon is not None else None

    # Process choices - generate the options HTML
    options_processed = None
    if choices is not None:
        choices_normalized = _normalize_choices(choices)
        options_html = _render_choices(choices_normalized, selected)
        options_processed = str(options_html)

    # Convert selected to string if provided
    selected_processed = str(selected) if selected is not None else None

    message = drop_none(
        {
            "label": label_processed,
            "showLabel": show_label,
            "icon": icon_processed,
            "options": options_processed,
            "value": selected_processed,
        }
    )

    session.send_input_message(id, message)
