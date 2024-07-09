from __future__ import annotations

import base64
import datetime
import os
from pathlib import Path

import pytest
from examples.example_apps import reruns, reruns_delay
from mod_state import expect_default_mod_state, expect_mod_state
from playwright.sync_api import Page

from shiny._utils import guess_mime_type
from shiny.playwright import controller
from shiny.run import ShinyAppProc

img_path = Path(__file__).parent / "imgs"
penguin_imgs = [str(img_path / img) for img in os.listdir(img_path)]


def expect_outputs(page: Page, module_id: str, letter: str, count: int):
    def resolve_id(id: str):
        if module_id:
            return f"{module_id}-{id}"
        return id

    dataframe = controller.OutputDataFrame(page, resolve_id("out_data_frame"))
    dataframe.expect_nrow(count + 1)

    controller.OutputText(page, resolve_id("out_text")).expect_value(
        f"Output text content. `input.radio_buttons()`: `{letter}`"
    )
    controller.OutputTextVerbatim(page, resolve_id("out_text_verbatim")).expect_value(
        f"Output text verbatim content. `input.radio_buttons()`: `{letter}`"
    )
    controller.OutputTable(page, resolve_id("out_table")).expect_nrow(count + 1)

    # Mirrors ImageTransformer implementation
    src = penguin_imgs[count]
    with open(src, "rb") as f:
        data = base64.b64encode(f.read())
        data_str = data.decode("utf-8")
    content_type = guess_mime_type(src)
    img_src = f"data:{content_type};base64,{data_str}"
    # Done Mirror
    controller.OutputImage(page, resolve_id("out_image")).expect_img_src(img_src)

    # TODO-future; Test OutputPlot
    # controller.OutputPlot(page, resolve_id("out_plot")).

    controller.OutputUi(page, resolve_id("out_ui")).expect.to_have_text(
        f"Output UI content. input.radio_buttons(): {letter}"
    )


def expect_labels(page: Page, module_id: str):
    def resolve_id(id: str):
        if module_id:
            return f"{module_id}-{id}"
        return id

    controller.InputNumeric(page, resolve_id("input_numeric")).expect_label("Numeric")
    controller.InputText(page, resolve_id("input_text")).expect_label("Text")
    controller.InputTextArea(page, resolve_id("input_text_area")).expect_label(
        "Text area"
    )
    controller.InputSelect(page, resolve_id("input_select")).expect_label("Select")
    controller.InputSelectize(page, resolve_id("input_selectize")).expect_label(
        "Selectize"
    )
    controller.InputCheckbox(page, resolve_id("input_checkbox")).expect_label(
        "Checkbox"
    )
    controller.InputSwitch(page, resolve_id("input_switch")).expect_label("Switch")
    controller.InputCheckboxGroup(
        page, resolve_id("input_checkbox_group")
    ).expect_label("Checkbox group")
    controller.InputRadioButtons(page, resolve_id("input_radio_buttons")).expect_label(
        "Radio buttons"
    )
    controller.InputFile(page, resolve_id("input_file")).expect_label("File")
    controller.InputSlider(page, resolve_id("input_slider")).expect_label("Slider")
    controller.InputDate(page, resolve_id("input_date")).expect_label("Date")
    controller.InputDateRange(page, resolve_id("input_date_range")).expect_label(
        "Date range"
    )


def expect_default_outputs(page: Page, module_id: str):
    expect_outputs(page, module_id, "a", 0)


# Sidebars do not seem to work on webkit. Skipping test on webkit
@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_module_support(page: Page, local_app: ShinyAppProc) -> None:
    page.set_viewport_size({"width": 3000, "height": 6000})
    page.goto(local_app.url)

    # Verify reset state
    for mod_id in ("", "mod1", "mod2"):
        expect_default_mod_state(page, mod_id)
        expect_default_outputs(page, mod_id)
        expect_labels(page, mod_id)

    # Click x3 `update_mod2`
    update_mod2 = controller.InputActionButton(page, "update_mod2")
    for i in range(3):
        update_mod2.click()
        controller.InputActionButton(page, "mod2-input_action_button").click()
        controller.InputActionLink(page, "mod2-input_action_link").click()
        with page.expect_download() as download_button_info:
            download_button = controller.DownloadButton(page, "mod2-download_button")
            download_button.click()
            download = download_button_info.value
            # wait for download to complete
            download_path = download.path()
            assert download.suggested_filename == "download_button-mod2.csv"
            assert download_path is not None
            with open(download_path, "r") as f:
                assert f.read() == f"session,type,count\nmod2,button,{i + 1}\n"
        with page.expect_download() as download_link_info:
            download_link = controller.DownloadLink(page, "mod2-download_link")
            download_link.click()
            download = download_link_info.value
            # wait for download to complete
            download_path = download.path()
            assert download.suggested_filename == "download_link-mod2.csv"
            assert download_path is not None
            with open(download_path, "r") as f:
                assert f.read() == f"session,type,count\nmod2,link,{i + 1}\n"

    controller.InputFile(page, "mod2-input_file").set(
        Path(__file__).parent / "test_file.txt"
    )

    # Make sure the global session and first module was not affected
    expect_default_mod_state(page, "")
    expect_default_outputs(page, "")
    expect_default_mod_state(page, "mod1")
    expect_default_outputs(page, "mod1")

    # Make sure the second module was affected
    expect_mod_state(
        page,
        module_id="mod2",
        sidebar=False,
        accordion=("d",),
        popover=True,
        tooltip=True,
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
