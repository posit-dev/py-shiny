import re
from typing import Union

import pytest
from playwright.sync_api import Page, expect

from conftest import ShinyAppProc, run_shiny_app
from pathlib import PurePath


def test_cpuinfo(page: Page, airmass_app: ShinyAppProc):
    page.goto(airmass_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
    img = plot.locator(">img")
    expect(img).to_have_attribute("src", re.compile(".{1000}"))
    # img.screenshot(path="sshot.png")

    page.reload()
    page.pause()
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))


def test_cpuinfo2(page: Page, cpuinfo_app: ShinyAppProc):
    page.goto(cpuinfo_app.url)
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
    img = plot.locator(">img")
    expect(img).to_have_attribute("src", re.compile(".{1000}"))
    # img.screenshot(path="sshot.png")

    page.reload()
    page.pause()
    plot = page.locator("#plot")
    expect(plot).to_have_class(re.compile(r"\bshiny-bound-output\b"))
