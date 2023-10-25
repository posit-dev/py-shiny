from __future__ import annotations

from typing import Any, Callable, Literal, Optional, Sequence, TypeVar, overload

from htmltools import (
    MetadataNode,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagFunction,
    TagList,
)

from ..._deprecated import warn_deprecated
from ...session import Session
from ...types import MISSING, MISSING_TYPE
from ...ui import AccordionPanel as MainAccordionPanel
from ...ui import accordion as main_accordion
from ...ui import accordion_panel as main_accordion_panel
from ...ui import accordion_panel_close as main_accordion_panel_close
from ...ui import accordion_panel_insert as main_accordion_panel_insert
from ...ui import accordion_panel_open as main_accordion_panel_open
from ...ui import accordion_panel_remove as main_accordion_panel_remove
from ...ui import accordion_panel_set as main_accordion_panel_set
from ...ui import input_text_area as main_input_text_area
from ...ui import popover as main_popover
from ...ui import tags
from ...ui import toggle_popover as main_toggle_popover
from ...ui import toggle_switch as main_toggle_switch
from ...ui import toggle_tooltip as main_toggle_tooltip
from ...ui import tooltip as main_tooltip
from ...ui import update_accordion_panel as main_update_accordion_panel
from ...ui import update_popover as main_update_popover
from ...ui import update_tooltip as main_update_tooltip
from ...ui._card import CardItem as MainCardItem
from ...ui._card import card_footer as main_card_footer
from ...ui._card import card_header as main_card_header
from ...ui._layout import layout_column_wrap as main_layout_column_wrap
from ...ui._navs import NavSetArg
from ...ui._navs import NavSetBar as MainNavSetBar
from ...ui._navs import NavSetCard as MainNavSetCard
from ...ui._navs import navset_bar as main_navset_bar
from ...ui._navs import navset_card_pill as main_navset_card_pill
from ...ui._navs import navset_card_tab as main_navset_card_tab
from ...ui._output import output_image as main_output_image
from ...ui._output import output_plot as main_output_plot
from ...ui._output import output_ui as main_output_ui
from ...ui._page import page_fillable as main_page_fillable
from ...ui._page import page_navbar as main_page_navbar
from ...ui._page import page_sidebar as main_page_sidebar
from ...ui._plot_output_opts import BrushOpts as MainBrushOpts
from ...ui._plot_output_opts import ClickOpts as MainClickOpts
from ...ui._plot_output_opts import DblClickOpts as MainDblClickOpts
from ...ui._plot_output_opts import HoverOpts as MainHoverOpts
from ...ui._sidebar import DeprecatedPanelMain, DeprecatedPanelSidebar
from ...ui._sidebar import Sidebar as MainSidebar
from ...ui._sidebar import layout_sidebar as main_layout_sidebar
from ...ui._sidebar import panel_main as main_panel_main
from ...ui._sidebar import panel_sidebar as main_panel_sidebar
from ...ui._sidebar import sidebar as main_sidebar
from ...ui._sidebar import toggle_sidebar as main_toggle_sidebar
from ...ui._valuebox import showcase_left_center as main_showcase_left_center
from ...ui._valuebox import showcase_top_right as main_showcase_top_right
from ...ui._valuebox import value_box as main_value_box
from ...ui.css._css_unit import CssUnit as MainCssUnit
from ...ui.css._css_unit import as_css_padding as main_as_css_padding
from ...ui.css._css_unit import as_css_unit as main_as_css_unit
from ...ui.css._css_unit import as_width_unit as main_as_width_unit
from ...ui.fill import as_fill_item as main_as_fill_item
from ...ui.fill import as_fillable_container as main_as_fillable_container
from ...ui.fill import is_fill_item as main_is_fill_item
from ...ui.fill import is_fillable_container as main_is_fillable_container
from ...ui.fill import remove_all_fill as main_remove_all_fill

