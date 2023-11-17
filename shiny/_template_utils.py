import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import questionary
from questionary import Choice

from ._custom_component_template_questions import (
    install_js_dependencies,
    isValidName,
    updateComponentNameInTemplate,
)


def template_query(question_state: Optional[str] = None):
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
            choices=choicesArray(
                [
                    ("Basic App", "basic-app"),
                    ("Express app", "express"),
                    ("Dashboard", "dashboard"),
                    ("Multi-page app with modules", "multi-page"),
                    ("Custom JavaScript Component", "js-component"),
                    ("Cancel", "cancel"),
                ]
            ),
        ).ask()
    else:
        template = question_state

    # Define the control flow for the top level menu
    # This is simple now but will get more complicated as we add more templates
    flow_dispatch = {
        "cancel": lambda: sys.exit(),
        "js-component": lambda: jsComponentQuestions(),
        "default": lambda: appTemplateQuestions(template),
    }

    # Call the appropriate function based on the user's choice
    flow_dispatch.get(template, flow_dispatch["default"])()


def appTemplateQuestions(template: str):
    appdir = questionary.path(
        "Enter destination directory:",
        default="./",
        only_directories=True,
    ).ask()

    app_dir = copyTemplateFiles(appdir, template)
    print(f"Created Shiny app at {app_dir}")


def jsComponentQuestions():
    """
    Hand question branch for the custom js templates. This should handle the entire rest
    of the question flow and is responsible for placing files etc. Currently it repeats
    a lot of logic from the default flow but as the custom templates get more
    complicated the logic will diverge
    """

    component_type = questionary.select(
        "What kind of component do you want to build?:",
        choices=choicesArray(
            [
                ("Input component", "js-input"),
                ("Output component", "js-output"),
                ("React component", "js-react"),
                ("Back", "back"),
            ]
        ),
    ).ask()

    if component_type == "back":
        template_query()
        return

    # As what the user wants the name of their component to be
    component_name = questionary.text(
        "What do you want to name your component?",
        instruction="Name must be dash-delimited and all lowercase. E.g. 'my-component-name'",
        validate=isValidName,
    ).ask()

    appdir = questionary.path(
        "Enter destination directory:",
        default=f"./{component_name}",
        only_directories=True,
    ).ask()

    app_dir = copyTemplateFiles(appdir, component_type)

    # Print messsage saying we're building the component
    print(f"Setting up {component_name} component package...")
    updateComponentNameInTemplate(app_dir, component_name)

    shouldInstallDeps = questionary.confirm(
        "Do you want to install js dependencies now?"
    ).ask()

    if shouldInstallDeps:
        install_js_dependencies(app_dir)
    else:
        print("Skipping installing NPM deps. Run `npm install` to install them later.")

    print(f"Successfully created {component_name} component package!")
    print("Next steps:")
    print(f"- Run `cd {app_dir}` to change into the new directory")
    if not shouldInstallDeps:
        print("- Run `npm install` to install dependencies")
    print("- Run `npm run build` to build the component")
    print("- Install package locally with `pip install -e .`")
    print("- Open and run the example app in the `example-app` directory")


def choicesArray(choices: List[Tuple[str, str]]):
    """
    Convert tuple of key-value pairs for Questionary questions to a list of Choice objects
    """
    return [Choice(name, value=value) for name, value in choices]


def copyTemplateFiles(dest: str, template: str):
    if dest == ".":
        dest = f"./{template}"

    app_dir = Path(dest)
    template_dir = Path(__file__).parent / "templates" / template
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

    return app_dir
