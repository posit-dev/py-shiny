# Experimental

from ._valuebox import showcase_left_center, showcase_top_right, value_box
from ._card import (
    ImgContainer,
    card,
    card_body,
    card_image,
    card_title,
)

from ._deprecated import (
    # Input Switch
    toggle_switch,
    # Input Text Area
    input_text_area,
    # Navs
    navset_pill_card,
    navset_tab_card,
    # Sidebar
    sidebar_toggle,
    panel_sidebar,
    panel_main,
    DeprecatedPanelSidebar,
    DeprecatedPanelMain,
    # Tooltip
    tooltip_update,
    tooltip_toggle,
    tooltip,
    toggle_tooltip,
    update_tooltip,
    # Css
    CssUnit,
    as_css_padding,
    as_css_unit,
    as_width_unit,
    # Popover
    popover,
    toggle_popover,
    update_popover,
    # # Accordion
    # AccordionPanel,
    # accordion,
    # accordion_panel,
    # accordion_panel_close,
    # accordion_panel_insert,
    # accordion_panel_open,
    # accordion_panel_remove,
    # accordion_panel_set,
    # update_accordion_panel,
    # Fill
    # FillingLayout,
    as_fill_carrier,
    as_fill_item,
    as_fillable_container,
    is_fill_carrier,
    is_fill_item,
    is_fillable_container,
    remove_all_fill,
    # Card
    TagCallable,
    WrapperCallable,
    CardItem,
    card_footer,
    card_header,
    # Layout
    layout_column_wrap,
    # Navs
    navset_bar,
    navset_card_pill,
    navset_card_tab,
)


# TODO-barret; Remove or trim
from ._accordion import (
    AccordionPanel,
    accordion,
    accordion_panel,
    accordion_panel_close,
    accordion_panel_insert,
    accordion_panel_open,
    accordion_panel_remove,
    accordion_panel_set,
    update_accordion_panel,
)
from ._output import output_image, output_plot, output_ui
from ._page import page_fillable, page_navbar, page_sidebar
from ._sidebar import (
    Sidebar,
    layout_sidebar,
    sidebar,
    toggle_sidebar,
)


__all__ = (
    # Sidebar
    "Sidebar",
    "layout_sidebar",
    "sidebar",
    "toggle_sidebar",
    # Page
    "page_sidebar",
    "page_fillable",
    "page_navbar",
    # Card
    "ImgContainer",
    "TagCallable",
    "card",
    "card_title",
    "card_body",
    "card_image",
    # ValueBox
    "value_box",
    "showcase_left_center",
    "showcase_top_right",
    # Output
    "output_image",
    "output_plot",
    "output_ui",
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
    # Deprecated
    # # Input Switch
    "toggle_switch",
    # # Input Text Area
    "input_text_area",
    # # Navs
    "navset_pill_card",
    "navset_tab_card",
    # # Tooltip
    "tooltip",
    "toggle_tooltip",
    "update_tooltip",
    "tooltip_update",
    "tooltip_toggle",
    # # Sidebar
    "sidebar_toggle",
    "panel_sidebar",
    "panel_main",
    "DeprecatedPanelSidebar",
    "DeprecatedPanelMain",
    # # Css
    "CssUnit",
    "as_css_unit",
    "as_css_padding",
    "as_width_unit",
    # # Popover
    "popover",
    "toggle_popover",
    "update_popover",
    # # # Accordion
    # "AccordionPanel",
    # "accordion",
    # "accordion_panel",
    # "accordion_panel_close",
    # "accordion_panel_insert",
    # "accordion_panel_open",
    # "accordion_panel_remove",
    # "accordion_panel_set",
    # "update_accordion_panel",
    # # Fill
    # "FillingLayout",
    "as_fill_carrier",
    "as_fillable_container",
    "as_fill_item",
    "remove_all_fill",
    "is_fill_carrier",
    "is_fillable_container",
    "is_fill_item",
    # # Card
    "TagCallable",
    "WrapperCallable",
    "CardItem",
    "card_header",
    "card_footer",
    # # Layout
    "layout_column_wrap",
    # # Navs
    "navset_bar",
    "navset_card_tab",
    "navset_card_pill",
)
