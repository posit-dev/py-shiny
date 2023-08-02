from __future__ import annotations

from typing import Optional

from conftest import ShinyAppProc
from controls import InputActionButton, InputSlider, OutputTextVerbatim
from playwright.sync_api import Page, expect


def test_slider_app(page: Page, local_app: ShinyAppProc) -> None:
    def check_case(
        id: str,
        *,
        value: tuple[Optional[str], Optional[str]] = (None, None),
        min: tuple[Optional[str], Optional[str]] = (None, None),
        max: tuple[Optional[str], Optional[str]] = (None, None),
    ):
        slider_times = InputSlider(page, f"{id}-times")
        btn_reset = InputActionButton(page, f"{id}-reset")
        out_txt = OutputTextVerbatim(page, f"{id}-txt")

        if value[0] is not None:
            out_txt.expect_value(value[0])
        if min[0] is not None:
            expect(slider_times.loc_irs.locator(".irs-min")).to_have_text(min[0])
        if max[0] is not None:
            expect(slider_times.loc_irs.locator(".irs-max")).to_have_text(max[0])

        btn_reset.loc.click()

        if value[1] is not None:
            out_txt.expect_value(value[1])
        if min[1] is not None:
            expect(slider_times.loc_irs.locator(".irs-min")).to_have_text(min[1])
        if max[1] is not None:
            expect(slider_times.loc_irs.locator(".irs-max")).to_have_text(max[1])

    page.goto(local_app.url)

    start_time = "2023-07-01 00:00:00"
    end_time = "2023-07-01 01:00:00"

    check_case("one", value=(start_time, end_time))
    check_case(
        "two",
        value=(f"{start_time} - {start_time}", f"{start_time} - {end_time}"),
    )
    check_case(
        "three",
        value=(f"{start_time} - {start_time}", f"{start_time} - {end_time}"),
    )
    check_case("four", min=("00:00:00", "23:00:00"))
    check_case("five", max=("01:00:00", "02:00:00"))
    check_case("six", min=("00:00:00", "23:00:00"), max=("01:00:00", "02:00:00"))
