from __future__ import annotations

from conftest import ShinyAppProc
from controls import Accordion, InputActionButton, OutputTextVerbatim, Sidebar
from playwright.sync_api import Page


def test_module_support(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    not_modules = OutputTextVerbatim(page, "not_modules")
    not_modules.expect_value("[]")

    out1 = OutputTextVerbatim(page, "mod1-out")
    out2 = OutputTextVerbatim(page, "mod2-out")

    out1.expect_value(
        "sidebar: True\naccordion: ('Panel 1',)\npopover: False\ntooltip: False"
    )
    out2.expect_value(
        "sidebar: True\naccordion: ('Panel 1',)\npopover: False\ntooltip: False"
    )

    Sidebar(page, "mod2-sidebar").loc_handle.click()
    Accordion(page, "mod2-accordion").accordion_panel("Panel 2").loc_label.click()
    InputActionButton(page, "mod2-popover_btn").click()
    InputActionButton(page, "mod2-tooltip_btn").loc.hover()

    # Make sure the first module was not affected
    out1.expect_value(
        "sidebar: True\naccordion: ('Panel 1',)\npopover: False\ntooltip: False"
    )
    # Make sure the second module was affected
    out2.expect_value(
        "sidebar: False\naccordion: ('Panel 1', 'Panel 2')\npopover: True\ntooltip: True"
    )
