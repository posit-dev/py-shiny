from shiny import reactive, render
from shiny.express import input, ui
from shiny.testmode import export_test_values

ui.input_slider("n", "N", min=0, max=100, value=20)


@reactive.calc
def doubled() -> int:
    return input.n() * 2


@render.text
def txt() -> str:
    return f"n * 2 = {doubled()}"


# Surface the internal reactive value in the test-mode snapshot, under the
# snapshot's `export` block. Has no effect unless test mode is enabled
# (`SHINY_TESTMODE=1`), so the call can be left in production code. The
# `shiny.pytest` app fixtures enable test mode by default, so an end-to-end
# test can assert on it with the `shiny.playwright.controller.AppTestValues`
# controller. The expected value may be an exact value or a function of the
# actual value:
#
#     def is_even(value):
#         return value % 2 == 0
#
#     app_values = controller.AppTestValues(page)
#     app_values.expect_export("doubled", 40)
#     app_values.expect_export("doubled", is_even)
export_test_values(doubled=doubled)
