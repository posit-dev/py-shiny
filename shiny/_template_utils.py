from __future__ import annotations

import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, cast
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

import questionary
from questionary import Choice

from ._custom_component_template_questions import (
    ComponentNameValidator,
    update_component_name_in_template,
)

# The choices are specified in _main because they populate the
# CLI flag options.
from ._main import app_template_choices, package_template_choices

styles_for_questions = questionary.Style(
    [
        (
            "secondary",
            "italic",
        ),
    ]
)
# Prebuild some common choices
cancel_choice: Choice = Choice(title=[("class:secondary", "[Cancel]")], value="cancel")
back_choice: Choice = Choice(title=[("class:secondary", "← Back")], value="back")


def choice_from_dict(choice_dict: dict[str, str]) -> list[Choice]:
    return [Choice(title=key, value=value) for key, value in choice_dict.items()]


def template_query(
    question_state: Optional[str] = None,
    mode: Optional[str] = None,
    dest_dir: Optional[Path] = None,
    package_name: Optional[str] = None,
):
    """
    This will initiate a CLI query which will ask the user which template they would like.
    If called without arguments this function will start from the top level and ask which
    type of template the user would like.

    You can also specify a question state to return to another level. For example if you
    were at level 5 of a question chain and wanted to return to level 4.
    This is not that useful currently because we only have two levels of questions.


    :param question_state: The question state you would like to return to. Currently, the options are:
        "cancel": Cancel the operation and exit.
        "js-component": Start the questions for creating a custom JavaScript component.
    """

    if question_state is None:
        template = questionary.select(
            "Which template would you like to use?:",
            choices=[*choice_from_dict(app_template_choices), cancel_choice],
            style=styles_for_questions,
        ).ask()
    else:
        template = question_state

    # Define the control flow for the top level menu
    if template is None or template == "cancel":
        sys.exit(1)
    elif template == "js-component":
        js_component_questions(dest_dir=dest_dir, package_name=package_name)
        return
    elif template in package_template_choices.values():
        js_component_questions(template, dest_dir=dest_dir, package_name=package_name)
    else:
        app_template_questions(template, mode, dest_dir=dest_dir)


def download_and_extract_zip(url: str, temp_dir: Path):
    try:
        response = urlopen(url)
        data = cast(bytes, response.read())
    except URLError as e:
        # Note that HTTPError is a subclass of URLError
        e.msg += f" for url: {url}"  # pyright: ignore
        raise e

    zip_file_path = temp_dir / "repo.zip"
    zip_file_path.write_bytes(data)
    with zipfile.ZipFile(zip_file_path, "r") as zip_file:
        zip_file.extractall(temp_dir)


def use_git_template(
    url: str, mode: Optional[str] = None, dest_dir: Optional[Path] = None
):
    # Github requires that we download the whole repository, so we need to
    # download and unzip the repo, then navigate to the subdirectory.

    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    repo_owner, repo_name, _, branch_name = path_parts[:4]
    subdirectory = "/".join(path_parts[4:])

    zip_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/{branch_name}.zip"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        download_and_extract_zip(zip_url, temp_dir)

        template_dir = os.path.join(
            temp_dir, f"{repo_name}-{branch_name}", subdirectory
        )

        if not os.path.exists(template_dir):
            raise Exception(f"Template directory '{template_dir}' does not exist")

        directory = repo_name + "-" + branch_name
        path = temp_dir / directory / subdirectory
        return app_template_questions(mode=mode, template_dir=path, dest_dir=dest_dir)


def app_template_questions(
    template: Optional[str] = None,
    mode: Optional[str] = None,
    template_dir: Optional[Path] = None,
    dest_dir: Optional[Path] = None,
):
    if template_dir is None:
        if template is None:
            raise ValueError("You must provide either template or template_dir")
        template_dir = Path(__file__).parent / "templates/app-templates" / template

    # Not all apps will be implemented in both express and core so we can
    # avoid the questions if it's a core only app.
    template_files = [file.name for file in template_dir.iterdir() if file.is_file()]
    express_available = "app-express.py" in template_files

    if mode == "express" and not express_available:
        raise Exception("Express mode not available for that template.")

    if mode is None and express_available:
        mode = questionary.select(
            "Would you like to use Shiny Express?",
            [
                Choice("Yes", "express"),
                Choice("No", "core"),
                back_choice,
                cancel_choice,
            ],
        ).ask()

        if mode is None or mode == "cancel":
            sys.exit(1)
        if mode == "back":
            template_query()
            return

    dest_dir = directory_prompt(template_dir, dest_dir)

    app_dir = copy_template_files(
        dest_dir,
        template_dir=template_dir,
        express_available=express_available,
        mode=mode,
    )

    print(f"Created Shiny app at {app_dir}")
    print(f"Next steps open and edit the app file: {app_dir}/app.py")
    print("You may need to install packages with: `pip install -r requirements.txt`")


