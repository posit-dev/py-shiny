# See https://github.com/microsoft/playwright-python/issues/1532
# pyright: reportUnknownMemberType=false

import re

from playwright.sync_api import Page, expect

from conftest import ShinyAppProc, create_example_fixture

airmass_app = create_example_fixture("airmass")
cpuinfo_app = create_example_fixture("cpuinfo")


def test_airmass(page: Page, airmass_app: ShinyAppProc):
    page.goto(airmass_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))

    img = plot.locator(">img")
    expect(img).to_have_attribute("src", re.compile(".{1000}"), timeout=30000)
    # img.screenshot(path="airmass.png")

    page.reload()
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))


def test_cpuinfo(page: Page, cpuinfo_app: ShinyAppProc):
    page.goto(cpuinfo_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
    img = plot.locator(">img")
    expect(img).to_have_attribute("src", re.compile(".{1000}"))
    # img.screenshot(path="cpuinfo.png")

    page.reload()
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
