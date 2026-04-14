"""Playwright tests for session.destroy() cleaning up dangling reactivity."""

import re

from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_create_panel_renders_ui(page: Page, local_app: ShinyAppProc):
    """Clicking 'Create Panel' inserts a new panel module."""
    page.goto(local_app.url)

    create_btn = controller.InputActionButton(page, "create_panel")

    # No panels initially
    expect(page.locator("#panel_container")).to_be_empty()

    # Create first panel
    create_btn.click()

    # Panel title appears
    title = controller.OutputText(page, "panel_1-panel_title")
    title.expect_value("Panel 1")

    # Effect counter starts incrementing
    status = controller.OutputTextVerbatim(page, "panel_1-local_status")
    status.expect_value(re.compile(r"Effect has fired \d+ times"))

    # Dynamic input and calc output appear
    txt_input = controller.InputText(page, "panel_1-dynamic_txt")
    txt_input.expect_value("hello from panel 1")

    calc_output = controller.OutputText(page, "panel_1-calc_display")
    calc_output.expect_value("Derived: 'hello from panel 1'")


def test_remove_panel_cleans_up_dom(page: Page, local_app: ShinyAppProc):
    """Clicking 'Remove this panel' removes the panel from the DOM."""
    page.goto(local_app.url)

    create_btn = controller.InputActionButton(page, "create_panel")

    # Create a panel
    create_btn.click()
    title = controller.OutputText(page, "panel_1-panel_title")
    title.expect_value("Panel 1")

    # Remove the panel
    remove_btn = controller.InputActionButton(page, "panel_1-remove")
    remove_btn.click()

    # Panel container div is removed from DOM
    expect(page.locator("#panel_1-panel_ui_container")).to_have_count(0)


def test_destroy_stops_effect_counter(page: Page, local_app: ShinyAppProc):
    """After destroy, the effect counter stops incrementing in the status monitor."""
    page.goto(local_app.url)

    create_btn = controller.InputActionButton(page, "create_panel")

    # Create and wait for the panel to start running
    create_btn.click()
    status = controller.OutputTextVerbatim(page, "panel_1-local_status")
    status.expect_value(re.compile(r"Effect has fired \d+ times"))

    # Wait for the effect to fire a few times so we can capture the count
    page.wait_for_timeout(2000)

    # Remove the panel (triggers destroy)
    remove_btn = controller.InputActionButton(page, "panel_1-remove")
    remove_btn.click()

    # Wait for destroy to complete
    expect(page.locator("#panel_1-panel_ui_container")).to_have_count(0)

    # The status monitor should show [DESTROYED] for panel_1
    status_panel = page.locator("#status_panel")
    expect(status_panel).to_contain_text("panel_1 [DESTROYED]")

    # Capture the effect count after destroy
    effect_count_el = status_panel.locator(
        "xpath=.//div[contains(., 'panel_1')]//td[contains(@class, 'fw-bold')]"
    ).first
    frozen_count = int(effect_count_el.inner_text())

    # Wait and verify the count doesn't increase (effect was destroyed)
    page.wait_for_timeout(3000)
    new_count = int(effect_count_el.inner_text())
    assert new_count == frozen_count, (
        f"Effect counter should be frozen after destroy, "
        f"but went from {frozen_count} to {new_count}"
    )


def test_multiple_panels_independent_destroy(page: Page, local_app: ShinyAppProc):
    """Destroying one panel does not affect other active panels."""
    page.goto(local_app.url)

    create_btn = controller.InputActionButton(page, "create_panel")

    # Create two panels
    create_btn.click()
    title1 = controller.OutputText(page, "panel_1-panel_title")
    title1.expect_value("Panel 1")

    create_btn.click()
    title2 = controller.OutputText(page, "panel_2-panel_title")
    title2.expect_value("Panel 2")

    # Both panels are running
    status1 = controller.OutputTextVerbatim(page, "panel_1-local_status")
    status1.expect_value(re.compile(r"Effect has fired \d+ times"))
    status2 = controller.OutputTextVerbatim(page, "panel_2-local_status")
    status2.expect_value(re.compile(r"Effect has fired \d+ times"))

    # Remove panel 1
    remove_btn1 = controller.InputActionButton(page, "panel_1-remove")
    remove_btn1.click()
    expect(page.locator("#panel_1-panel_ui_container")).to_have_count(0)

    # Panel 2 is still alive and updating
    page.wait_for_timeout(1500)
    # Verify panel 2's effect counter is still going
    status2_text = page.locator("#panel_2-local_status").inner_text()
    match = re.search(r"(\d+)", status2_text)
    assert match is not None
    count_before = int(match.group(1))

    page.wait_for_timeout(2000)
    status2_text = page.locator("#panel_2-local_status").inner_text()
    match = re.search(r"(\d+)", status2_text)
    assert match is not None
    count_after = int(match.group(1))
    assert count_after > count_before, (
        f"Panel 2's effect should still be running after panel 1 destroy, "
        f"but count went from {count_before} to {count_after}"
    )


def test_panel_recreation_after_destroy(page: Page, local_app: ShinyAppProc):
    """A new panel can be created after a previous one was destroyed."""
    page.goto(local_app.url)

    create_btn = controller.InputActionButton(page, "create_panel")

    # Create and remove panel 1
    create_btn.click()
    title1 = controller.OutputText(page, "panel_1-panel_title")
    title1.expect_value("Panel 1")

    remove_btn = controller.InputActionButton(page, "panel_1-remove")
    remove_btn.click()
    expect(page.locator("#panel_1-panel_ui_container")).to_have_count(0)

    # Create panel 2 — it should work normally
    create_btn.click()
    title2 = controller.OutputText(page, "panel_2-panel_title")
    title2.expect_value("Panel 2")

    status2 = controller.OutputTextVerbatim(page, "panel_2-local_status")
    status2.expect_value(re.compile(r"Effect has fired \d+ times"))

    calc2 = controller.OutputText(page, "panel_2-calc_display")
    calc2.expect_value("Derived: 'hello from panel 2'")


def test_input_responds_after_creation(page: Page, local_app: ShinyAppProc):
    """Typing in the dynamic input updates the calc output."""
    page.goto(local_app.url)

    create_btn = controller.InputActionButton(page, "create_panel")
    create_btn.click()

    txt_input = controller.InputText(page, "panel_1-dynamic_txt")
    calc_output = controller.OutputText(page, "panel_1-calc_display")

    # Default value
    calc_output.expect_value("Derived: 'hello from panel 1'")

    # Type new value
    txt_input.set("testing destroy")
    calc_output.expect_value("Derived: 'testing destroy'")