__all__ = (
    # Input Switch
    "toggle_switch",
    # Input Text Area
    "input_text_area",
    # Navs
    "navset_pill_card",
    "navset_tab_card",
    # Tooltip
    "tooltip_update",
    "tooltip_toggle",
    "tooltip",
    "toggle_tooltip",
    "update_tooltip",
    # Sidebar
    "Sidebar",
    "sidebar",
    "layout_sidebar",
    "toggle_sidebar",
    "sidebar_toggle",
    "panel_sidebar",
    "panel_main",
    "DeprecatedPanelSidebar",
    "DeprecatedPanelMain",
    # Css Unit
    "CssUnit",
    "as_css_unit",
    "as_css_padding",
    "as_width_unit",
    # Popover
    "popover",
    "toggle_popover",
    "update_popover",
    # Accordion
    "AccordionPanel",
    "accordion",
    "accordion_panel",
    "accordion_panel_set",
    "accordion_panel_open",
    "accordion_panel_close",
    "accordion_panel_insert",
    "accordion_panel_remove",
    "update_accordion_panel",
    # Fill
    "as_fill_carrier",
    "as_fillable_container",
    "as_fill_item",
    "remove_all_fill",
    "is_fill_carrier",
    "is_fillable_container",
    "is_fill_item",
    # Card
    "TagCallable",
    "CardItem",
    "card_header",
    "card_footer",
    # Value Box
    "value_box",
    # Layout
    "layout_column_wrap",
    # Navs
    "navset_bar",
    "navset_card_tab",
    "navset_card_pill",
    # Output
    "output_ui",
    "output_plot",
    "output_image",
    # Page
    "page_navbar",
    "page_sidebar",
    "page_fillable",
)

######################
# Input Switch
######################


