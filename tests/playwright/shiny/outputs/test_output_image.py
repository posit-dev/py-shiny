import re

from conftest import create_doc_example_core_fixture
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

app = create_doc_example_core_fixture("output_image")


def test_output_image_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    img = controller.OutputImage(page, "image")

    img.expect_inline(False)

    img.expect_img_src(re.compile(r"data:image/png;base64"))
    img.expect_img_height(None)
    img.expect_img_width("100px")
    img.expect_img_alt(None)
