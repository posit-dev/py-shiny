from __future__ import annotations

import datetime

from controls import OutputTextVerbatim
from playwright.sync_api import Page


def expect_state(
    page: Page,
    module_id: str,
    key: str,
    value: object,
):
    new_module_id = f"{module_id}-" if module_id else ""
    OutputTextVerbatim(
        page,
        f"{new_module_id}status_{key}",
    ).expect_value(f"ui.{key}: `{value}`")


def expect_x_state(
    page: Page,
    module_id: str,
    key: str,
    value: object,
):
    new_module_id = f"{module_id}-" if module_id else ""
    new_key = key.replace("x_", "")
    OutputTextVerbatim(
        page,
        f"{new_module_id}status_x_{new_key}",
    ).expect_value(f"x.ui.{new_key}: `{value}`")


def expect_mod_state(
    page: Page,
    module_id: str,
    *,
    sidebar: bool,
    accordion: tuple[str, ...],
    popover: bool,
    tooltip: bool,
    input_action_button: int,
    input_action_link: int,
    input_file: str | None,
    input_checkbox: bool,
    input_checkbox_group: tuple[str, ...],
    input_date: datetime.date | str,
    input_date_range: tuple[datetime.date, datetime.date],
    input_numeric: int,
    input_password: str,
    input_radio_buttons: str,
    input_select: str,
    input_selectize: str,
    input_slider: int,
    input_switch: bool,
    input_text: str,
    input_text_area: str,
    navset_bar: str,
    navset_card_pill: str,
    navset_card_tab: str,
    navset_hidden: str,
    navset_pill: str,
    navset_tab: str,
):
    # print(str(locals().items()))
    # Must realize the locals before iterating
    for key, value in list(locals().items()):
        if key == "page" or key == "module_id":
            continue
        if key.startswith("x_"):
            expect_x_state(page, module_id, key, value)
        else:
            expect_state(page, module_id, key, value)


def expect_default_mod_state(page: Page, module_id: str):
    expect_mod_state(
        page,
        module_id=module_id,
        sidebar=True,
        accordion=("a",),
        popover=False,
        tooltip=False,
        input_action_button=0,
        input_action_link=0,
        input_file=None,
        input_checkbox=False,
        input_checkbox_group=("b", "c", "d"),
        input_date=datetime.date(2023, 8, 24),
        input_date_range=(datetime.date(2023, 8, 25), datetime.date(2023, 8, 27)),
        input_numeric=0,
        input_password="password0",
        input_radio_buttons="a",
        input_select="a",
        input_selectize="a",
        input_slider=0,
        input_switch=False,
        input_text="text0",
        input_text_area="text_area0",
        navset_bar="a",
        navset_card_pill="a",
        navset_card_tab="a",
        navset_hidden="a",
        navset_pill="a",
        navset_tab="a",
    )