# Deprecated 2023-09-12
def toggle_switch(
    id: str,
    value: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.toggle_switch()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.toggle_switch()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.toggle_switch()` instead."
    )
    return main_toggle_switch(id, value, session=session)


######################
# Input Text Area
######################


# Deprecated 2023-09-12
def input_text_area(
    id: str,
    label: TagChild,
    value: str = "",
    *,
    width: Optional[str] = None,
    height: Optional[str] = None,
    cols: Optional[int] = None,
    rows: Optional[int] = None,
    placeholder: Optional[str] = None,
    resize: Optional[Literal["none", "both", "horizontal", "vertical"]] = None,
    autoresize: bool = False,
    autocomplete: Optional[str] = None,
    spellcheck: Optional[Literal["true", "false"]] = None,
) -> Tag:
    """Deprecated. Please use `shiny.ui.input_text_area()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.input_text_area()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.input_text_area()` instead."
    )
    return main_input_text_area(
        id,
        label,
        value=value,
        width=width,
        height=height,
        cols=cols,
        rows=rows,
        placeholder=placeholder,
        resize=resize,
        autoresize=autoresize,
        autocomplete=autocomplete,
        spellcheck=spellcheck,
    )


######################
# Navs
######################


# Deprecated 2023-08-15
def navset_pill_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[MainSidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
    placement: Literal["above", "below"] = "above",
) -> MainNavSetCard:
    """Deprecated. Please use `navset_card_pill()` instead of `navset_pill_card()`."""
    warn_deprecated(
        "`shiny.experimental.ui.navset_pill_card()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.experimental.ui.navset_card_pill()` instead."
    )
    return main_navset_card_pill(
        *args,
        id=id,
        selected=selected,
        sidebar=sidebar,
        header=header,
        footer=footer,
        placement=placement,
    )


# Deprecated 2023-08-15
def navset_tab_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[MainSidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> MainNavSetCard:
    """Deprecated. Please use `navset_card_tab()` instead of `navset_tab_card()`."""
    warn_deprecated(
        "`shiny.experimental.ui.navset_tab_card()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.experimental.ui.navset_card_tab()` instead."
    )
    return main_navset_card_tab(
        *args,
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


######################
# Tooltip
######################


# Deprecated 2023-09-12
def tooltip(
    trigger: TagChild,
    *args: TagChild | TagAttrs,
    id: Optional[str] = None,
    placement: Literal["auto", "top", "right", "bottom", "left"] = "auto",
    options: Optional[dict[str, object]] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """Deprecated. Please use `shiny.ui.tooltip()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.tooltip()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.tooltip()` instead."
    )
    return main_tooltip(
        trigger,
        *args,
        id=id,
        placement=placement,
        options=options,
        **kwargs,
    )


# Deprecated 2023-08-23
def tooltip_update(id: str, *args: TagChild, session: Optional[Session] = None) -> None:
    """Deprecated. Please use `shiny.ui.update_tooltip()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.tooltip_update()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.update_tooltip()` instead."
    )
    main_update_tooltip(
        id,
        *args,
        session=session,
    )


# Deprecated 2023-09-12
def update_tooltip(id: str, *args: TagChild, session: Optional[Session] = None) -> None:
    """Deprecated. Please use `shiny.ui.update_tooltip()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.update_tooltip()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.update_tooltip()` instead."
    )
    main_update_tooltip(
        id,
        *args,
        session=session,
    )


# Deprecated 2023-08-23
def tooltip_toggle(
    id: str,
    show: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.toggle_tooltip()`."""
    warn_deprecated(
        "`shiny.experimental.ui.tooltip_toggle()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.toggle_tooltip()` instead."
    )
    main_toggle_tooltip(
        id=id,
        show=show,
        session=session,
    )


# Deprecated 2023-09-12
def toggle_tooltip(
    id: str,
    show: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.toggle_tooltip()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.tooltip_toggle()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.toggle_tooltip()` instead."
    )
    main_toggle_tooltip(
        id=id,
        show=show,
        session=session,
    )


######################
# Sidebar
######################


class Sidebar(MainSidebar):
    """Deprecated. Please use `shiny.ui.Sidebar` instead."""

    def __init__(
        self,
        tag: Tag,
        collapse_tag: Optional[Tag],
        position: Literal["left", "right"],
        open: Literal["desktop", "open", "closed", "always"],
        width: CssUnit,
        max_height_mobile: Optional[str | float],
        color_fg: Optional[str],
        color_bg: Optional[str],
    ):
        warn_deprecated(
            "`shiny.experimental.ui.Sidebar` is deprecated. "
            "This class will be removed in a future version, "
            "please use :class:`shiny.ui.Sidebar` instead."
        )
        super().__init__(
            tag,
            collapse_tag,
            position,
            open,
            width,
            max_height_mobile,
            color_fg,
            color_bg,
        )


def sidebar(
    *args: TagChild | TagAttrs,
    width: CssUnit = 250,
    position: Literal["left", "right"] = "left",
    open: Literal["desktop", "open", "closed", "always"] = "desktop",
    id: Optional[str] = None,
    title: TagChild | str = None,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    class_: Optional[str] = None,  # TODO-future; Consider using `**kwargs` instead
    max_height_mobile: Optional[str | float] = None,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
) -> MainSidebar:
    """Deprecated. Please use `shiny.ui.sidebar()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.sidebar()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.sidebar()` instead."
    )
    return main_sidebar(
        *args,
        width=width,
        position=position,
        open=open,
        id=id,
        title=title,
        bg=bg,
        fg=fg,
        class_=class_,
        max_height_mobile=max_height_mobile,
        gap=gap,
        padding=padding,
    )


def layout_sidebar(
    sidebar: Sidebar | TagChild | TagAttrs,
    *args: TagChild | TagAttrs,
    fillable: bool = True,
    fill: bool = True,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    border: Optional[bool] = None,
    border_radius: Optional[bool] = None,
    border_color: Optional[str] = None,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
) -> MainCardItem:
    """Deprecated. Please use `shiny.ui.layout_sidebar()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.layout_sidebar()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.layout_sidebar()` instead."
    )
    return main_layout_sidebar(
        sidebar,
        *args,
        fillable=fillable,
        fill=fill,
        bg=bg,
        fg=fg,
        border=border,
        border_radius=border_radius,
        border_color=border_color,
        gap=gap,
        padding=padding,
        height=height,
        **kwargs,
    )


def toggle_sidebar(
    id: str,
    open: Literal["toggle", "open", "closed", "always"] | bool | None = None,
    session: Session | None = None,
) -> None:
    """Deprecated. Please use `shiny.ui.toggle_sidebar()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.toggle_sidebar()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.toggle_sidebar()` instead."
    )
    return main_toggle_sidebar(
        id,
        open=open,
        session=session,
    )


# ----------------------------


# ----------------------------


