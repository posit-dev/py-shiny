import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

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


def choice_from_dict(choice_dict: Dict[str, str]) -> List[Choice]:
    return [Choice(title=key, value=value) for key, value in choice_dict.items()]


def template_query(question_state: Optional[str] = None, mode: Optional[str] = None):
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
        js_component_questions()
        return
    elif template in package_template_choices.values():
        js_component_questions(template)
    else:
        app_template_questions(template, mode)


def app_template_questions(template: str, mode: Optional[str] = None):
    # Not all apps will be implemented in both express and classic so we can
    # avoid the questions if it's a classic only app.
    template_dir = Path(__file__).parent / "templates/app-templates" / template
    template_files = [file.name for file in template_dir.iterdir() if file.is_file()]
    express_available = "app-express.py" in template_files

    if mode == "express" and not express_available:
        raise Exception("Express mode not available for that template.")

    if mode is None and express_available:
        mode = questionary.select(
            "Would you like to use express or classic mode?",
            [
                Choice("Classic", "classic"),
                Choice("Express", "express"),
                back_choice,
                cancel_choice,
            ],
        ).ask()

        if mode is None or mode == "cancel":
            sys.exit(1)
        if mode == "back":
            template_query()
            return

    appdir = questionary.path(
        "Enter destination directory:",
        default=build_path_string(),
        only_directories=True,
    ).ask()

    if appdir is None:
        sys.exit(1)

    app_dir = copy_template_files(
        appdir,
        template,
        template_subdir="app-templates",
        mode=mode,
        express_available=express_available,
    )
    print(f"Created Shiny app at {app_dir}")
    print(f"Next steps open and edit the app file: {app_dir}/app.py")


def js_component_questions(component_type: Optional[str] = None):
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

    # As what the user wants the name of their component to be
    component_name = questionary.text(
        "What do you want to name your component?",
        instruction="Name must be dash-delimited and all lowercase. E.g. 'my-component-name'",
        validate=ComponentNameValidator,
    ).ask()

    if component_name is None:
        sys.exit(1)

    appdir = questionary.path(
        "Enter destination directory:",
        default=build_path_string(component_name),
        only_directories=True,
    ).ask()

    if appdir is None:
        sys.exit(1)

    app_dir = copy_template_files(
        appdir,
        component_type,
        template_subdir="package-templates",
        express_available=False,
        mode=None,
    )

    # Print messsage saying we're building the component
    print(f"Setting up {component_name} component package...")
    update_component_name_in_template(app_dir, component_name)

    print("\nNext steps:")
    print(f"- Run `cd {app_dir}` to change into the new directory")
    print("- Run `npm install` to install dependencies")
    print("- Run `npm run build` to build the component")
    print("- Install package locally with `pip install -e .`")
    print("- Open and run the example app in the `example-app` directory")


def build_path_string(*path: str):
    """
    Build a path string that is valid for the current OS
    """
    return os.path.join(".", *path)


def copy_template_files(
    dest: str,
    template: str,
    template_subdir: str,
    express_available: bool,
    mode: Optional[str] = None,
):
    if dest == ".":
        dest = build_path_string(template)

    app_dir = Path(dest)
    template_dir = Path(__file__).parent / "templates" / template_subdir / template

    duplicate_files = [
        file.name for file in template_dir.iterdir() if (app_dir / file.name).exists()
    ]

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
            shutil.copytree(item, app_dir / item.name)

    def rename_unlink(file_to_rename: str, file_to_delete: str, dir: Path = app_dir):
        (dir / file_to_rename).rename(dir / "app.py")
        (dir / file_to_delete).unlink()

    if express_available:
        if mode == "express":
            rename_unlink("app-express.py", "app-classic.py")
        if mode == "classic":
            rename_unlink("app-classic.py", "app-express.py")
    else:
        (app_dir / "app-classic.py").rename(app_dir / "app.py")

    return app_dir
