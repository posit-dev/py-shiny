from __future__ import annotations

import json
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


def choice_from_templates(templates: list[ShinyTemplate]) -> list[Choice]:
    return [Choice(title=t.title, value=t.name) for t in templates]


@dataclass
class ShinyTemplate:
    name: str
    path: Path
    type: str = "app"
    title: str | None = None
    description: str | None = None
    _express_available: bool | None = None

    @property
    def express_available(self) -> bool:
        if self._express_available is None:
            self._express_available = (self.path / "app-express.py").exists()
        return self._express_available


def find_templates(path: Path | str = ".") -> list[ShinyTemplate]:
    path = Path(path)
    templates: list[ShinyTemplate] = []

    template_files = sorted(path.glob("**/_template.json"))
    for tf in template_files:
        with tf.open() as f:
            template = json.load(f)
            templates.append(
                ShinyTemplate(
                    name=template["name"],
                    title=template.get("title"),
                    path=tf.parent.absolute(),
                    type=template.get("type", "app"),
                    description=template.get("description"),
                )
            )

    return templates


def template_by_name(templates: list[ShinyTemplate], name: str) -> ShinyTemplate | None:
    for template in templates:
        if template.name == name:
            return template
    return None


class ShinyInternalTemplates:
    def __init__(self):
        self.templates: list[ShinyTemplate] | None = None

    def _templates(self) -> list[ShinyTemplate]:
        if self.templates is not None:
            return self.templates
        self.templates = find_templates(Path(__file__).parent / "templates")
        return self.templates

    @property
    def apps(self) -> list[ShinyTemplate]:
        templates = self._templates()
        return [t for t in templates if t.type == "app"]

    @property
    def packages(self) -> list[ShinyTemplate]:
        templates = self._templates()
        return [t for t in templates if t.type == "package"]