# Deprecated 2023-08-23
def sidebar_toggle(
    id: str,
    open: Literal["toggle", "open", "closed", "always"] | bool | None = None,
    session: Session | None = None,
) -> None:
    """Deprecated. Please use `shiny.ui.toggle_sidebar()` instead of `sidebar_toggle()`."""
    warn_deprecated(
        "`shiny.experimental.ui.sidebar_toggle()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.toggle_sidebar()` instead."
    )
    main_toggle_sidebar(
        id=id,
        open=open,
        session=session,
    )


# Deprecated 2023-06-13
# Includes: DeprecatedPanelSidebar
def panel_sidebar(
    *args: TagChild | TagAttrs,
    width: int = 4,
    **kwargs: TagAttrValue,
) -> DeprecatedPanelSidebar:
    """Deprecated. Please use `shiny.ui.sidebar()` instead of
    `shiny.experimental.ui.panel_sidebar()`."""
    warn_deprecated(
        "`shiny.experimental.ui.panel_sidebar()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.sidebar()` with `shiny.ui.layout_sidebar()` instead."
    )
    return main_panel_sidebar(
        *args,
        width=width,
        **kwargs,
    )


# Deprecated 2023-06-13
# Includes: DeprecatedPanelMain
def panel_main(
    *args: TagChild | TagAttrs,
    width: int = 8,
    **kwargs: TagAttrValue,
) -> DeprecatedPanelMain:
    """Deprecated. Please use `shiny.ui.layout_sidebar()` instead of
    `shiny.experimental.ui.panel_main()`."""
    warn_deprecated(
        "`shiny.experimental.ui.panel_main()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.sidebar()` with `shiny.ui.layout_sidebar()` instead."
    )
    return main_panel_main(
        *args,
        width=width,
        **kwargs,
    )


######################
# Css Unit
######################

# Deprecated 2023-09-12
CssUnit = MainCssUnit
"""
Deprecated. Please use `shiny.ui.css_unit.CssUnit` instead.
"""


@overload
def as_css_unit(value: None) -> None:
    ...


@overload
def as_css_unit(value: CssUnit) -> str:
    ...


# Deprecated 2023-09-12
def as_css_unit(value: None | CssUnit) -> None | str:
    """
    Deprecated. Please use `shiny.ui.css_unit.as_css_unit()` instead.
    """
    warn_deprecated(
        "`shiny.experimental.ui.as_css_unit()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.css_unit.as_css_unit()` instead."
    )
    return main_as_css_unit(value)


@overload
def as_css_padding(padding: CssUnit | list[CssUnit]) -> str:
    ...


@overload
def as_css_padding(padding: None) -> None:
    ...


# Deprecated 2023-09-12
def as_css_padding(padding: CssUnit | list[CssUnit] | None) -> str | None:
    """
    Deprecated. Please use `shiny.ui.css_unit.as_css_padding()` instead.
    """
    warn_deprecated(
        "`shiny.experimental.ui.as_css_padding()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.css_unit.as_css_padding()` instead."
    )
    return main_as_css_padding(padding)


# Deprecated 2023-09-12
def as_width_unit(x: str | float | int) -> str:
    """Deprecated. Please use `shiny.ui.css_unit.as_width_unit()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.as_width_unit()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.css_unit.as_width_unit()` instead."
    )
    return main_as_width_unit(x)


######################
# Popover
######################


# Deprecated 2023-09-12
def popover(
    trigger: TagChild,
    *args: TagChild | TagAttrs,
    title: Optional[TagChild] = None,
    id: Optional[str] = None,
    placement: Literal["auto", "top", "right", "bottom", "left"] = "auto",
    options: Optional[dict[str, Any]] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """Deprecated. Please use `shiny.ui.popover()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.popover()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.popover()` instead."
    )
    return main_popover(
        trigger,
        *args,
        title=title,
        id=id,
        placement=placement,
        options=options,
        **kwargs,
    )


# Deprecated 2023-09-12
def toggle_popover(
    id: str,
    show: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.toggle_popover()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.toggle_popover()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.toggle_popover()` instead."
    )
    return main_toggle_popover(id, show, session=session)


# Deprecated 2023-09-12
def update_popover(
    id: str,
    *args: TagChild,
    title: Optional[TagChild] = None,
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.update_popover()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.update_popover()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.update_popover()` instead."
    )
    return main_update_popover(id, *args, title=title, session=session)


