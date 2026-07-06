from __future__ import annotations

import base64
import datetime
import os
from pathlib import Path

import pytest
from examples.example_apps import reruns, reruns_delay
from mod_state import expect_default_mod_state, expect_mod_state
from playwright.sync_api import Download, Page

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


def expect_default_outputs(page: Page, module_id: str):
    expect_outputs(page, module_id, "a", 0)


def expect_download_contents(
    download: Download,
    destination: Path,
    suggested_filename: str,
    expected_contents: str,
) -> None:
    download.save_as(str(destination))
    assert download.suggested_filename == suggested_filename
    assert destination.read_text() == expected_contents


# Sidebars do not seem to work on webkit. Skipping test on webkit
@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_module_support(page: Page, local_app: ShinyAppProc, tmp_path: Path) -> None:
    page.set_viewport_size({"width": 3000, "height": 6000})
    page.goto(local_app.url)

    # Update mod2 once; one pass covers ID resolution without multiplying remote
    # WebKit locator/action cost.
    update_mod2 = controller.InputActionButton(page, "update_mod2")
    update_mod2.click()
    controller.InputActionButton(page, "mod2-input_action_button").click()
    controller.InputActionLink(page, "mod2-input_action_link").click()
    with page.expect_download() as download_button_info:
        download_button = controller.DownloadButton(page, "mod2-download_button")
        download_button.click()
        download = download_button_info.value
        expect_download_contents(
            download=download,
            destination=tmp_path / "download_button-mod2.csv",
            suggested_filename="download_button-mod2.csv",
            expected_contents="session,type,count\nmod2,button,1\n",
        )
    with page.expect_download() as download_link_info:
        download_link = controller.DownloadLink(page, "mod2-download_link")
        download_link.click()
        download = download_link_info.value
        expect_download_contents(
            download=download,
            destination=tmp_path / "download_link-mod2.csv",
            suggested_filename="download_link-mod2.csv",
            expected_contents="session,type,count\nmod2,link,1\n",
        )

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
        accordion=("b",),
        popover=True,
        tooltip=True,
        input_action_button=1,
        input_action_link=1,
        input_file="test_file.txt",
        input_checkbox=True,
        input_checkbox_group=("a", "c", "d"),
        input_date=datetime.date(2023, 8, 25),
        input_date_range=(datetime.date(2023, 8, 26), datetime.date(2023, 8, 28)),
        input_numeric=1,
        input_password="password1",
        input_radio_buttons="b",
        input_select="b",
        input_selectize="b",
        input_slider=1,
        input_switch=True,
        input_text="text1",
        input_text_area="text_area1",
        navset_bar="b",
        navset_card_pill="b",
        navset_card_tab="b",
        navset_hidden="b",
        navset_pill="b",
        navset_tab="b",
    )
    expect_outputs(page, "mod2", "b", 1)
