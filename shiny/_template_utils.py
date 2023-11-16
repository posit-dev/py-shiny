import shutil
import sys
from pathlib import Path

# import questionary
# from questionary import Choice


def copyTemplateFiles(dest: str, template: str):
    if dest == ".":
        dest = f"./{template}"

    app_dir = Path(dest)
    template_dir = Path(__file__).parent / "templates" / template
    duplicate_files = [
        file.name for file in template_dir.iterdir() if (app_dir / file.name).exists()
    ]
    print(duplicate_files)

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
