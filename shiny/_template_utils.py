from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import textwrap
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Optional, cast
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

import click
import questionary
from questionary import Choice

from ._custom_component_template_questions import (
    ComponentNameValidator,
    update_component_name_in_template,
)

# The choices are specified in _main because they populate the
# CLI flag options.
from ._main import app_template_choices, package_template_choices

styles_for_questions = questionary.Style([("secondary", "italic")])
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
    elif template == "external-gallery":
        url = cli_url("https://shiny.posit.co/py/templates")
        click.echo(f"Opening {url} in your browser.")
        click.echo(
            f"Choose a template and copy the {cli_code('shiny create')} command to use it."
        )
        import webbrowser

        webbrowser.open(url)
        sys.exit(0)
    elif template == "js-component":
        js_component_questions(dest_dir=dest_dir, package_name=package_name)
        return
    elif template in package_template_choices.values():
        js_component_questions(template, dest_dir=dest_dir, package_name=package_name)
    else:
        app_template_questions(template, mode, dest_dir=dest_dir)


def download_and_extract_zip(url: str, temp_dir: Path) -> Path:
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

    items = list(temp_dir.iterdir())

    # If we unzipped a single directory, return the path to that directory.
    # This avoids much nonsense in trying to guess the directory name, which technically
    # can be derived from the zip file URL, but it's not worth the effort.
    directories = [d for d in items if d.is_dir()]
    files = [f for f in items if f.is_file() and f.name != "repo.zip"]

    # We have exactly one directory and no other files
    if len(directories) == 1 and len(files) == 0:
        return directories[0]

    return temp_dir


def use_git_template(
    url: str,
    template: str | None = None,
    mode: str | None = None,
    dest_dir: Path | None = None,
):
    # Github requires that we download the whole repository, so we need to
    # download and unzip the repo, then navigate to the subdirectory.

    spec = parse_github_arg(url)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        template_dir = temp_dir
        success = False

        # Github uses different formats on the `archive/` endpoints for
        # refs/heads/{branch}.zip, refs/tags/{tag}.zip, or just {commit}.zip.
        # It's hard to tell in advance which one is intended, so we try all three in
        # succession, using the first that works.
        for zip_url in github_zip_url(spec):
            try:
                template_dir = download_and_extract_zip(zip_url, temp_dir)
                success = True
                break
            except Exception:
                pass

        if not success:
            raise click.ClickException(
                f"Failed to download repository from GitHub {cli_url(url)}."
                + " Please check the URL or GitHub spec and try again."
            )

        template_dir = template_dir / spec.path

        if not os.path.exists(template_dir):
            raise click.ClickException(
                f"Template directory '{cli_input(spec.path)}' does not exist "
                + f"in the {cli_field(spec.repo_owner + "/" + spec.repo_name)} repository."
            )

        return app_template_questions(
            template=template,
            mode=mode,
            template_dir=Path(template_dir),
            dest_dir=dest_dir,
        )


def github_zip_url(repo_location: GithubRepoLocation) -> Generator[str]:
    for suffix in ["refs/heads/", "refs/tags/", ""]:
        url = f"https://github.com/{repo_location.repo_owner}/{repo_location.repo_name}/archive/{suffix}{repo_location.ref}.zip"
        yield url


@dataclass
class GithubRepoLocation:
    repo_owner: str
    repo_name: str
    ref: str
    path: str


def parse_github_arg(x: str) -> GithubRepoLocation:
    if re.match(r"^(https?:)//|github[.]com", x):
        return parse_github_url(x)
    return parse_github_spec(x)


def parse_github_spec(spec: str):
    """
    Parses GitHub repo + path spec in the form of:

    * {repo_owner}/{repo_name}@{ref}:{path}
    * {repo_owner}/{repo_name}:{path}@{ref}
    * {repo_owner}/{repo_name}:{path}
    * {repo_owner}/{repo_name}/{path}
    * {repo_owner}/{repo_name}/{path}@{ref}
    * {repo_owner}/{repo_name}/{path}?ref={ref}
    """

    parts = re.split(r"(:|@|[?]ref=|/)", spec)

    if len(parts) < 3:
        raise click.BadParameter(
            f"Could not parse as GitHub spec: '{cli_input(spec)}'"
            + ". Please use the format "
            + cli_field("{repo_owner}/{repo_name}@{ref}:{path}")
            + ".",
            param_hint="--github",
        )

    repo_owner, _, repo_name = parts[:3]
    path = ""
    ref = ""

    which = "path"
    for i, part in enumerate(parts[3:]):
        # special characters indicate a change in which part we're parsing
        if i == 0 and part == "/":
            continue
        if part in ("@", "?ref="):
            which = "ref"
            continue
        if part == ":":
            which = "path"
            continue
        # send each part to the correct repo variable
        if which == "path":
            path += part
        elif which == "ref":
            ref += part

    if ref == "":
        ref = "HEAD"

    return GithubRepoLocation(
        repo_owner=repo_owner,
        repo_name=repo_name,
        ref=ref,
        path=path,
    )


