from pathlib import Path

import questionary
from questionary import Choice

from ._template_utils import copyTemplateFiles

js_component_choices = [
    ("Input component", "js-input"),
    ("Output component", "js-output"),
    ("React component", "js-react"),
    ("Cancel", "cancel"),
]


def isValidName(name: str):
    """
    Validate that the name is all lowercase and dash or space-delimited
    """
    # Check for underscores
    if "_" in name:
        return False

    # Check for uppercase letters
    if name != name.lower():
        return False

    return True


def componentTemplateQuestions():
    """
    Hand question branch for the custom js templates. This should handle the entire rest
    of the question flow and is responsible for placing files etc. Currently it repeats
    a lot of logic from the default flow but as the custom templates get more
    complicated the logic will diverge
    """
    component_type = questionary.select(
        "What kind of component do you want to build?:",
        choices=[Choice(name, value=value) for name, value in js_component_choices],
    ).ask()

    appdir = questionary.path(
        "Enter destination directory:",
        default="./",
        only_directories=True,
    ).ask()

    app_dir = copyTemplateFiles(appdir, component_type)

    # As what the user wants the name of their component to be
    component_name = questionary.text(
        "What do you want to name your component?",
        instruction="Name must be dash-delimited and all lowercase. E.g. 'my-component-name'",
        validate=isValidName,
    ).ask()

    # Print messsage saying we're building the component
    print(f"Setting up {component_name} component package...")
    updateComponentNameInTemplate(app_dir, component_name)

    shouldInstallDeps = questionary.confirm(
        "Do you want to install js dependencies now?"
    ).ask()

    if shouldInstallDeps:
        print("Installing NPM deps now...")
    else:
        print("Skipping installing NPM deps. Run `npm install` to install them later.")


def updateComponentNameInTemplate(templateDir: Path, newComponentName: str):
    """
    Function to update the name of a custom component in the template files
    Needs to find and replace the following:
    - `custom_component` -> `new_component_name`  # python module/pkg name
    - `custom-component` -> `new-component-name`  # component tag name
    - `CustomComponentEl` -> `NewComponentNameEl` # component class name
    Also needs to change some file/directory names
    - `customComponent/` -> `newComponentName/`         # python pkg name
    - `custom_component.py` -> `new_component_name.py`  # python module name
    """

    # Previous names
    old_underscore_name = "custom_component"
    old_dash_name = "custom-component"
    old_capital_case_name = "CustomComponent"

    # Create a series of names corresponding to the various formats needed
    # The name is currently provided in space-demlimited or dash-delimited format
    # e.g. "new-component-name" -> ["new", "component", "name"]
    #      "new component name" -> ["new", "component", "name"]

    # First normalize the name to be space-delimited
    # e.g. "new-component-name" -> "new component name"
    #      "new component name" -> "new component name"
    # and then split into an array of words
    name_parts = newComponentName.replace("-", " ").split(" ")

    # Now create the various formats needed
    underscore_name = "_".join(name_parts)
    dash_name = "-".join(name_parts)
    capital_case_name = "".join([part.capitalize() for part in name_parts])

    # Rename the directory containing the python code: aka ./custom_component -> ./new_component_name
    python_pkg_dir = templateDir / old_underscore_name
    python_pkg_dir.rename(templateDir / underscore_name)

    # Next rename the python module: aka ./new_component_name/custom_component.py -> ./new_component_name/new_component_name.py
    python_module_path = templateDir / underscore_name / f"{old_underscore_name}.py"
    python_module_path.rename(templateDir / underscore_name / f"{underscore_name}.py")

    def updateNamesInFiles(dir: Path):
        # Now do a find-and-replace for the various name types across all the files in the
        # template directory
        for item in dir.iterdir():
            if item.is_file():
                # Only do this for files
                with open(item, "r") as f:
                    file_contents = f.read()
                # First, "custom_component" -> "new_component_name"
                file_contents = file_contents.replace(
                    old_underscore_name, underscore_name
                )
                # Next, "custom-component" -> "new-component-name"
                file_contents = file_contents.replace(old_dash_name, dash_name)
                # Next, "CustomComponentEl" -> "NewComponentNameEl"
                file_contents = file_contents.replace(
                    old_capital_case_name, capital_case_name
                )

                with open(item, "w") as f:
                    f.write(file_contents)

    # Loop over dirs_to_update and run the update function on them
    for dir_to_update in ["", "srcts", underscore_name, "example-app"]:
        updateNamesInFiles(templateDir / dir_to_update)
