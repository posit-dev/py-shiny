from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_input_selectize_update_options(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    single = controller.InputSelectize(page, "single")
    multiple = controller.InputSelectize(page, "multiple")

    single_out = controller.OutputCode(page, "single_out")
    multiple_out = controller.OutputCode(page, "multiple_out")

    # Confirm starting state
    single.expect_selected(["Option 1"])
    multiple.expect_selected(["Option 1", "Option 2"])

    def click_clear_button(x: controller.InputSelectize):
        x.loc.locator("..").locator("> div.plugin-clear_button > a.clear").click()

    # Can clear single selection via clear_button (after options have been updated)
    click_clear_button(single)
    single.expect_selected([""])
    single_out.expect_value("")

    # Can clear multiple selection via clear_button (after options have been updated)
    click_clear_button(multiple)
    multiple.expect_selected([])
    multiple_out.expect_value("")

    multiple.set(["Option 2", "Option 3"])

    # Can remove individual options
    def click_remove_button(x: controller.InputSelectize, option: str):
        x.loc.locator(
            f"+ div.plugin-remove_button > .has-options > .item[data-value='{option}'] > .remove:first-child"
        ).click()
        page.keyboard.press("Escape")

    click_remove_button(multiple, "Option 2")
    multiple.expect_selected(["Option 3"])
    multiple_out.expect_value("Option 3")

    click_remove_button(multiple, "Option 3")
    multiple.expect_selected([])
    multiple_out.expect_value("")
