from __future__ import annotations

import base64
import datetime
import os
from pathlib import Path

from conftest import ShinyAppProc

# TODO-karan; Create OutputDataFrame class
# TODO-karan: Create classes for DownloadLink, DownloadButton
from controls import (
    InputActionButton,
    InputActionLink,
    InputCheckbox,
    InputCheckboxGroup,
    InputDate,
    InputDateRange,
    InputFile,
    InputNumeric,
    InputRadioButtons,
    InputSelect,
    InputSelectize,
    InputSlider,
    InputSwitch,
    InputText,
    InputTextArea,
    OutputImage,
    OutputTable,
    OutputText,
    OutputTextVerbatim,
    OutputUi,
)
from playwright.sync_api import Page
from playwright.sync_api import expect as playwright_expect

from shiny._utils import guess_mime_type


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
    x_sidebar: bool,
    x_accordion: tuple[str, ...],
    x_popover: bool,
    x_tooltip: bool,
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
        x_sidebar=True,
        x_accordion=("a",),
        x_popover=False,
        x_tooltip=False,
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


img_path = Path(__file__).parent / "imgs"
penguin_imgs = [str(img_path / img) for img in os.listdir(img_path)]


def expect_outputs(page: Page, module_id: str, letter: str, count: int):
    def resolve_id(id: str):
        if module_id:
            return f"{module_id}-{id}"
        return id

    # TODO-karan; Test with OutputDataFrame class
    playwright_expect(
        page.locator("#" + resolve_id("out_data_frame")).locator("table tbody tr")
    ).to_have_count(count + 1)

    OutputText(page, resolve_id("out_text")).expect_value(
        f"Output text content. `input.radio_buttons()`: `{letter}`"
    )
    OutputTextVerbatim(page, resolve_id("out_text_verbatim")).expect_value(
        f"Output text verbatim content. `input.radio_buttons()`: `{letter}`"
    )
    OutputTable(page, resolve_id("out_table")).expect_n_row(count + 1)

    # Mirrors ImageTransformer implementation
    src = penguin_imgs[count]
    with open(src, "rb") as f:
        data = base64.b64encode(f.read())
        data_str = data.decode("utf-8")
    content_type = guess_mime_type(src)
    img_src = f"data:{content_type};base64,{data_str}"
    # Done Mirror
    OutputImage(page, resolve_id("out_image")).expect_img_src(img_src)

    # TODO-future; Test OutputPlot
    # OutputPlot(page, resolve_id("out_plot")).

    OutputUi(page, resolve_id("out_ui")).expect.to_have_text(
        f"Output UI content. input.radio_buttons(): {letter}"
    )


def expect_labels(page: Page, module_id: str):
    def resolve_id(id: str):
        if module_id:
            return f"{module_id}-{id}"
        return id

    InputNumeric(page, resolve_id("input_numeric")).expect_label("Numeric")
    InputText(page, resolve_id("input_text")).expect_label("Text")
    InputTextArea(page, resolve_id("input_text_area")).expect_label("Text area")
    InputSelect(page, resolve_id("input_select")).expect_label("Select")
    InputSelectize(page, resolve_id("input_selectize")).expect_label("Selectize")
    InputCheckbox(page, resolve_id("input_checkbox")).expect_label("Checkbox")
    InputSwitch(page, resolve_id("input_switch")).expect_label("Switch")
    InputCheckboxGroup(page, resolve_id("input_checkbox_group")).expect_label(
        "Checkbox group"
    )
    InputRadioButtons(page, resolve_id("input_radio_buttons")).expect_label(
        "Radio buttons"
    )
    InputFile(page, resolve_id("input_file")).expect_label("File")
    InputSlider(page, resolve_id("input_slider")).expect_label("Slider")
    InputDate(page, resolve_id("input_date")).expect_label("Date")
    InputDateRange(page, resolve_id("input_date_range")).expect_label("Date range")


def expect_default_outputs(page: Page, module_id: str):
    expect_outputs(page, module_id, "a", 0)


def test_module_support(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Verify reset state
    for mod_id in ("", "mod1", "mod2"):
        expect_default_mod_state(page, mod_id)
        expect_default_outputs(page, mod_id)
        expect_labels(page, mod_id)

    # Click x3 `update_mod2`
    update_mod2 = InputActionButton(page, "update_mod2")
    for i in range(3):
        update_mod2.click()
        InputActionButton(page, "mod2-input_action_button").click()
        InputActionLink(page, "mod2-input_action_link").click()
        # TODO-karan; click Download button using DownloadButton class
        with page.expect_download() as download_button_info:
            page.locator("#mod2-download_button").click()
            download = download_button_info.value
            # wait for download to complete
            download_path = download.path()
            assert download.suggested_filename == "download_button-mod2.csv"
            assert download_path is not None
            with open(download_path, "r") as f:
                assert f.read() == f"session,type,count\nmod2,button,{i + 1}\n"
        # TODO-karan; click Download link using DownloadLink class
        with page.expect_download() as download_link_info:
            page.locator("#mod2-download_link").click()
            download = download_link_info.value
            # wait for download to complete
            download_path = download.path()
            assert download.suggested_filename == "download_link-mod2.csv"
            assert download_path is not None
            with open(download_path, "r") as f:
                assert f.read() == f"session,type,count\nmod2,link,{i + 1}\n"

    InputFile(page, "mod2-input_file").set(Path(__file__).parent / "test_file.txt")

    # Make sure the global session and first module was not affected
    expect_default_mod_state(page, "")
    expect_default_outputs(page, "")
    expect_default_mod_state(page, "mod1")
    expect_default_outputs(page, "mod1")

    # Make sure the second module was affected
    expect_mod_state(
        page,
        module_id="mod2",
        x_sidebar=False,
        x_accordion=("d",),
        x_popover=True,
        x_tooltip=True,
        input_action_button=3,
        input_action_link=3,
        input_file="test_file.txt",
        input_checkbox=True,
        input_checkbox_group=("a", "b", "c"),
        input_date=datetime.date(2023, 8, 27),
        input_date_range=(datetime.date(2023, 8, 28), datetime.date(2023, 8, 30)),
        input_numeric=3,
        input_password="password3",
        input_radio_buttons="d",
        input_select="d",
        input_selectize="d",
        input_slider=3,
        input_switch=True,
        input_text="text3",
        input_text_area="text_area3",
        navset_bar="d",
        navset_card_pill="d",
        navset_card_tab="d",
        navset_hidden="d",
        navset_pill="d",
        navset_tab="d",
    )
    expect_outputs(page, "mod2", "d", 3)