def js_component_questions(
    component_type: Optional[str] = None,
    dest_dir: Optional[Path] = None,
    package_name: Optional[str] = None,
):
    """
    Hand question branch for the custom js templates. This should handle the entire rest
    of the question flow and is responsible for placing files etc. Currently it repeats
    a lot of logic from the default flow but as the custom templates get more
    complicated the logic will diverge
    """
    if component_type is None:
        component_type = questionary.select(
            "What kind of component do you want to build?:",
            choices=[
                *choice_from_dict(package_template_choices),
                back_choice,
                cancel_choice,
            ],
            style=styles_for_questions,
        ).ask()

    if component_type == "back":
        template_query()
        return

    if component_type is None or component_type == "cancel":
        sys.exit(1)

    # Ask what the user wants the name of their component to be
    if package_name is None:
        package_name = questionary.text(
            "What do you want to name your component?",
            instruction="Name must be dash-delimited and all lowercase. E.g. 'my-component-name'",
            validate=ComponentNameValidator,
        ).ask()

        if package_name is None:
            sys.exit(1)

    template_dir = (
        Path(__file__).parent / "templates/package-templates" / component_type
    )

    dest_dir = directory_prompt(template_dir, dest_dir)

    app_dir = copy_template_files(
        dest_dir,
        template_dir=template_dir,
        express_available=False,
        mode=None,
    )

    # Print messsage saying we're building the component
    print(f"Setting up {package_name} component package...")
    update_component_name_in_template(app_dir, package_name)

    print("\nNext steps:")
    print(f"- Run `cd {app_dir}` to change into the new directory")
    print("- Run `npm install` to install dependencies")
    print("- Run `npm run build` to build the component")
    print("- Install package locally with `pip install -e .`")
    print("- Open and run the example app in the `example-app` directory")


def directory_prompt(
    template_dir: Path, dest_dir: Optional[Path | str | None] = None
) -> Path:
    if dest_dir is not None:
        return Path(dest_dir)

    app_dir = questionary.path(
        "Enter destination directory:",
        default=build_path_string(""),
        only_directories=True,
    ).ask()

    if app_dir is None:
        sys.exit(1)

    if app_dir == ".":
        app_dir = build_path_string(template_dir.name)

    return Path(app_dir)


def build_path_string(*path: str):
    """
    Build a path string that is valid for the current OS
    """
    return os.path.join(".", *path)


def copy_template_files(
    app_dir: Path,
    template_dir: Path,
    express_available: bool,
    mode: Optional[str] = None,
):
    files_to_check = [file.name for file in template_dir.iterdir()]

    if "__pycache__" in files_to_check:
        files_to_check.remove("__pycache__")

    files_to_check.append("app.py")

    duplicate_files = [file for file in files_to_check if (app_dir / file).exists()]

    if any(duplicate_files):
        err_files = ", ".join(['"' + file + '"' for file in duplicate_files])
        print(
            f"Error: Can't create new files because the following files already exist in the destination directory: {err_files}"
        )
        sys.exit(1)

    if not app_dir.exists():
        app_dir.mkdir()

    for item in template_dir.iterdir():
        if item.is_file():
            shutil.copy(item, app_dir / item.name)
        else:
            if item.name != "__pycache__":
                shutil.copytree(item, app_dir / item.name)

    def rename_unlink(file_to_rename: str, file_to_delete: str, dir: Path = app_dir):
        (dir / file_to_rename).rename(dir / "app.py")
        (dir / file_to_delete).unlink()

    if express_available:
        if mode == "express":
            rename_unlink("app-express.py", "app-core.py")
        if mode == "core":
            rename_unlink("app-core.py", "app-express.py")
    if (app_dir / "app-core.py").exists():
        (app_dir / "app-core.py").rename(app_dir / "app.py")

    return app_dir
