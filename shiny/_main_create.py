from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
import textwrap
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, Literal, Optional, cast
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
    cli_warning,
    directory_prompt,
)

styles_for_questions = questionary.Style([("secondary", "italic")])
# Prebuild some common choices
cancel_choice: Choice = Choice(title=[("class:secondary", "[Cancel]")], value="cancel")
back_choice: Choice = Choice(title=[("class:secondary", "← Back")], value="back")


def choice_from_templates(templates: list[ShinyTemplate]) -> list[Choice]:
    return [Choice(title=t.title, value=t.id) for t in templates]


@dataclass
class ShinyTemplate:
    """
    Shiny Template

    This class receives metadata for a Shiny template from a `_template.json` file.
    (Alternatively, a template can be created from just `name` and `path` for legacy
    reasons.)

    Attributes
    ----------
    id
        The identifier of the Shiny template. This `id` should be unique within a
        repository of templates.
    path
        The path to the `_template.json` file or the root directory of the template.
    type
        The type of the template (e.g. "app", "package"), default: 'app'.
    title
        A brief title for the template, if provided.
    description
        A longer description of the template, if provided.
    next_steps
        A list of next steps or instructions related to this template, shown after the
        default instructions are displayed. In the `_template.json` file, this field
        can be a single string or an array of strings.
    follow_up
        A list of follow-up actions or information related to this template. In the
        `_template.json` file, this field can be a single string, an array of strings,
        or an object with a `text` field and an optional `type` field. The `type` field
        can be "action", "info", "warning", "danger", or "text".
    """

    id: str
    path: Path
    type: str = "app"
    title: str | None = None
    description: str | None = None
    next_steps: list[str] = field(default_factory=list)
    follow_up: list[ShinyTemplateFollowUp] = field(default_factory=list)
    _express_available: bool | None = None

    @property
    def express_available(self) -> bool:
        """
        Does the template include an Express variant, denoted by the presence of an
        `app-express.py` file?
        """

        if self._express_available is None:
            self._express_available = (self.path / "app-express.py").exists()
        return self._express_available


class ShinyTemplateFollowUp:
    def __init__(
        self,
        text: str,
        type: str = "text",
    ):
        self.text = text
        self.type: Literal["action", "info", "warning", "danger", "text"] = "text"
        if type in ("action", "info", "warning", "danger"):
            self.type = type


def find_templates(path: Path | str = ".") -> list[ShinyTemplate]:
    path = Path(path)
    templates: list[ShinyTemplate] = []
    duplicated_ids: set[str] = set()

    template_files = sorted(path.glob("**/_template.json"))
    for tf in template_files:
        with tf.open() as f:
            try:
                template = json.load(f)
            except json.JSONDecodeError as err:
                raise ValueError(f"Error parsing {tf}: {err}")

            # "next_steps" and "follow_up" can be either a string or an array of strings
            # or an array of dictionaries (follow_up only)
            follow_up_raw: str | list[dict[str, str]] = template.get("follow_up", [])
            if isinstance(follow_up_raw, str):
                follow_up_raw = [{"text": follow_up_raw}]

            follow_up = [ShinyTemplateFollowUp(**f) for f in follow_up_raw]

            next_steps: str | list[str] = template.get("next_steps", [])
            if isinstance(next_steps, str):
                next_steps = [next_steps]

            if "id" not in template:
                raise ValueError(f"Template in {tf} is missing a 'id' field.")

            id = template["id"]
            if id in [t.id for t in templates]:
                duplicated_ids.add(id)

            templates.append(
                ShinyTemplate(
                    id=id,
                    path=tf.parent.absolute(),
                    title=template.get("title"),
                    type=template.get("type", "app"),
                    description=template.get("description"),
                    follow_up=follow_up,
                    next_steps=next_steps,
                )
            )

    if duplicated_ids:
        click.echo(
            cli_danger(
                "Warning: The following templates contain duplicate IDs. "
                + "Only the first occurrence will be used."
            )
        )
        for id in duplicated_ids:
            paths = [t.path.relative_to(path) for t in templates if t.id == id]
            click.echo(
                cli_warning(
                    cli_code(f'"id": "{id}"')
                    + " used by: "
                    + ", ".join([cli_field(str(p)) for p in paths])
                )
            )

    return templates


def template_by_name(templates: list[ShinyTemplate], name: str) -> ShinyTemplate | None:
    for template in templates:
        if template.id == name:
            return template
    return None


