from playwright.sync_api import Page, expect

from shiny.run import ShinyAppProc


def _root_variable(page: Page, name: str) -> str:
    return page.locator("html").evaluate(
        "(element, property) => getComputedStyle(element)"
        ".getPropertyValue(property).trim()",
        name,
    )


def test_default_document_uses_light_brand_colors(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    html = page.locator("html")
    body = page.locator("body")
    primary = page.locator("#primary")
    primary_bg = page.locator("#primary-bg")
    success_bg = page.locator("#success-bg")
    warning_bg = page.locator("#warning-bg")
    link = page.locator("#link")
    heading = page.locator("#heading")
    inline_code = page.locator("#inline-code")
    block_code = page.locator("#block-code")

    expect(html).not_to_have_attribute("data-bs-theme", "light")
    expect(body).to_have_css("color", "rgb(17, 17, 17)")
    expect(body).to_have_css("background-color", "rgb(255, 255, 255)")
    expect(primary).to_have_css("background-color", "rgb(204, 0, 0)")
    expect(primary_bg).to_have_css("background-color", "rgb(204, 0, 0)")
    expect(success_bg).to_have_css("background-color", "rgb(136, 68, 204)")
    expect(warning_bg).to_have_css("background-color", "rgb(255, 193, 7)")
    expect(link).to_have_css("color", "rgb(0, 85, 170)")
    expect(link).to_have_css("background-color", "rgb(238, 246, 255)")
    expect(heading).to_have_css("color", "rgb(17, 17, 17)")
    expect(inline_code).to_have_css("color", "rgb(17, 17, 17)")
    expect(inline_code).to_have_css("background-color", "rgb(241, 245, 250)")
    expect(block_code).to_have_css("color", "rgb(17, 17, 17)")
    expect(block_code).to_have_css("background-color", "rgb(248, 249, 250)")
    assert _root_variable(page, "--acme-primary-rgb") == "204,0,0"


def test_explicit_dark_mode_uses_dark_and_scalar_brand_colors(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    html = page.locator("html")
    html.evaluate("element => element.setAttribute('data-bs-theme', 'dark')")

    body = page.locator("body")
    primary = page.locator("#primary")
    primary_bg = page.locator("#primary-bg")
    success_bg = page.locator("#success-bg")
    warning_bg = page.locator("#warning-bg")
    link = page.locator("#link")
    heading = page.locator("#heading")
    inline_code = page.locator("#inline-code")
    block_code = page.locator("#block-code")

    expect(body).to_have_css("color", "rgb(238, 238, 238)")
    expect(body).to_have_css("background-color", "rgb(34, 34, 34)")
    expect(primary).to_have_css("background-color", "rgb(0, 170, 68)")
    expect(primary_bg).to_have_css("background-color", "rgb(0, 170, 68)")
    expect(success_bg).to_have_css("background-color", "rgb(136, 68, 204)")
    expect(warning_bg).to_have_css("background-color", "rgb(255, 136, 0)")
    expect(link).to_have_css("color", "rgb(153, 204, 255)")
    expect(link).to_have_css("background-color", "rgb(32, 48, 64)")
    expect(heading).to_have_css("color", "rgb(238, 238, 238)")
    expect(inline_code).to_have_css("color", "rgb(238, 238, 238)")
    expect(inline_code).to_have_css("background-color", "rgb(38, 55, 70)")
    expect(block_code).to_have_css("color", "rgb(238, 238, 238)")
    expect(block_code).to_have_css("background-color", "rgb(31, 41, 51)")
    assert _root_variable(page, "--acme-primary-rgb") == "0,170,68"


def test_runtime_mode_switch_updates_derived_components(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.goto(local_app.url)

    html = page.locator("html")
    body = page.locator("body")
    primary = page.locator("#primary")
    primary_bg = page.locator("#primary-bg")

    expect(primary).to_have_css("background-color", "rgb(204, 0, 0)")

    html.evaluate("element => element.setAttribute('data-bs-theme', 'dark')")
    expect(body).to_have_css("color", "rgb(238, 238, 238)")
    expect(primary).to_have_css("background-color", "rgb(0, 170, 68)")
    expect(primary_bg).to_have_css("background-color", "rgb(0, 170, 68)")

    html.evaluate("element => element.setAttribute('data-bs-theme', 'light')")
    expect(body).to_have_css("color", "rgb(17, 17, 17)")
    expect(primary).to_have_css("background-color", "rgb(204, 0, 0)")
    expect(primary_bg).to_have_css("background-color", "rgb(204, 0, 0)")
