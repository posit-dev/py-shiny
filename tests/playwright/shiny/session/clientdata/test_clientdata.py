import re

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_output_image_kitchen(page: Page, local_app: ShinyAppProc) -> None:

    page.goto(local_app.url)

    text = controller.OutputTextVerbatim(page, "clientdatatext")

    # This doesn't cover all the clientdata values since we already have
    # tests that cover the frontend logic
    # https://github.com/rstudio/shinycoreci/blob/main/inst/apps/032-client-data-and-query-string/
    #
    # The important part is that we're testing here is that at least
    # some of these values are available in Python via session.clientdata
    text.expect.to_contain_text(re.compile(r"url_protocol\(\)\s+->\s+http"))
    text.expect.to_contain_text(re.compile(r"url_pathname\(\)\s+->\s+/"))
    text.expect.to_contain_text(
        re.compile(r"url_hostname\(\)\s+->\s+(localhost|127\.0\.0\.1)")
    )
    text.expect.to_contain_text(re.compile(r'output_hidden\("myplot"\)\s+->\s+False'))
    text.expect.to_contain_text(
        re.compile(r'output_bg_color\("myplot"\)\s+->\s+rgb\(255, 255, 255\)')
    )
    text.expect.to_contain_text(re.compile(r'output_hidden\("myplot"\)\s+->\s+False'))
