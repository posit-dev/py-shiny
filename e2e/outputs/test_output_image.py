import re

from conftest import ShinyAppProc, create_doc_example_fixture
from controls import OutputImage
from playwright.sync_api import Page

app = create_doc_example_fixture("output_image")


def test_output_image_kitchen(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    img = OutputImage(page, "image")

    img.expect_inline(inline=False)

    img.expect_img_src(re.compile(r"data:image/png;base64"))
    img.expect_img_height(None)
    img.expect_img_width("100px")
    img.expect_img_alt(None)
