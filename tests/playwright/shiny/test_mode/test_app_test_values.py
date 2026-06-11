from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_app_test_values(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Ensure the app is loaded/bound before reading the snapshot.
    controller.InputText(page, "name").expect_value("abc")

    app_values = controller.AppTestValues(page)

    # Per-key expectations (auto-retry across async settle).
    app_values.expect_input("name", "abc")
    app_values.expect_output("double_txt", "doubled = 40")
    app_values.expect_export("doubled", 40)

    # Raw snapshot shape.
    data = app_values.get()
    assert set(data.keys()) == {"input", "output", "export"}
    assert data["export"]["doubled"] == 40

    # Change inputs; the snapshot reflects the new values (auto-retry).
    controller.InputText(page, "name").set("xyz")
    app_values.expect_input("name", "xyz")

    controller.InputSlider(page, "n").set("30")
    app_values.expect_output("double_txt", "doubled = 60")
    app_values.expect_export("doubled", 60)