# ######################
# # Accordion
# ######################


# Deprecated 2023-09-12
class AccordionPanel(MainAccordionPanel):
    """
    Deprecated. Please use `shiny.ui.AccordionPanel` instead.
    """

    ...


# Deprecated 2023-09-12
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
    """Deprecated. Please use `shiny.ui.accordion()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.accordion()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.accordion()` instead."
    )
    return main_accordion(
        *args,
        id=id,
        open=open,
        multiple=multiple,
        class_=class_,
        width=width,
        height=height,
        **kwargs,
    )


# Deprecated 2023-09-12
def accordion_panel(
    title: TagChild,
    *args: TagChild | TagAttrs,
    value: Optional[str] | MISSING_TYPE = MISSING,
    icon: Optional[TagChild] = None,
    **kwargs: TagAttrValue,
) -> MainAccordionPanel:
    """Deprecated. Please use `shiny.ui.accordion_panel()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.accordion_panel()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.accordion_panel()` instead."
    )
    return main_accordion_panel(
        title,
        *args,
        value=value,
        icon=icon,
        **kwargs,
    )


# # Deprecated 2023-09-12
def accordion_panel_set(
    id: str,
    values: bool | str | list[str],
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.accordion_panel_set()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.accordion_panel_set()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.accordion_panel_set()` instead."
    )
    return main_accordion_panel_set(id, values, session=session)


# # Deprecated 2023-09-12
def accordion_panel_open(
    id: str,
    values: bool | str | list[str],
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.accordion_panel_open()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.accordion_panel_open()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.accordion_panel_open()` instead."
    )
    return main_accordion_panel_open(id, values, session=session)


# # Deprecated 2023-09-12
def accordion_panel_close(
    id: str,
    values: bool | str | list[str],
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.accordion_panel_close()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.accordion_panel_close()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.accordion_panel_close()` instead."
    )
    return main_accordion_panel_close(id, values, session=session)


# # Deprecated 2023-09-12
def accordion_panel_insert(
    id: str,
    panel: AccordionPanel,
    target: Optional[str] = None,
    position: Literal["after", "before"] = "after",
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.accordion_panel_insert()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.accordion_panel_insert()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.accordion_panel_insert()` instead."
    )
    return main_accordion_panel_insert(
        id,
        panel,
        target=target,
        position=position,
        session=session,
    )