class ShinyInternalTemplates:
    """
    Shiny's Internal Templates

    Internal templates that are built into the shiny package are always available via
    `shiny create`. These templates are stored in the `shiny/templates` directory and
    are divided into `app-templates` and `package-templates`.

    To add a new template, create the template subfolder in either of the two template
    folders and add a `_template.json` file. See `ShinyTemplate` for expected fields.

    * `use_template_internal()` is the initial menu seen, which presents `templates/app`
      templates with additional choices.
    * `templates/package` templates are also referred to as `js-components` in the code
      base, these templates appear as a submenu and are handled by
      `use_internal_package_template()`.
    * `templates/chat` templates are generative AI templates and are handled by
      `use_internal_chat_ai_template()`,
    """

    def __init__(self):
        self.templates: dict[str, list[ShinyTemplate]] = {}

    def _templates(self, dir: str = "templates") -> list[ShinyTemplate]:
        if dir in self.templates:
            return self.templates[dir]
        self.templates[dir] = find_templates(Path(__file__).parent / dir)
        return self.templates[dir]

    @property
    def apps(self) -> list[ShinyTemplate]:
        return self._templates("templates/app")

    @property
    def packages(self) -> list[ShinyTemplate]:
        return self._templates("templates/package")

    @property
    def chat_llms(self) -> list[ShinyTemplate]:
        return self._templates("templates/chat/llms")

    @property
    def chat_enterprise(self) -> list[ShinyTemplate]:
        return self._templates("templates/chat/llm-enterprise")

    @property
    def stream_llms(self) -> list[ShinyTemplate]:
        return self._templates("templates/markdown-stream/llms")

    @property
    def stream_enterprise(self) -> list[ShinyTemplate]:
        return self._templates("templates/markdown-stream/llm-enterpise")


shiny_internal_templates = ShinyInternalTemplates()


