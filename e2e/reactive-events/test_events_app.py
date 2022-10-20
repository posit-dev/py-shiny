from conftest import ShinyAppProc, create_example_fixture
from playwright.sync_api import Page
from controls import ActionButton, UIOutput, NavControls

event_app = create_example_fixture("event")


def test_event(page: Page, event_app: ShinyAppProc):
    page.goto(event_app.url)

    # sync
    click_me_sync = ActionButton(page, "btn")
    click_me_sync.loc.click()

    output1 = UIOutput(page, "btn_value")
    assert output1.get_text() == "1"
    # TODO: Check the messages in the python console
    # @effect() event:  1
    # @calc() event:    1

    click_me_sync.loc.click()
    assert output1.get_text() == "2"

    # TODO: Check the messages in the python console
    # @effect() event:  2
    # @calc() event:    2

    # async
    nav_async = NavControls(page, "nav-tabs", "Async")
    nav_async.loc.click()

    click_me_async = ActionButton(page, "btn_async")
    click_me_async.loc.click()
    output2 = UIOutput(page, "btn_async_value")
    assert output2.get_text() == "1"
    # TODO: Check the messages in the python console
    # async @effect() event:  1
    # async @calc() event:    1

    click_me_async.loc.click()
    assert output2.get_text() == "2"

    # TODO: Check the messages in the python console
    # async @effect() event:  2
    # async @calc() event:    2







    # plot = page.locator("#plot")
    # expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
