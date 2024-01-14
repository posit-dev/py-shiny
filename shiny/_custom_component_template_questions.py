import re
from importlib import util
from pathlib import Path

from prompt_toolkit.document import Document
from questionary import ValidationError, Validator


def is_existing_module(name: str) -> bool:
    """
    Check if a module name can be imported, which indicates that it is either
    a standard module name, or the name of an installed module.
    In either case the new module would probably cause a name conflict.
    """
    try:
        spec = util.find_spec(name)
        if spec is not None:
            return True
        else:
            return False
    except ImportError:
        return False


def is_pep508_identifier(name: str):
    """
    Checks if a package name is a PEP 508 identifier.
    """
    # Regex from https://peps.python.org/pep-0508/#names
    pattern = re.compile(r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$", re.IGNORECASE)
    return bool(pattern.match(name))


class ComponentNameValidator(Validator):
    def validate(self, document: Document):
        """
        Validate that the name is all lowercase and dash or space-delimited
        """
        name = document.text

        # Dont accept empty names
        if len(name) == 0:
            raise ValidationError(
                message="Name needed for component",
                cursor_position=len(name),
            )

        # Check for underscores
        if "_" in name:
            raise ValidationError(
                message="Use dashes `-` instead of underscores `_`",
                cursor_position=len(name),
            )

        # Check for uppercase letters
        if name != name.lower():
            raise ValidationError(
                message="Name must be all lowercase",
                cursor_position=len(name),
            )

        # Check for quotations

        if (
            name.startswith('"')
            or name.endswith('"')
            or name.startswith("'")
            or name.endswith("'")
        ):
            raise ValidationError(
                message="The name should be unquoted.",
                cursor_position=len(name),
            )

        # Pypi only allows names shorter than 214 characters
        if len(name) > 214:
            raise ValidationError(message="Name can't exceed 214 characters")

        if not is_pep508_identifier(name):
            raise ValidationError(
                message="Name must be a pep508 identifier: https://peps.python.org/pep-0508/#names",
                cursor_position=len(name),
            )

        # Using the name of an existing package causes an import error

        if is_existing_module(name):
            raise ValidationError(
                message="Package already installed in your current environment.",
                cursor_position=len(name),
            )


def update_component_name_in_template(template_dir: Path, new_component_name: str):
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
    name_parts = new_component_name.replace("-", " ").split(" ")

    # Now create the various formats needed
    underscore_name = "_".join(name_parts)
    dash_name = "-".join(name_parts)
    capital_case_name = "".join([part.capitalize() for part in name_parts])

    # Rename the directory containing the python code: aka ./custom_component -> ./new_component_name
    python_pkg_dir = template_dir / old_underscore_name
    python_pkg_dir.rename(template_dir / underscore_name)

    # Next rename the python module: aka ./new_component_name/custom_component.py -> ./new_component_name/new_component_name.py
    python_module_path = template_dir / underscore_name / f"{old_underscore_name}.py"
    python_module_path.rename(template_dir / underscore_name / f"{underscore_name}.py")

    def update_names_in_files(dir: Path):
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
        update_names_in_files(template_dir / dir_to_update)