shiny_internal_templates = ShinyInternalTemplates()


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

    app_templates = shiny_internal_templates.apps
    pkg_templates = shiny_internal_templates.packages

    menu_choices = [
        Choice(title="Custom JavaScript component...", value="js-component"),
        Choice(
            title="Choose from the Shiny Templates website", value="external-gallery"
        ),
        cancel_choice,
    ]

    if question_state is None:
        question_state = questionary.select(
            "Which template would you like to use?:",
            choices=[
                *choice_from_templates(app_templates),
                *menu_choices,
            ],
            style=styles_for_questions,
        ).ask()

    if question_state is None or question_state == "cancel":
        sys.exit(1)

    template = template_by_name([*app_templates, *pkg_templates], question_state)

    if template is not None:
        if template.type == "app":
            return app_template_questions(template, mode, dest_dir=dest_dir)
        if template.type == "package":
            return js_component_questions(
                template, dest_dir=dest_dir, package_name=package_name
            )

    if question_state == "external-gallery":
        url = cli_url("https://shiny.posit.co/py/templates")
        click.echo(f"Opening {url} in your browser.")
        click.echo(
            f"Choose a template and copy the {cli_code('shiny create')} command to use it."
        )
        import webbrowser

        webbrowser.open(url)
        sys.exit(0)
    elif question_state == "js-component":
        js_component_questions(dest_dir=dest_dir, package_name=package_name)
    else:
        valid_choices = [t.name for t in app_templates + pkg_templates]
        if question_state not in valid_choices:
            raise click.BadOptionUsage(
                "--template",
                f"Invalid value for '--template' / '-t': {question_state} is not one of "
                + f"""'{"', '".join(valid_choices)}'.""",
            )


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
    template_name: str | None = None,
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

        templates = find_templates(template_dir)

        if not templates:
            # Legacy: repo doesn't have _template.json files, so we have to rely on
            # paths, i.e. template_dir / template_name
            if template_name is None:
                # warn that we're assuming the repo spec points to the template directly
                click.echo(
                    cli_info(
                        f"Using {cli_field(spec_cli)} as the template. "
                        + f"Use {cli_code('--template')} to specify a template otherwise."
                    )
                )
                template_name = template_dir.name
            else:
                template_dir = template_dir / template_name

            template = ShinyTemplate(
                name=template_name,
                title=f"Template from {spec_cli}",
                path=template_dir,
            )
        elif template_name:
            # Repo has templates and the user already picked one
            template = template_by_name(templates, template_name)
            if not template:
                raise click.ClickException(
                    f"Template '{cli_input(template_name)}' not found in {cli_field(spec_cli)}."
                )
        else:
            # Has templates, but the user needs to pick one
            template_name = questionary.select(
                "Which template would you like to use?:",
                choices=[*choice_from_templates(templates), cancel_choice],
                style=styles_for_questions,
            ).ask()

            if template_name is None or template_name == "cancel":
                sys.exit(1)

            template = template_by_name(templates, template_name)
            if not template:
                raise click.ClickException(
                    f"Template '{cli_input(template_name)}' not found in {cli_field(spec_cli)}."
                )

        return app_template_questions(
            template=template,
            mode=mode,
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
    template: ShinyTemplate,
    mode: Optional[str] = None,
    dest_dir: Optional[Path] = None,
):
    template_dir = template.path
    template_cli_name = cli_bold(cli_field(template.title or template.name))

    if mode == "express" and not template.express_available:
        raise click.BadParameter(
            f"Express mode not available for the {template_cli_name} template."
        )

    click.echo(cli_wait(f"Creating {template_cli_name} Shiny app..."))
    dest_dir = directory_prompt(dest_dir, template_dir.name)

    if mode is None and template.express_available:
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

    app_dir = copy_template_files(template, dest_dir, mode=mode)

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
    component_type: Optional[str | ShinyTemplate] = None,
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
                *choice_from_templates(shiny_internal_templates.packages),
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

    if isinstance(component_type, ShinyTemplate):
        template = component_type
    else:
        template = template_by_name(shiny_internal_templates.packages, component_type)

    if template is None:
        # Validation should have happened in `use_template_internal()`
        raise ValueError(f"Package template for {component_type} not found.")

    # Ask what the user wants the name of their component to be
    if package_name is None:
        package_name = questionary.text(
            "What do you want to name your component?",
            instruction="Name must be dash-delimited and all lowercase. E.g. 'my-component-name'",
            validate=ComponentNameValidator,
        ).ask()

        if package_name is None:
            sys.exit(1)

    dest_dir = directory_prompt(dest_dir, package_name)

    app_dir = copy_template_files(template, dest_dir, mode=None)

    # Print message saying we're building the component
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
    template: ShinyTemplate,
    dest_dir: Path,
    mode: Optional[str] = None,
):
    files_to_check = [file.name for file in template.path.iterdir()]

    if "__pycache__" in files_to_check:
        files_to_check.remove("__pycache__")

    files_to_check.append("app.py")

    duplicate_files = [file for file in files_to_check if (dest_dir / file).exists()]

    if any(duplicate_files):
        err_files = ", ".join([cli_input('"' + file + '"') for file in duplicate_files])
        click.echo(
            cli_danger(
                "Error: Can't create new files because the following files "
                + f"already exist in the destination directory: {err_files}."
            )
        )
        sys.exit(1)

    if not dest_dir.exists():
        dest_dir.mkdir()

    for item in template.path.iterdir():
        if item.is_file():
            if item.name == "_template.json":
                continue
            shutil.copy(item, dest_dir / item.name)
        else:
            if item.name != "__pycache__":
                shutil.copytree(item, dest_dir / item.name)

    def rename_unlink(file_to_rename: str, file_to_delete: str, dir: Path = dest_dir):
        (dir / file_to_rename).rename(dir / "app.py")
        (dir / file_to_delete).unlink()

    if template.express_available:
        if mode == "express":
            rename_unlink("app-express.py", "app-core.py")
        if mode == "core":
            rename_unlink("app-core.py", "app-express.py")
    if (dest_dir / "app-core.py").exists():
        (dest_dir / "app-core.py").rename(dest_dir / "app.py")

    return dest_dir