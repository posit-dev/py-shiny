import re

from playwright.sync_api import Page, expect

from shiny.run import ShinyAppProc


def test_output_size_updates(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    size_info = page.locator("#size_info")

    expect(size_info).to_contain_text(re.compile(r'"width":\s*240(\.0+)?'))
    expect(size_info).to_contain_text(re.compile(r'"height":\s*120(\.0+)?'))

    page.evaluate(
        """
        () => {
            window.__resizeEvents = 0;
            window.addEventListener("resize", () => {
                window.__resizeEvents += 1;
            });
        }
        """
    )

    page.get_by_role("button", name="Toggle size").click()

    expect(size_info).to_contain_text(re.compile(r'"width":\s*360(\.0+)?'))
    expect(size_info).to_contain_text(re.compile(r'"height":\s*180(\.0+)?'))
    assert page.evaluate("() => window.__resizeEvents") == 0


def test_output_hidden_state_updates(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    hidden_info = page.locator("#hidden_info")

    expect(hidden_info).to_contain_text('"hidden": false')

    page.get_by_role("button", name="Toggle visibility").click()
    expect(hidden_info).to_contain_text('"hidden": true')

    page.get_by_role("button", name="Toggle visibility").click()
    expect(hidden_info).to_contain_text('"hidden": false')


def test_output_theme_updates(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    theme_info = page.locator("#theme_info")

    expect(theme_info).to_contain_text('"bg": "rgb(250, 250, 248)"')
    expect(theme_info).to_contain_text('"fg": "rgb(34, 39, 46)"')
    expect(theme_info).to_contain_text('"accent": "rgb(12, 110, 253)"')
    expect(theme_info).to_contain_text('"families": ["Courier New", "monospace"]')
    expect(theme_info).to_contain_text('"size": "18px"')

    page.get_by_role("button", name="Toggle theme").click()

    expect(theme_info).to_contain_text('"bg": "rgb(23, 27, 36)"')
    expect(theme_info).to_contain_text('"fg": "rgb(238, 241, 245)"')
    expect(theme_info).to_contain_text('"accent": "rgb(255, 138, 76)"')
    expect(theme_info).to_contain_text('"families": ["Times New Roman", "serif"]')
    expect(theme_info).to_contain_text('"size": "20px"')


def test_output_hidden_state_updates_via_tabs(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    nav_hidden_info = page.locator("#nav_hidden_info")

    expect(nav_hidden_info).to_contain_text('"hidden": false')

    page.get_by_role("tab", name="Other").click()
    expect(nav_hidden_info).to_contain_text('"hidden": true')

    page.get_by_role("tab", name="Observed").click()
    expect(nav_hidden_info).to_contain_text('"hidden": false')


def test_output_unbind_rebind_smoke(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    dynamic_info = page.locator("#dynamic_info")

    expect(dynamic_info).to_contain_text('"mounted": true')
    expect(dynamic_info).to_contain_text(re.compile(r'"width":\s*220(\.0+)?'))
    expect(dynamic_info).to_contain_text('"hidden": false')

    page.get_by_role("button", name="Toggle dynamic mount").click()
    expect(dynamic_info).to_contain_text('"mounted": false')
    expect(page.locator("#dynamic_probe")).not_to_be_attached()

    page.get_by_role("button", name="Toggle dynamic mount").click()
    expect(dynamic_info).to_contain_text('"mounted": true')
    expect(dynamic_info).to_contain_text(re.compile(r'"width":\s*220(\.0+)?'))
    expect(dynamic_info).to_contain_text('"hidden": false')

    page.get_by_role("button", name="Toggle dynamic size").click()
    expect(dynamic_info).to_contain_text(re.compile(r'"width":\s*320(\.0+)?'))
