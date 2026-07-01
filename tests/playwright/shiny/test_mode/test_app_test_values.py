import pytest
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

    # Whole-block expectations: subset (default) checks only the given keys,
    # ignoring other keys present in the block.
    app_values.expect_inputs({"name": "xyz"})
    app_values.expect_outputs({"double_txt": "doubled = 60"})
    app_values.expect_exports({"doubled": 60})

    # Whole-block "exact": the block's key set must equal the given keys. The
    # `export` block has exactly one key, so this holds.
    app_values.expect_exports({"doubled": 60}, match="exact")

    # "exact" fails fast when the block has extra keys (the `input` block has
    # both "name" and "n"), so a short timeout keeps the negative check quick.
    with pytest.raises(AssertionError):
        app_values.expect_inputs({"name": "xyz"}, match="exact", timeout=1)
