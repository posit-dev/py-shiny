import os
import shutil
import subprocess
import tempfile

import pytest


def subprocess_create(app_template: str, mode: str):
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
    ]

    subprocess.run(cmd)
    assert os.path.isdir(dest_dir)
    assert os.path.isfile(f"{dest_dir}/app.py")

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(cmd, check=True)

    shutil.rmtree(dest_dir)


@pytest.mark.parametrize("app_template", ["basic-app", "dashboard", "multi-page"])
def test_create_core(app_template: str):
    subprocess_create(app_template, "core")


@pytest.mark.parametrize("app_template", ["basic-app"])
def test_create_express(app_template: str):
    subprocess_create(app_template, "express")
