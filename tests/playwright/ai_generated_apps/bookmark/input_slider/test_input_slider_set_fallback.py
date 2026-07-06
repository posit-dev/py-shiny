"""Regression test for `InputSlider.set()`'s direct-drag implementation.

`set()` computes the target value's exact position from the slider's step
configuration and drags the handle straight there, verifying the landing
position against the widget's internal state. Older sweep-based versions could
miss the target when the browser coalesced or dropped mouse-move events (seen
on webkit under CI load). This test drags the handle to an extreme with raw
mouse events first, then verifies `set()` still lands exactly on the target.
"""

import pytest
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-express.py"])


def test_set_from_extreme_position(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    slider = controller.InputSlider(page, "basic")
    value_out = controller.OutputText(page, "basic_text")
    slider.expect_value("50")

    # Park the handle at the far left with raw mouse events
    handle = slider.loc_irs.locator("> .irs-handle")
    handle_bb = handle.bounding_box()
    grid = slider.loc_irs.locator("> .irs > .irs-line")
    grid_bb = grid.bounding_box()
    assert handle_bb is not None and grid_bb is not None
    y = handle_bb["y"] + handle_bb["height"] / 2
    mouse = page.mouse
    mouse.move(handle_bb["x"] + handle_bb["width"] / 2, y)
    mouse.down()
    mouse.move(grid_bb["x"], y)
    mouse.up()
    slider.expect_value("0")

    slider.set("55")
    slider.expect_value("55")
    value_out.expect_value("Slider value: 55")

    # A value the slider cannot produce raises with the slider's actual values
    with pytest.raises(ValueError, match="Could not find value '55.5'"):
        slider.set("55.5")
