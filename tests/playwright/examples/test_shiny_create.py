import os
import subprocess
import tempfile

import pytest
from example_apps import get_apps, reruns, validate_example
from playwright.sync_api import Page


def subprocess_create(
    app_template: str,
    dest_dir: str = "",
    *,
    mode: str = "core",
    package_name: str = "",
):
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


@pytest.mark.examples
@pytest.mark.flaky(reruns=reruns, reruns_delay=1)
@pytest.mark.parametrize("ex_app_path", get_apps("shiny/templates/app-templates"))
def test_template_examples(page: Page, ex_app_path: str) -> None:
    validate_example(page, ex_app_path)


@pytest.mark.examples
@pytest.mark.flaky(reruns=reruns, reruns_delay=1)
@pytest.mark.parametrize("app_template", ["basic-app", "dashboard", "multi-page"])
def test_create_core(app_template: str, page: Page):
    with tempfile.TemporaryDirectory("example_apps") as tmpdir:
        subprocess_create(app_template, dest_dir=tmpdir)
        validate_example(page, f"{tmpdir}/app.py")


@pytest.mark.examples
@pytest.mark.flaky(reruns=reruns, reruns_delay=1)
@pytest.mark.parametrize("app_template", ["basic-app"])
def test_create_express(app_template: str, page: Page):
    with tempfile.TemporaryDirectory("example_apps") as tmpdir:
        subprocess_create(app_template, dest_dir=tmpdir, mode="express")
        validate_example(page, f"{tmpdir}/app.py")


@pytest.mark.examples
@pytest.mark.flaky(reruns=reruns, reruns_delay=1)
@pytest.mark.parametrize("app_template", ["js-input", "js-output", "js-react"])
def test_create_js(app_template: str):
    with tempfile.TemporaryDirectory("example_apps") as tmpdir:
        subprocess_create(app_template, dest_dir=tmpdir, package_name="my_component")
        # TODO-Karan: Add test to validate once flag to install packages is implemented
