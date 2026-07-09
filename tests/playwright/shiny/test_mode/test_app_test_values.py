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

    # Snapshot preprocessing: the live input keeps its real value while the
    # snapshot shows the scrubbed one; same for the timestamp output.
    controller.InputText(page, "secret").expect_value("hunter2")
    app_values.expect_input("secret", "<redacted>")
    app_values.expect_output("stamp", "time = <scrubbed>")

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

    # Predicates: any callable stands in for an expected value and is retried
    # until it returns truthy; a failing predicate raises with its name.
    def is_integer(value: object) -> bool:
        return isinstance(value, int)

    app_values.expect_export("doubled", is_integer)
    app_values.expect_inputs({"n": is_integer, "name": "xyz"})
    with pytest.raises(AssertionError, match="does not satisfy is_integer"):
        app_values.expect_input("name", is_integer, timeout=1)

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

    # "exact" also verifies values, not just the key set: the key matches but
    # the expected value is wrong, so this must fail.
    with pytest.raises(AssertionError):
        app_values.expect_exports({"doubled": 999}, match="exact", timeout=1)
