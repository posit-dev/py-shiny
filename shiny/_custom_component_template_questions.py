import subprocess
from pathlib import Path


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


def install_js_dependencies(app_dir: Path):
    """
    Installs JS dependencies using npm in the specified directory and streams the output.

    Args:
    app_dir (str): The directory where npm install should be executed.
    """
    print("Installing NPM deps now...")

    try:
        process = subprocess.Popen(
            ["npm", "install"],
            cwd=app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,  # Ensures text mode is used
        )

        # Stream the output line by line
        while True:
            stdout = process.stdout
            if stdout is None:
                break
            output = stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

        # Check the return code
        rc = process.poll()
        if rc != 0:
            print(f"npm install failed with exit code {rc}")
            return False
        else:
            print("npm install completed successfully.")
            return True

    except Exception as e:
        print(f"An error occurred while installing NPM dependencies: {e}")
        return False


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
