import os
import shutil
import subprocess
import tempfile

import pytest


def subprocess_create(app_template: str, mode: str = "core", package_name: str = ""):
    dest_dir = tempfile.mkdtemp()
    cmd = [
        "shiny",
        "create",
        "--template",
        app_template,
        "--mode",
        mode,
        "--directory",
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

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(cmd, check=True)

    shutil.rmtree(dest_dir)


@pytest.mark.parametrize("app_template", ["basic-app", "dashboard", "multi-page"])
def test_create_core(app_template: str):
    subprocess_create(app_template)


@pytest.mark.parametrize("app_template", ["basic-app"])
def test_create_express(app_template: str):
    subprocess_create(app_template, "express")


@pytest.mark.parametrize("app_template", ["js-input", "js-output", "js-react"])
def test_create_js(app_template: str):
    subprocess_create("js-input", package_name="my_component")
