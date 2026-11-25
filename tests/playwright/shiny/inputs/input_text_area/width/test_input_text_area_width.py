import pytest
from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@pytest.mark.parametrize(
    "id, container_width, textarea_width",
    [
        # `.shiny-input-container` is 300px; `.form-control` fills it, so `cols`
        # has no effect on the rendered width.
        ("default", "300px", "300px"),
        ("cols", "300px", "300px"),
        # The textarea fills the width given to the container.
        ("px", "600px", "600px"),
        ("px_cols", "450px", "450px"),
        ("percent", "400px", "400px"),
        # Without `width=`, a user rule on the textarea wins.
        ("user_css", "300px", "150px"),
        # With `width=`, the inline `width:100%` beats the user rule.
        ("user_css_px", "500px", "500px"),
    ],
)
def test_input_text_area_computed_width(
    page: Page,
    local_app: ShinyAppProc,
    id: str,
    container_width: str,
    textarea_width: str,
) -> None:
    page.goto(local_app.url)

    text_area = controller.InputTextArea(page, id)

    expect(text_area.loc_container).to_have_css("width", container_width)
    expect(text_area.loc).to_have_css("width", textarea_width)
