from conftest import ShinyAppProc
from controls import InputCheckbox
from playwright.sync_api import Page, expect


def test_async_app(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    # Non-module version

    cb_show = InputCheckbox(page, "show")
    expect(cb_show.loc).to_be_visible()
    expect(cb_show.loc).not_to_be_checked()

    loc = page.locator("#cond_message")
    expect(loc).to_be_hidden()

    cb_show.loc.check()
    expect(loc).to_be_visible()
    expect(loc).to_contain_text("Lorem ipsum dolor sit amet")

    # Module version

    cb_mod_show = InputCheckbox(page, "mod-show")
    expect(cb_mod_show.loc).to_be_visible()
    expect(cb_mod_show.loc).not_to_be_checked()

    mod_loc = page.locator("#mod-cond_message")
    expect(mod_loc).to_be_hidden()

    cb_mod_show.loc.check()
    expect(mod_loc).to_be_visible()
    expect(mod_loc).to_contain_text("consectetur adipiscing elit")
