# See https://github.com/microsoft/playwright-python/issues/1532
# pyright: reportUnknownMemberType=false

import re
from playwright.sync_api import Page, expect

from conftest import ShinyAppProc


def test_airmass(page: Page, airmass_app: ShinyAppProc):
    page.goto(airmass_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))

    img = plot.locator(">img")
    expect(img).to_have_attribute("src", re.compile(".{1000}"), timeout=30)
    # img.screenshot(path="airmass.png")

    page.reload()
    page.pause()
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
    page.pause()
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
