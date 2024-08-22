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

from ._main_create_custom import (
    ComponentNameValidator,
    update_component_name_in_template,
)
from ._main_utils import (
    cli_action,
    cli_bold,
    cli_code,
    cli_danger,
    cli_field,
    cli_info,
    cli_input,
    cli_success,
    cli_url,
    cli_verbatim,
    cli_wait,
    directory_prompt,
)

# These templates are copied over from the `shiny/templates/app_templates`
# directory. The process for adding new ones is to add your app folder to
# that directory, and then add another entry to this dictionary.
app_template_choices = {
    "Basic app": "basic-app",
    "Sidebar layout": "basic-sidebar",
    "Basic dashboard": "dashboard",
    "Intermediate dashboard": "dashboard-tips",
    "Navigating multiple pages/panels": "basic-navigation",
    "Custom JavaScript component ...": "js-component",
    "Choose from the Shiny Templates website": "external-gallery",
}

# These are templates which produce a Python package and have content filled in at
# various places based on the user input. You can add new ones by following the
# examples in `shiny/templates/package-templates` and then adding entries to this
# dictionary.
package_template_choices = {
    "Input component": "js-input",
    "Output component": "js-output",
    "React component": "js-react",
}

styles_for_questions = questionary.Style([("secondary", "italic")])
# Prebuild some common choices
cancel_choice: Choice = Choice(title=[("class:secondary", "[Cancel]")], value="cancel")
back_choice: Choice = Choice(title=[("class:secondary", "← Back")], value="back")


def choice_from_dict(choice_dict: dict[str, str]) -> list[Choice]:
    return [Choice(title=key, value=value) for key, value in choice_dict.items()]


def use_template_internal(
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

    valid_template_choices = {**app_template_choices, **package_template_choices}
    if template not in valid_template_choices.values():
        raise click.BadOptionUsage(
            "--template",
            f"Invalid value for '--template' / '-t': {template} is not one of "
            + f"""'{"', '".join(valid_template_choices.values())}'.""",
        )

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


def use_template_github(
    github: str,
    template: str | None = None,
    mode: str | None = None,
    dest_dir: Path | None = None,
):
    # Github requires that we download the whole repository, so we need to
    # download and unzip the repo, then navigate to the subdirectory.

    spec = parse_github_arg(github)
    spec_cli = f"{spec.repo_owner}/{spec.repo_name}"
    if spec.ref != "HEAD":
        spec_cli = f"{spec_cli}@{spec.ref}"
    if spec.path:
        spec_cli = f"{spec_cli}:{spec.path}"

    click.echo(cli_info(f"Using GitHub repository {cli_field(spec_cli)}."))

    with tempfile.TemporaryDirectory() as temp_dir:
        extracted_dir = None
        errors: list[str] = []

        # Github uses different formats on the `archive/` endpoints for
        # refs/heads/{branch}.zip, refs/tags/{tag}.zip, or just {commit}.zip.
        # It's hard to tell in advance which one is intended, so we try all three in
        # succession, using the first that works.
        for zip_url in github_zip_url(spec):
            try:
                extracted_dir = download_and_extract_zip(zip_url, Path(temp_dir))
                break
            except Exception as err:
                errors.append(str(err))
                pass

        if extracted_dir is None:
            raise click.ClickException(
                f"Failed to download repository from GitHub {cli_url(github)}. "
                + "Please check the URL or GitHub spec and try again.\n"
                + "We received the following errors:\n"
                + textwrap.indent("\n".join(errors), "  ")
            )

        template_dir = extracted_dir / spec.path

        if not os.path.exists(template_dir):
            raise click.ClickException(
                f"Template directory '{cli_input(spec.path)}' does not exist in {cli_field(spec_cli)}."
            )

        return app_template_questions(
            template=template,
            mode=mode,
            template_dir=Path(template_dir),
            dest_dir=dest_dir,
        )


def github_zip_url(spec: GithubRepoLocation) -> Generator[str]:
    for suffix in ["refs/heads/", "refs/tags/", ""]:
        url = f"https://github.com/{spec.repo_owner}/{spec.repo_name}/archive/{suffix}{spec.ref}.zip"
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

    # We split the spec into parts, using a capture group so that the splitting
    # characters are retained in the path parts. Then we know that {repo_owner} /
    # {repo_name} come first in the first three parts, reducing the problem to parsing
    # ref and path in the remaining parts.
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

    # FIXME: We don't have any special syntax of files to signal a "template", which
    # means that we could end up here with `template_dir` being a repo of templates. If
    # `template` is missing, we end up copying everything in `template_dir` as if it's
    # all part of a single big template. When we introduce a way to signal or coordinate
    # templates in a repo, we will add a check here to avoid copying more than one
    # template.
    click.echo(
        cli_wait(
            f"Creating Shiny app from template {cli_bold(cli_field(template_dir.name))}..."
        )
    )

    # Not all apps will be implemented in both express and core so we can
    # avoid the questions if it's a core only app.
    template_files = [file.name for file in template_dir.iterdir() if file.is_file()]
    express_available = "app-express.py" in template_files

    if mode == "express" and not express_available:
        raise Exception("Express mode not available for that template.")

    dest_dir = directory_prompt(dest_dir, template_dir.name)

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
            use_template_internal()
            return

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
                    "cd " + str(app_dir) if app_dir != Path(os.curdir) else "",
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
        use_template_internal()
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

    dest_dir = directory_prompt(dest_dir, package_name)

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
                "cd " + str(app_dir) if app_dir != Path(os.curdir) else "",
                "npm install      # install dependencies",
                "npm run build    # build the component",
                "pip install -e . # install the package locally",
            ],
            indent=4,
        )
    )
    click.echo(
        f"- Open and run the example app in the {cli_field('example-app')} directory"
    )


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
