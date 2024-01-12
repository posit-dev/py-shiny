import os
import subprocess
import tempfile

import pytest
from playwright.sync_api import Page

from tests.playwright.examples.example_apps import validate_example


def subprocess_create(app_template: str, mode: str = "core", package_name: str = ""):
    dest_dir = tempfile.TemporaryDirectory("example_apps").name
    cmd = [
        "shiny",
        "create",
        "--template",
        app_template,
        "--mode",
        mode,
        "--dir",
        dest_dir,
        "--package-name",
        package_name,
    ]

    subprocess.run(cmd)
    assert os.path.isdir(dest_dir)

    # Package templates don't have a top-level app.py file
    if package_name == "":
        assert os.path.isfile(f"{dest_dir}/app.py")
    else:
        assert os.path.isfile(f"{dest_dir}/pyproject.toml")

    print("\nCheck for duplicate files")
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(cmd, check=True)

    return dest_dir


@pytest.mark.parametrize("app_template", ["basic-app", "dashboard", "multi-page"])
def test_create_core(app_template: str, page: Page):
    dir = subprocess_create(app_template)
    validate_example(page, f"{dir}/app.py")


@pytest.mark.parametrize("app_template", ["basic-app"])
def test_create_express(app_template: str, page: Page):
    dir = subprocess_create(app_template, "express")
    validate_example(page, f"{dir}/app.py")


@pytest.mark.parametrize("app_template", ["js-input", "js-output", "js-react"])
def test_create_js(app_template: str):
    subprocess_create("js-input", package_name="my_component")