def use_internal_template(
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
    gen_ai_templates = [
        *shiny_internal_templates.chat_llms,
        *shiny_internal_templates.chat_enterprise,
        *shiny_internal_templates.stream_llms,
        *shiny_internal_templates.stream_enterprise,
    ]

    menu_choices = [
        Choice(title="Generative AI...", value="_gen-ai"),
        Choice(title="Custom JavaScript component...", value="_js-component"),
        Choice(
            title="Choose from the Shiny Templates website", value="_external-gallery"
        ),
    ]

    if question_state is None:
        question_state = question_choose_template(app_templates, *menu_choices)

    template = template_by_name(
        [*app_templates, *pkg_templates, *gen_ai_templates], question_state
    )

    if template is not None:
        if template.type == "app":
            return app_template_questions(template, mode, dest_dir=dest_dir)
        if template.type == "package":
            return package_template_questions(
                template, dest_dir=dest_dir, package_name=package_name
            )

    if question_state == "_external-gallery":
        url = "https://shiny.posit.co/py/templates"
        click.echo(f"Opening {cli_url(url)} in your browser.")
        click.echo(
            f"Choose a template and copy the {cli_code('shiny create')} command to use it."
        )
        import webbrowser

        webbrowser.open(url)
        sys.exit(0)
    elif question_state == "_js-component":
        use_internal_package_template(dest_dir=dest_dir, package_name=package_name)
    elif question_state == "_gen-ai":
        use_internal_gen_ai_template(dest_dir=dest_dir, package_name=package_name)
    else:
        valid_choices = [t.id for t in app_templates + pkg_templates]
        if question_state not in valid_choices:
            raise click.BadOptionUsage(
                "--template",
                f"Invalid value for '--template' / '-t': {question_state} is not one of "
                + f"""'{"', '".join(valid_choices)}'.""",
            )


def use_internal_package_template(
    dest_dir: Optional[Path] = None,
    package_name: Optional[str] = None,
):
    input = questionary.select(
        "What kind of component do you want to build?",
        choices=[
            *choice_from_templates(shiny_internal_templates.packages),
            back_choice,
            cancel_choice,
        ],
        style=styles_for_questions,
    ).ask()

    if input == "back":
        use_internal_template()
        return

    if input is None or input == "cancel":
        sys.exit(1)

    template = template_by_name(shiny_internal_templates.packages, input)

    if template is None:
        # This should be valid because we're selecting from the list of templates
        # but just in case and to make type checkers happy
        raise ValueError(f"Package template for {input} not found.")

    package_template_questions(template, dest_dir=dest_dir, package_name=package_name)


def use_internal_gen_ai_template(
    input: str | None = None,
    dest_dir: Optional[Path] = None,
    package_name: Optional[str] = None,
):
    if input is None:
        input = questionary.select(
            "Which kind of Gen AI template would you like?",
            choices=[
                Choice(title="Chat with LLM...", value="_chat-llms"),
                Choice(
                    title="Chat with enterprise LLM...", value="_chat-llm_enterprise"
                ),
                Choice(title="Stream markdown with LLM...", value="_stream-llms"),
                Choice(
                    title="Stream markdown with enterprise LLM...",
                    value="_stream-enterprise",
                ),
                back_choice,
                cancel_choice,
            ],
            style=styles_for_questions,
        ).ask()

        if input is None or input == "cancel":
            sys.exit(1)

        if input == "back":
            use_internal_template(dest_dir=dest_dir, package_name=package_name)
            return

        use_internal_gen_ai_template(
            input, dest_dir=dest_dir, package_name=package_name
        )
        return

    if input == "_chat-llms":
        template_choices = shiny_internal_templates.chat_llms
    elif input == "_chat-llm_enterprise":
        template_choices = shiny_internal_templates.chat_enterprise
    elif input == "_stream-llms":
        template_choices = shiny_internal_templates.stream_llms
    elif input == "_stream-enterprise":
        template_choices = shiny_internal_templates.stream_enterprise
    else:
        raise ValueError(f"Invalid Gen AI template choice: {input}")

    choice = question_choose_template(template_choices, back_choice)

    if choice == "back":
        use_internal_gen_ai_template(dest_dir=dest_dir, package_name=package_name)
        return

    template = template_by_name(
        [
            *shiny_internal_templates.chat_llms,
            *shiny_internal_templates.chat_enterprise,
            *shiny_internal_templates.stream_llms,
            *shiny_internal_templates.stream_enterprise,
        ],
        choice,
    )

    if template is None:
        raise ValueError(f"Chat AI template for {choice} not found.")

    app_template_questions(template, dest_dir=dest_dir, mode=None)


def question_choose_template(
    templates: list[ShinyTemplate],
    *extras: Choice,
) -> str:
    """
    Ask the user to pick one of the templates. Includes and handles the cancel choice.
    """

    choice = questionary.select(
        "Which template would you like to use?",
        choices=[*choice_from_templates(templates), *extras, cancel_choice],
        style=styles_for_questions,
    ).ask()

    if choice is None or choice == "cancel":
        sys.exit(1)

    return choice


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


def use_github_template(
    github: str,
    template_name: str | None = None,
    mode: str | None = None,
    dest_dir: Path | None = None,
    package_name: str | None = None,
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
                id=template_name,
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
            template_name = question_choose_template(templates)
            template = template_by_name(templates, template_name)

            if not template:
                raise click.ClickException(
                    f"Template '{cli_input(template_name)}' not found in {cli_field(spec_cli)}."
                )

        if template.type == "package":
            return package_template_questions(
                template,
                dest_dir=dest_dir,
                package_name=package_name,
            )
        else:
            return app_template_questions(template, dest_dir=dest_dir, mode=mode)


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
    template_cli_name = cli_bold(cli_field(template.title or template.id))

    if mode == "express" and not template.express_available:
        raise click.BadParameter(
            f"Express mode not available for the {template_cli_name} template."
        )

    click.echo(cli_wait(f"Creating {template_cli_name} Shiny app..."))
    dest_dir = directory_prompt(dest_dir, template.id)

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
            use_internal_template()
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

    click_echo_next_steps_and_follow_up(template)


def package_template_questions(
    template: ShinyTemplate,
    dest_dir: Optional[Path] = None,
    package_name: Optional[str] = None,
):
    # Ask what the user wants the name of their component to be
    if package_name is None:
        package_name = questionary.text(
            "What do you want to name your component?",
            instruction="Name must be dash-delimited and all lowercase. E.g. 'my-component-name'",
            validate=ComponentNameValidator,
        ).ask()

        if package_name is None:
            sys.exit(1)

    app_dir = copy_template_files(
        template,
        dest_dir=directory_prompt(dest_dir, package_name),
        mode=None,
    )

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

    click_echo_next_steps_and_follow_up(template)


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

    dest_dir.mkdir(parents=True, exist_ok=True)

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


def click_echo_next_steps_and_follow_up(template: ShinyTemplate):
    for next_step in template.next_steps:
        click.echo(f"- {next_step}")

    if len(template.follow_up) > 0:
        click.echo()
        for follow_up in template.follow_up:
            click.echo(cli_follow_up(follow_up))


def cli_follow_up(follow_up: ShinyTemplateFollowUp):
    if follow_up.type == "text":
        return follow_up.text
    if follow_up.type == "action":
        return cli_action(follow_up.text)
    if follow_up.type == "info":
        return cli_info(follow_up.text)
    if follow_up.type == "warning":
        return cli_danger(follow_up.text)
    if follow_up.type == "danger":
        return cli_danger(follow_up.text)

    return follow_up.text
