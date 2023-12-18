"""
Tools for creating user interfaces including: custom components, HTML components,
layout helpers, page-level containers, and more.
"""

from ._bootstrap import (
    row,
    column,
    panel_well,
    panel_conditional,
    panel_title,
    panel_fixed,
    panel_absolute,
    help_text,
)
from ._sidebar import (
    Sidebar,
    sidebar,
    layout_sidebar,
    update_sidebar,
    panel_sidebar,
    panel_main,
)

from ._layout import layout_column_wrap
from ._layout_columns import layout_columns


# Expose the following modules for extended usage: ex: ui.fill.as_fill_item(x)
from . import css  # noqa: F401  # pyright: ignore[reportUnusedImport]
from . import fill  # noqa: F401  # pyright: ignore[reportUnusedImport]

from ._card import (
    card,
    CardItem,
    card_header,
    card_footer,
)

from ._accordion import (
    AccordionPanel,
    accordion,
    accordion_panel,
    insert_accordion_panel,
    remove_accordion_panel,
    update_accordion,
    update_accordion_panel,
)

from ._download_button import download_button, download_link
from ._plot_output_opts import brush_opts, click_opts, dblclick_opts, hover_opts
from ._include_helpers import include_css, include_js
from ._input_action_button import input_action_button, input_action_link
from ._input_check_radio import (
    input_checkbox,
    input_checkbox_group,
    input_switch,
    input_radio_buttons,
)
from ._input_date import input_date, input_date_range
from ._input_file import input_file
from ._input_numeric import input_numeric
from ._input_password import input_password
from ._input_select import input_select, input_selectize
from ._input_slider import input_slider, SliderValueArg, SliderStepArg, AnimationOptions
from ._input_text import input_text, input_text_area
from ._input_update import (
    update_action_button,
    update_action_link,
    update_checkbox,
    update_switch,
    update_checkbox_group,
    update_radio_buttons,
    update_date,
    update_date_range,
    update_numeric,
    update_select,
    update_selectize,
    update_slider,
    update_text,
    update_text_area,
    update_navs,
    update_tooltip,
    update_popover,
)
from ._insert import insert_ui, remove_ui
from ._markdown import markdown
from ._modal import modal_button, modal, modal_show, modal_remove
from ._navs import (
    nav_panel,
    nav_menu,
    nav_control,
    nav_spacer,
    navset_tab,
    navset_pill,
    navset_underline,
    navset_card_pill,
    navset_card_underline,
    navset_card_tab,
    navset_pill_list,
    navset_hidden,
    navset_bar,
    # Deprecated
    navset_pill_card,
    navset_tab_card,
    nav,
)
from ._notification import notification_show, notification_remove
from ._output import (
    output_plot,
    output_image,
    output_text,
    output_text_verbatim,
    output_table,
    output_ui,
)
from ._page import (
    page_sidebar,
    page_navbar,
    page_fillable,
    page_fluid,
    page_fixed,
    page_bootstrap,
    page_output,
)
from ._progress import Progress

from .dataframe import output_data_frame

from ._popover import popover
from ._valuebox import (
    value_box,
    value_box_theme,
    showcase_bottom,
    showcase_left_center,
    showcase_top_right,
    ValueBoxTheme,
    ShowcaseLayout,
)
from ._tooltip import tooltip


from htmltools import (
    TagList,
    Tag,
    TagChild,
    TagAttrs,
    TagAttrValue,
    tags,
    HTML,
    head_content,
    p,
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    a,
    br,
    div,
    span,
    pre,
    code,
    img,
    strong,
    em,
    hr,
)


__all__ = (
    # _bootstrap
    "row",
    "column",
    "panel_well",
    "panel_conditional",
    "panel_title",
    "panel_fixed",
    "panel_absolute",
    "help_text",
    # _sidebar
    "Sidebar",
    "sidebar",
    "layout_sidebar",
    "update_sidebar",
    "panel_sidebar",
    "panel_main",
    # _layout
    "layout_columns",
    "layout_column_wrap",
    # _card
    "CardItem",
    "card",
    "card_header",
    "card_footer",
    # _accordion
    "AccordionPanel",
    "accordion",
    "accordion_panel",
    "insert_accordion_panel",
    "remove_accordion_panel",
    "update_accordion",
    "update_accordion_panel",
    # _download_button
    "download_button",
    "download_link",
    # _plot_output_opts
    "brush_opts",
    "click_opts",
    "dblclick_opts",
    "hover_opts",
    # _include_helpers
    "include_css",
    "include_js",
    # _input_action_button
    "input_action_button",
    "input_action_link",
    # _input_check_radio
    "input_checkbox",
    "input_checkbox_group",
    "input_switch",
    "input_radio_buttons",
    # _input_date
    "input_date",
    "input_date_range",
    # _input_file
    "input_file",
    # _input_numeric
    "input_numeric",
    # _input_password
    "input_password",
    # _input_select
    "input_select",
    "input_selectize",
    # _input_slider
    "input_slider",
    "SliderValueArg",
    "SliderStepArg",
    "AnimationOptions",
    # _input_text
    "input_text",
    "input_text_area",
    # _input_update
    "update_action_button",
    "update_action_link",
    "update_checkbox",
    "update_switch",
    "update_checkbox_group",
    "update_radio_buttons",
    "update_date",
    "update_date_range",
    "update_numeric",
    "update_select",
    "update_selectize",
    "update_slider",
    "update_text",
    "update_text_area",
    "update_navs",
    "update_tooltip",
    "update_popover",
    # _insert
    "insert_ui",
    "remove_ui",
    # _markdown
    "markdown",
    # _modal
    "modal_button",
    "modal",
    "modal_show",
    "modal_remove",
    # _navs
    "nav_panel",
    "nav_menu",
    "nav_control",
    "nav_spacer",
    "navset_tab",
    "navset_card_tab",
    "navset_card_pill",
    "navset_card_underline",
    "navset_pill",
    "navset_underline",
    "navset_pill_list",
    "navset_hidden",
    "navset_bar",
    # # Deprecated
    "navset_pill_card",
    "navset_tab_card",
    "nav",
    # _notification
    "notification_show",
    "notification_remove",
    # _output
    "output_data_frame",  # dataframe
    "output_plot",
    "output_image",
    "output_text",
    "output_text_verbatim",
    "output_table",
    "output_ui",
    "page_output",
    # _page
    "page_sidebar",
    "page_navbar",
    "page_fillable",
    "page_fluid",
    "page_fixed",
    "page_bootstrap",
    # _popover
    "popover",
    # _valuebox
    "value_box",
    "value_box_theme",
    "showcase_bottom",
    "showcase_left_center",
    "showcase_top_right",
    "ValueBoxTheme",
    "ShowcaseLayout",
    # _tooltip
    "tooltip",
    # _progress
    "Progress",
    # Items below are from htmltools
    "TagList",
    "Tag",
    "TagChild",
    "TagAttrs",
    "TagAttrValue",
    "tags",
    "HTML",
    "head_content",
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "a",
    "br",
    "div",
    "span",
    "pre",
    "code",
    "img",
    "strong",
    "em",
    "hr",
)
