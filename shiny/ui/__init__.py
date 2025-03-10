"""
Tools for creating user interfaces including: custom components, HTML components,
layout helpers, page-level containers, and more.
"""

from htmltools import (
    HTML,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagList,
    a,
    br,
    code,
    div,
    em,
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    head_content,
    hr,
    img,
    p,
    pre,
    span,
    strong,
    tags,
)

from ..bookmark._button import input_bookmark_button

# The css module is for internal use, so we won't re-export it.
# Expose the fill module for extended usage: ex: ui.fill.as_fill_item(x).
# Export busy_indicators module
from . import (  # noqa: F401
    busy_indicators,
    css,  # pyright: ignore[reportUnusedImport]
    fill,
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
from ._bootstrap import (
    column,
    help_text,
    panel_absolute,
    panel_conditional,
    panel_fixed,
    panel_title,
    panel_well,
    row,
)
from ._card import (
    CardItem,
    card,
    card_body,
    card_footer,
    card_header,
)
from ._chat import Chat, chat_ui
from ._download_button import download_button, download_link
from ._include_helpers import include_css, include_js
from ._input_action_button import input_action_button, input_action_link
from ._input_check_radio import (
    input_checkbox,
    input_checkbox_group,
    input_radio_buttons,
    input_switch,
)
from ._input_dark_mode import input_dark_mode, update_dark_mode
from ._input_date import input_date, input_date_range
from ._input_file import input_file
from ._input_numeric import input_numeric
from ._input_password import input_password
from ._input_select import input_select, input_selectize
from ._input_slider import AnimationOptions, SliderStepArg, SliderValueArg, input_slider
from ._input_task_button import bind_task_button, input_task_button
from ._input_text import input_text, input_text_area
from ._input_update import (
    update_action_button,
    update_action_link,
    update_checkbox,
    update_checkbox_group,
    update_date,
    update_date_range,
    update_navs,
    update_numeric,
    update_popover,
    update_radio_buttons,
    update_select,
    update_selectize,
    update_slider,
    update_switch,
    update_task_button,
    update_text,
    update_text_area,
    update_tooltip,
)
from ._insert import insert_ui, remove_ui
from ._layout import layout_column_wrap
from ._layout_columns import layout_columns
from ._markdown import markdown
from ._markdown_stream import MarkdownStream, output_markdown_stream
from ._modal import modal, modal_button, modal_remove, modal_show
from ._navs import (
    nav_control,
    nav_menu,
    nav_panel,
    nav_spacer,
    navbar_options,
    navset_bar,
    navset_card_pill,
    navset_card_tab,
    navset_card_underline,
    navset_hidden,
    navset_pill,
    navset_pill_list,
    navset_tab,
    navset_underline,
)
from ._notification import notification_remove, notification_show
from ._output import (
    output_code,
    output_image,
    output_plot,
    output_table,
    output_text,
    output_text_verbatim,
    output_ui,
)
from ._page import (
    page_auto,
    page_bootstrap,
    page_fillable,
    page_fixed,
    page_fluid,
    page_navbar,
    page_output,
    page_sidebar,
)
from ._plot_output_opts import brush_opts, click_opts, dblclick_opts, hover_opts
from ._popover import popover
from ._progress import Progress
from ._sidebar import (
    Sidebar,
    layout_sidebar,
    sidebar,
    update_sidebar,
)
from ._theme import Theme
from ._tooltip import tooltip
from ._utils import js_eval
from ._valuebox import (
    ShowcaseLayout,
    ValueBoxTheme,
    showcase_bottom,
    showcase_left_center,
    showcase_top_right,
    value_box,
    value_box_theme,
)
from .dataframe import output_data_frame

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
    # _layout
    "layout_columns",
    "layout_column_wrap",
    # _card
    "CardItem",
    "card",
    "card_body",
    "card_header",
    "card_footer",
    # _chat
    "Chat",
    "chat_ui",
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
    # _input_dark_mode
    "input_dark_mode",
    "update_dark_mode",
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
    # _input_task_button
    "bind_task_button",
    "input_task_button",
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
    "update_task_button",
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
    # _markdown_stream
    "output_markdown_stream",
    "MarkdownStream",
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
    "navbar_options",
    # _notification
    "notification_show",
    "notification_remove",
    # _output
    "output_data_frame",  # dataframe
    "output_plot",
    "output_image",
    "output_text",
    "output_code",
    "output_text_verbatim",
    "output_table",
    "output_ui",
    # _page
    "page_sidebar",
    "page_navbar",
    "page_fillable",
    "page_fluid",
    "page_fixed",
    "page_bootstrap",
    "page_auto",
    "page_output",
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
    # _theme
    "Theme",
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
    # Submodules
    "busy_indicators",
    "fill",
    # utils
    "js_eval",
    # bookmark
    "input_bookmark_button",
)