# # Deprecated 2023-09-12
def accordion_panel_remove(
    id: str,
    target: str | list[str],
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.accordion_panel_remove()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.accordion_panel_remove()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.accordion_panel_remove()` instead."
    )
    return main_accordion_panel_remove(
        id,
        target=target,
        session=session,
    )


# Deprecated 2023-09-12
def update_accordion_panel(
    id: str,
    target: str,
    *body: TagChild,
    title: TagChild | None | MISSING_TYPE = MISSING,
    value: str | None | MISSING_TYPE = MISSING,
    icon: TagChild | None | MISSING_TYPE = MISSING,
    session: Optional[Session] = None,
) -> None:
    """Deprecated. Please use `shiny.ui.update_accordion_panel()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.update_accordion_panel()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.update_accordion_panel()` instead."
    )
    return main_update_accordion_panel(
        id,
        target,
        *body,
        title=title,
        value=value,
        icon=icon,
        session=session,
    )


# ######################
# # Fill
# ######################
TagT = TypeVar("TagT", bound="Tag")


def as_fill_carrier(
    tag: TagT,
    *,
    min_height: None = None,
    max_height: None = None,
    gap: None = None,
) -> TagT:
    """Deprecated. Please use a combination of `shiny.ui.fill.as_fillable_container()` and `shiny.ui.fill.as_fill_item()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.as_fill_carrier()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.fill.as_fill_container()` and `shiny.ui.fill.as_fillable_item()` instead."
    )

    if min_height is not None:
        raise RuntimeError(
            "`min_height` is no longer supported. Please add the attribute directly to the Tag's style."
        )
    if max_height is not None:
        raise RuntimeError(
            "`max_height` is no longer supported. Please add the attribute directly to the Tag's style."
        )
    if gap is not None:
        raise RuntimeError(
            "`gap` is no longer supported. Please add the attribute directly to the Tag's style."
        )
    return main_as_fillable_container(main_as_fill_item(tag))


def as_fillable_container(
    tag: TagT,
    *,
    min_height: None = None,
    max_height: None = None,
    gap: None = None,
) -> TagT:
    """Deprecated. Please use `shiny.ui.fill.as_fillable_container()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.as_fillable_container()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.fill.as_fillable_container()` instead."
    )
    if min_height is not None:
        raise RuntimeError(
            "`min_height` is no longer supported. Please add the attribute directly to the Tag's style."
        )
    if max_height is not None:
        raise RuntimeError(
            "`max_height` is no longer supported. Please add the attribute directly to the Tag's style."
        )
    if gap is not None:
        raise RuntimeError(
            "`gap` is no longer supported. Please add the attribute directly to the Tag's style."
        )

    return main_as_fillable_container(tag)


def as_fill_item(
    tag: TagT,
    *,
    min_height: None = None,
    max_height: None = None,
) -> TagT:
    """Deprecated. Please use `shiny.ui.fill.as_fill_item()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.as_fill_item()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.fill.as_fill_item()` instead."
    )
    if min_height is not None:
        raise RuntimeError(
            "`min_height` is no longer supported. Please add the attribute directly to the Tag's style."
        )
    if max_height is not None:
        raise RuntimeError(
            "`max_height` is no longer supported. Please add the attribute directly to the Tag's style."
        )

    return main_as_fill_item(tag)


def remove_all_fill(tag: TagT) -> TagT:
    """Deprecated. Please use `shiny.ui.fill.remove_all_fill()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.remove_all_fill()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.fill.remove_all_fill()` instead."
    )
    return main_remove_all_fill(tag)


def is_fill_carrier(tag: Tag) -> bool:
    """Deprecated. Please use a combination of `shiny.ui.fill.is_fillable_container()` and `shiny.ui.fill.is_fill_item()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.is_fill_carrier()` is deprecated. "
        "This method will be removed in a future version, "
        "please use a combination of `shiny.ui.fill.is_fillable_container()` and `shiny.ui.fill.is_fill_item()` instead."
    )
    return main_is_fill_item(main_is_fillable_container(tag))


def is_fillable_container(tag: TagChild) -> bool:
    """Deprecated. Please use `shiny.ui.fill.is_fillable_container()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.is_fillable_container()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.fill.is_fillable_container()` instead."
    )
    return main_is_fillable_container(tag)


def is_fill_item(tag: TagChild) -> bool:
    """Deprecated. Please use `shiny.ui.fill.is_fill_item()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.is_fill_item()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.fill.is_fill_item()` instead."
    )
    return main_is_fill_item(tag)


# ######################
# # Card
# ######################

TagCallable = TagFunction
"""Deprecated. Please use `htmltools.TagFunction"""


class CardItem(MainCardItem):
    """Deprecated. Please use `shiny.ui.CardItem` instead."""

    def __init__(
        self,
        item: TagChild,
    ):
        warn_deprecated(
            "`shiny.experimental.ui.CardItem()` is deprecated. "
            "This class will be removed in a future version, "
            "please use :class:`shiny.ui.CardItem` instead."
        )
        super().__init__(item)


def card_header(
    *args: TagChild | TagAttrs,
    container: TagFunction = tags.div,
    **kwargs: TagAttrValue,
) -> MainCardItem:
    """Deprecated. Please use `shiny.ui.card_header()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.card_header()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.card_header()` instead."
    )
    return main_card_header(*args, container=container, **kwargs)


