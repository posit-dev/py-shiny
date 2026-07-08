from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from .. import __version__

# Re-exported as `shiny.run_app` (see `shiny/__init__.py`)
from ._run import run
from ._run import run_app as run_app  # noqa: F401
from ._skills import skills
from ._static import cells_to_app, get_shiny_deps, static, static_assets


@click.group("main")
@click.version_option(__version__)
def main() -> None:
    pass


main.add_command(run)
main.add_command(skills)
main.add_command(static)
main.add_command(static_assets)
main.add_command(cells_to_app)
main.add_command(get_shiny_deps)


@main.group(help="""Add files to enhance your Shiny app.""")
def add() -> None:
    pass


@add.command(help="""Add a test file for a specified Shiny app.

Generate a comprehensive test file for a specified app using AI. The generator
will analyze your app code and create appropriate test cases with assertions.

After creating the test file, you can use `pytest` to run the tests:

        pytest TEST_FILE
""")
@click.option(
    "--app",
    "-a",
    type=str,
    help="Path to the app file for which you want to generate a test file.",
)
@click.option(
    "--test-file",
    "-t",
    type=str,
    help="Path for the generated test file. If not provided, will be auto-generated.",
)
@click.option(
    "--provider",
    type=click.Choice(["anthropic", "openai"]),
    default="anthropic",
    help="AI provider to use for test generation.",
)
@click.option(
    "--model",
    type=str,
    help="Specific model to use (optional). Examples: haiku3.5, sonnet,  gpt-5, gpt-5-mini",
)
# Param for app.py, param for test_name
def test(
    app: str | None,
    test_file: str | None,
    provider: str,
    model: str | None,
) -> None:
    from ._generate_test import generate_test_file

    generate_test_file(
        app_file=app, output_file=test_file, provider=provider, model=model
    )


@main.command(help="""Create a Shiny application from a template.

Create an app based on a template. You will be prompted with
a number of application types, as well as the destination folder.
If you don't provide a destination folder, it will be created in the current working
directory based on the template name.

After creating the application, you use `shiny run`:

    shiny run APPDIR/app.py --reload
""")
@click.option(
    "--template",
    "-t",
    type=click.STRING,
    help="Choose a template for your new application.",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(
        ["core", "express"],
        case_sensitive=False,
    ),
    help="Do you want to use a Shiny Express template or a Shiny Core template?",
)
@click.option(
    "--github",
    "-g",
    help="""
    The GitHub repo containing the template, e.g. 'posit-dev/py-shiny-templates'.
    Can be in the format '{repo_owner}/{repo_name}', '{repo_owner}/{repo_name}@{ref}',
    or '{repo_owner}/{repo_name}:{path}@{ref}'.
    Alternatively, a GitHub URL of the template sub-directory, e.g
    'https://github.com/posit-dev/py-shiny-templates/tree/main/dashboard'.
    """,
)
@click.option(
    "--dir",
    "-d",
    type=str,
    help="The destination directory, you will be prompted if this is not provided.",
)
@click.option(
    "--package-name",
    help="""
    If you are using one of the JavaScript component templates,
    you can use this flag to specify the name of the resulting package without being prompted.
    """,
)
def create(
    template: Optional[str] = None,
    mode: Optional[str] = None,
    github: Optional[str] = None,
    dir: Optional[Path | str] = None,
    package_name: Optional[str] = None,
) -> None:
    from ._create import use_github_template, use_internal_template

    if dir is not None:
        dir = Path(dir)

    if github is not None:
        use_github_template(
            github,
            template_name=template,
            mode=mode,
            dest_dir=dir,
            package_name=package_name,
        )
    else:
        use_internal_template(template, mode, dir, package_name)
