from __future__ import annotations

import os
import sys
from pathlib import Path

import click
import questionary

from ._main_utils import cli_action, cli_bold, cli_code, path_rel_wd


def add_test_file(
    *,
    app_file: Path | None,
    test_file: Path | None,
):
    if app_file is None:

        def path_exists(x: Path) -> bool | str:
            if not isinstance(x, (str, Path)):
                return False
            if Path(x).is_dir():
                return "Please provide a file path to your Shiny app"
            return Path(x).exists() or f"Shiny app file can not be found: {x}"

        app_file_val = questionary.path(
            "Enter the path to the app file:",
            default=path_rel_wd("app.py"),
            validate=path_exists,
        ).ask()
    else:
        app_file_val = app_file
    # User quit early
    if app_file_val is None:
        sys.exit(1)
    app_file = Path(app_file_val)

    if test_file is None:

        def path_does_not_exist(x: Path) -> bool | str:
            if not isinstance(x, (str, Path)):
                return False
            if Path(x).is_dir():
                return "Please provide a file path for your test file."
            if Path(x).exists():
                return "Test file already exists. Please provide a new file name."
            if not Path(x).name.startswith("test_"):
                return "Test file must start with 'test_'"
            return True

        test_file_val = questionary.path(
            "Enter the path to the test file:",
            default=path_rel_wd(
                os.path.relpath(app_file.parent / "tests" / "test_app.py", ".")
            ),
            validate=path_does_not_exist,
        ).ask()
    else:
        test_file_val = test_file

    # User quit early
    if test_file_val is None:
        sys.exit(1)
    test_file = Path(test_file_val)

    # Make sure app file exists
    if not app_file.exists():
        raise FileExistsError("App file does not exist: ", test_file)
    # Make sure output test file doesn't exist
    if test_file.exists():
        raise FileExistsError("Test file already exists: ", test_file)
    if not test_file.name.startswith("test_"):
        return "Test file must start with 'test_'"

    # if app path directory is the same as the test file directory, use `local_app`
    # otherwise, use `create_app_fixture`
    is_same_dir = app_file.parent == test_file.parent

    test_name = test_file.name.replace(".py", "")
    rel_path = os.path.relpath(app_file, test_file.parent)

    template = (
        f"""\
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def {test_name}(page: Page, local_app: ShinyAppProc):

    page.goto(local_app.url)
    # Add test code here
"""
        if is_same_dir
        else f"""\
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture("{rel_path}")


def {test_name}(page: Page, app: ShinyAppProc):

    page.goto(app.url)
    # Add test code here
"""
    )
    # Make sure test file directory exists
    test_file.parent.mkdir(parents=True, exist_ok=True)

    # Write template to test file
    test_file.write_text(template)

    # next steps
    click.echo()
    click.echo(cli_action(cli_bold("Next steps:")))
    click.echo(f"- Run {cli_code('pytest')} in your terminal to run all the tests")