def card_footer(
    *args: TagChild | TagAttrs,
    **kwargs: TagAttrValue,
) -> MainCardItem:
    """Deprecated. Please use `shiny.ui.card_footer()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.card_footer()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.card_footer()` instead."
    )

    return main_card_footer(*args, **kwargs)


######################
# # Valuebox
######################


def value_box(
    title: TagChild,
    value: TagChild,
    *args: TagChild | TagAttrs,
    showcase: Optional[TagChild] = None,
    showcase_layout: Callable[[TagChild, Tag], MainCardItem] | None = None,
    full_screen: bool = False,
    theme_color: Optional[str] = "primary",
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """Deprecated. Please use `shiny.ui.value_box()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.value_box()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.value_box()` instead."
    )
    return main_value_box(
        title,
        value,
        *args,
        showcase=showcase,
        showcase_layout=showcase_layout,
        full_screen=full_screen,
        theme_color=theme_color,
        height=height,
        max_height=max_height,
        fill=fill,
        class_=class_,
        **kwargs,
    )


def showcase_left_center(
    width: CssUnit = "30%",
    max_height: CssUnit = "100px",
    max_height_full_screen: CssUnit = "67%",
) -> Callable[[TagChild | TagAttrs, Tag], MainCardItem]:
    # TODO-barret; Give better message. These are defunct
    """Deprecated. Please use `shiny.ui.showcase_left_center()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.showcase_left_center()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.showcase_left_center()` instead."
    )
    # TODO-barret; Return new structure
    return main_showcase_left_center(
        width=width,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
    )


def showcase_top_right(
    width: CssUnit = "30%",
    max_height: CssUnit = "75px",
    max_height_full_screen: CssUnit = "67%",
) -> Callable[[TagChild | TagAttrs, Tag], MainCardItem]:
    # TODO-barret; Give better message. These are defunct
    """Deprecated. Please use `shiny.ui.showcase_top_right()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.showcase_top_right()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.showcase_top_right()` instead."
    )
    # TODO-barret; Return new structure
    return main_showcase_top_right(
        width=width,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
    )


# ######################
# # Layout
# ######################
def layout_column_wrap(
    width: Optional[CssUnit],
    *args: TagChild | TagAttrs,
    fixed_width: bool = False,
    heights_equal: Literal["all", "row"] = "all",
    fill: bool = True,
    fillable: bool = True,
    height: Optional[CssUnit] = None,
    height_mobile: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """Deprecated. Please use `shiny.ui.layout_column_wrap()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.layout_column_wrap()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.layout_column_wrap()` instead."
    )
    return main_layout_column_wrap(
        width,
        *args,
        fixed_width=fixed_width,
        heights_equal=heights_equal,
        fill=fill,
        fillable=fillable,
        height=height,
        height_mobile=height_mobile,
        gap=gap,
        class_=class_,
        **kwargs,
    )


# ######################
# # Navs
# ######################


def navset_bar(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    title: TagChild,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[MainSidebar] = None,
    fillable: bool | list[str] = True,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    position: Literal[
        "static-top", "fixed-top", "fixed-bottom", "sticky-top"
    ] = "static-top",
    header: TagChild = None,
    footer: TagChild = None,
    bg: Optional[str] = None,
    # TODO-bslib: default to 'auto', like we have in R (parse color via webcolors?)
    inverse: bool = False,
    collapsible: bool = True,
    fluid: bool = True,
) -> MainNavSetBar:
    """Deprecated. Please use `shiny.ui.navset_bar()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.navset_bar()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.navset_bar()` instead."
    )
    return main_navset_bar(
        *args,
        title=title,
        id=id,
        selected=selected,
        sidebar=sidebar,
        fillable=fillable,
        gap=gap,
        padding=padding,
        position=position,
        header=header,
        footer=footer,
        bg=bg,
        inverse=inverse,
        collapsible=collapsible,
        fluid=fluid,
    )


