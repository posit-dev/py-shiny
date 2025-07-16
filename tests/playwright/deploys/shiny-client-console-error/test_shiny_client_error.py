import re

import pytest
from playwright.sync_api import Page, expect
from utils.deploy_utils import (
    local_deploys_app_url_fixture,
    reruns,
    reruns_delay,
    skip_if_not_chrome,
)

app_url = local_deploys_app_url_fixture("shiny_client_console_error")


@skip_if_not_chrome
@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
def test_shiny_client_console_error(page: Page, app_url: str) -> None:
    page.goto(app_url)

    assert page.locator("#same_id").count() == 2
    shiny_error_message = page.locator("shiny-error-message")

    # show the client error message only for local apps
    if "127.0.0.1" in app_url:

        expect(shiny_error_message).not_to_have_count(0)
        expect(shiny_error_message).to_have_attribute(
            "message", re.compile(r'"same_id": 2 inputs')
        )
        expect(page.get_by_role("button", name="Dismiss all")).to_have_count(1)
        expect(
            page.get_by_role("button", name="Copy error to clipboard")
        ).to_have_count(1)

    # for deployed apps to shinyapps.io or connect hide the client error message
    else:
        expect(shiny_error_message).to_have_count(0)