def parse_github_url(x: str) -> GithubRepoLocation:
    """
    Parses a GitHub URL

    e.g. "https://github.com/posit-dev/py-shiny-templates/tree/main/dashboard"
    """

    if not re.match(r"^(https?:)//", x):
        x = "//" + x

    parsed_url = urlparse(x)
    path_parts = parsed_url.path.strip("/").split("/")
    repo_owner, repo_name, _, ref = path_parts[:4]
    path = "/".join(path_parts[4:])
    return GithubRepoLocation(
        repo_owner=repo_owner,
        repo_name=repo_name,
        ref=ref,
        path=path,
    )


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
    elif template is not None:
        template_dir = template_dir / template

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

    click.echo(cli_success(f"Created Shiny app at {cli_field(str(app_dir))}"))
    click.echo()
    click.echo(cli_action(cli_bold("Next steps:")))
    if (app_dir / "requirements.txt").exists():
        click.echo("- Install required dependencies:")
        click.echo(
            cli_verbatim(
                [
                    "cd " + str(app_dir),
                    "pip install -r requirements.txt",
                ],
                indent=4,
            )
        )
    click.echo(f"- Open and edit the app file: {cli_field(str(app_dir / 'app.py'))}")


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
    click.echo(cli_wait(f"Setting up {cli_field(package_name)} component package..."))
    update_component_name_in_template(app_dir, package_name)

    click.echo()
    click.echo(cli_action(cli_bold("Next steps:")))
    click.echo("- Setup your component:")
    click.echo(
        cli_verbatim(
            [
                "cd " + str(app_dir),
                "npm install      # install dependencies",
                "npm run build    # build the component",
                "pip install -e . # install the package locally",
            ],
            indent=4,
        )
    )
    click.echo(f"- Open and run the example app in the {cli_field('example-app')} directory")


def directory_prompt(
    template_dir: Path, dest_dir: Optional[Path | str | None] = None
) -> Path:
    if dest_dir is not None:
        return Path(dest_dir)

    app_dir = questionary.path(
        "Enter destination directory:",
        default=path_rel_wd(),
        only_directories=True,
    ).ask()

    if app_dir is None:
        sys.exit(1)

    if app_dir == ".":
        app_dir = path_rel_wd(template_dir.name)

    return Path(app_dir)


def path_rel_wd(*path: str):
    """
    Path relative to the working directory, formatted for the current OS
    """
    return os.path.join(".", *(path or [""]))


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
        err_files = ", ".join([cli_input('"' + file + '"') for file in duplicate_files])
        click.echo(
            cli_danger(
                "Error: Can't create new files because the following files "
                + f"already exist in the destination directory: {err_files}."
            )
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


def cli_field(x: str):
    return click.style(x, fg="cyan")


def cli_bold(x: str):
    return click.style(x, bold=True)


def cli_ital(x: str):
    return click.style(x, italic=True)


def cli_input(x: str):
    return click.style(x, fg="green")


def cli_code(x: str):
    return click.style("`" + x + "`", fg="magenta")


def cli_verbatim(x: str | list[str], indent: int = 2):
    lines = [click.style(line, fg="cyan") for line in x if line != ""]
    return textwrap.indent("\n".join(lines), " " * indent)


def cli_url(x: str):
    return click.style(x, fg="blue", underline=True)


def cli_success(x: str):
    return click.style("\u2713", fg="green") + " " + x


def cli_info(x: str):
    return click.style("\u2139", fg="blue") + " " + x


def cli_action(x: str):
    return click.style("→", fg="blue") + " " + x


def cli_warning(x: str):
    return click.style("!", fg="yellow") + " " + x


def cli_danger(x: str):
    return click.style("\u00d7", fg="red") + " " + x


def cli_wait(x: str):
    return click.style("\u2026", fg="yellow") + " " + x
