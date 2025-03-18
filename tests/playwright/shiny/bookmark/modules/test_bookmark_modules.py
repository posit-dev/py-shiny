import os
from pathlib import Path

import pytest
from playwright.sync_api import Page

from shiny.playwright.controller import InputRadioButtons, OutputCode
from shiny.run import ShinyAppProc, run_shiny_app


@pytest.mark.parametrize(
    "app_name,mod0_key,mod1_key",
    [
        # Express mode
        ("app-express.py", "mod0", "mod3"),
        # Core mode
        ("app-core.py", "mod0", "mod3"),
        # Recursive modules within core mode
        ("app-core-recursive.py", "mod3", "mod3-sub2-sub1-sub0"),
    ],
)
@pytest.mark.parametrize("bookmark_store", ["url", "server"])
def test_bookmark_modules(
    page: Page,
    bookmark_store: str,
    app_name: str,
    mod0_key: str,
    mod1_key: str,
) -> None:

    # Set environment variable before the app starts
    os.environ["SHINY_BOOKMARK_STORE"] = bookmark_store

    app: ShinyAppProc = run_shiny_app(
        Path(__file__).parent / app_name,
        wait_for_start=True,
    )

    try:

        page.goto(app.url)

        OutputCode(page, "bookmark_store").expect_value(bookmark_store)

        def expect_mod(mod_key: str, values: list[str]):
            assert len(values) == 4
            OutputCode(page, f"{mod_key}-value").expect_value(str(values))
            InputRadioButtons(page, f"{mod_key}-btn1").expect_selected(values[0])
            InputRadioButtons(page, f"{mod_key}-btn2").expect_selected(values[1])
            InputRadioButtons(page, f"{mod_key}-dyn1").expect_selected(values[2])
            InputRadioButtons(page, f"{mod_key}-dyn2").expect_selected(values[3])

        def set_mod(mod_key: str, values: list[str]):
            assert len(values) == 4
            InputRadioButtons(page, f"{mod_key}-btn1").set(values[0])
            InputRadioButtons(page, f"{mod_key}-btn2").set(values[1])
            InputRadioButtons(page, f"{mod_key}-dyn1").set(values[2])
            InputRadioButtons(page, f"{mod_key}-dyn2").set(values[3])

        expect_mod(mod0_key, ["a", "a", "a", "a"])
        expect_mod(mod1_key, ["a", "a", "a", "a"])

        set_mod(mod0_key, ["b", "b", "c", "c"])

        expect_mod(mod0_key, ["b", "b", "c", "c"])
        expect_mod(mod1_key, ["a", "a", "a", "a"])

        page.reload()

        expect_mod(mod0_key, ["b", "b", "c", "c"])
        expect_mod(mod1_key, ["a", "a", "a", "a"])

        if bookmark_store == "url":
            assert "_inputs_" in page.url
            assert "_values_" in page.url
        if bookmark_store == "server":
            assert "_state_id_" in page.url

    finally:
        app.close()
        os.environ.pop("SHINY_BOOKMARK_STORE")