def navset_card_tab(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[MainSidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> MainNavSetCard:
    """Deprecated. Please use `shiny.ui.navset_card_tab()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.navset_card_tab()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.navset_card_tab()` instead."
    )
    return main_navset_card_tab(
        *args,
        id=id,
        selected=selected,
        sidebar=sidebar,
        header=header,
        footer=footer,
    )


def navset_card_pill(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[MainSidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
    placement: Literal["above", "below"] = "above",
) -> MainNavSetCard:
    """Deprecated. Please use `shiny.ui.navset_card_pill()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.navset_card_pill()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.navset_card_pill()` instead."
    )
    return main_navset_card_pill(
        *args,
        id=id,
        selected=selected,
        sidebar=sidebar,
        header=header,
        footer=footer,
        placement=placement,
    )


# ######################
# # Outputs
# ######################
def output_plot(
    id: str,
    width: str = "100%",
    height: str = "400px",
    *,
    inline: bool = False,
    click: bool | MainClickOpts = False,
    dblclick: bool | MainDblClickOpts = False,
    hover: bool | MainHoverOpts = False,
    brush: bool | MainBrushOpts = False,
    fill: bool | MISSING_TYPE = MISSING,
) -> Tag:
    """Deprecated. Please use `shiny.ui.output_plot()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.output_plot()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.output_plot()` instead."
    )
    return main_output_plot(
        id=id,
        width=width,
        height=height,
        inline=inline,
        click=click,
        dblclick=dblclick,
        hover=hover,
        brush=brush,
        fill=fill,
    )


# @add_example()
def output_image(
    id: str,
    width: str = "100%",
    height: str = "400px",
    *,
    inline: bool = False,
    click: bool | MainClickOpts = False,
    dblclick: bool | MainDblClickOpts = False,
    hover: bool | MainHoverOpts = False,
    brush: bool | MainBrushOpts = False,
    # NEW
    fill: bool = False,
    # /NEW
) -> Tag:
    """Deprecated. Please use `shiny.ui.output_image()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.output_image()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.output_image()` instead."
    )
    return main_output_image(
        id=id,
        width=width,
        height=height,
        inline=inline,
        click=click,
        dblclick=dblclick,
        hover=hover,
        brush=brush,
        fill=fill,
    )


# @add_example()
def output_ui(
    id: str,
    inline: bool = False,
    container: Optional[TagFunction] = None,
    fill: bool = False,
    fillable: bool = False,
    **kwargs: TagAttrValue,
) -> Tag:
    """Deprecated. Please use `shiny.ui.output_ui()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.output_ui()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.output_ui()` instead."
    )
    return main_output_ui(
        id=id,
        inline=inline,
        container=container,
        fill=fill,
        fillable=fillable,
        **kwargs,
    )


# ######################
# # Page
# ######################
def page_sidebar(
    sidebar: MainSidebar | TagChild | TagAttrs,
    *args: TagChild | TagAttrs,
    title: Optional[str | Tag | TagList] = None,
    fillable: bool = True,
    fillable_mobile: bool = False,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """Deprecated. Please use `shiny.ui.page_sidebar()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.page_sidebar()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.page_sidebar()` instead."
    )
    return main_page_sidebar(
        sidebar,
        *args,
        title=title,
        fillable=fillable,
        fillable_mobile=fillable_mobile,
        window_title=window_title,
        lang=lang,
        **kwargs,
    )


def page_navbar(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    title: Optional[str | Tag | TagList] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
    # Only page_navbar gets enhancedtreatement for `fillable`
    # If an `*args`'s `data-value` attr string is in `fillable`, then the component is fillable
    fillable: bool | list[str] = True,
    fillable_mobile: bool = False,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    bg: Optional[str] = None,
    inverse: bool = True,
    collapsible: bool = True,
    fluid: bool = True,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
) -> Tag:
    """Deprecated. Please use `shiny.ui.page_navbar()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.page_navbar()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.page_navbar()` instead."
    )
    return main_page_navbar(
        *args,
        title=title,
        id=id,
        selected=selected,
        sidebar=sidebar,
        fillable=fillable,
        fillable_mobile=fillable_mobile,
        gap=gap,
        padding=padding,
        position=position,
        header=header,
        footer=footer,
        bg=bg,
        inverse=inverse,
        collapsible=collapsible,
        fluid=fluid,
        window_title=window_title,
        lang=lang,
    )


def page_fillable(
    *args: TagChild | TagAttrs,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    gap: Optional[CssUnit] = None,
    fillable_mobile: bool = False,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """Deprecated. Please use `shiny.ui.page_fillable()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.page_fillable()` is deprecated. "
        "This method will be removed in a future version, "
        "please use `shiny.ui.page_fillable()` instead."
    )
    return main_page_fillable(
        *args,
        padding=padding,
        gap=gap,
        fillable_mobile=fillable_mobile,
        title=title,
        lang=lang,
        **kwargs,
    )
