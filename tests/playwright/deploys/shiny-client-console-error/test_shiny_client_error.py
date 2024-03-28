from playwright.sync_api import Page
from utils.deploy_utils import create_deploys_app_url_fixture, skip_if_not_chrome

app_url = create_deploys_app_url_fixture("shiny_client_console_error")


@skip_if_not_chrome
def test_shiny_client_console_error(page: Page, app_url: str) -> None:
    page.goto(app_url)

    assert page.locator("#same_id").count() == 2
    shiny_error_message = page.query_selector("shiny-error-message")

    # show the client error message only for local apps
    if "http" in app_url:

        assert shiny_error_message is not None
        assert (
            shiny_error_message.get_attribute("message")
            == 'The following ID was repeated:\n- "same_id": 2 inputs'
        )
        assert page.get_by_role("button", name="Dismiss all").count() == 1
        assert page.get_by_role("button", name="Copy error to clipboard").count() == 1

    # for deployed apps to shinyapps.io or connect hide the client error message
    else:
        assert shiny_error_message is None
