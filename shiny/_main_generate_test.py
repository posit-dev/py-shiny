from __future__ import annotations

import sys
from pathlib import Path

import click
import questionary

from ._main_utils import cli_action, cli_bold, cli_code, path_rel_wd


def generate_test_file(
    *,
    app_file: str | None,
    output_file: str | None,
    provider: str,
    model: str | None,
):
    """Generate AI-powered test file for a Shiny app."""

    if app_file is None:

        def path_exists(x: str) -> bool | str:
            if not isinstance(x, (str, Path)):
                return False
            path = Path(x)
            if path.is_dir():
                return "Please provide a file path to your Shiny app"
            return path.exists() or f"Shiny app file can not be found: {x}"

        app_file_val = questionary.path(
            "Enter the path to the app file:",
            default=path_rel_wd("app.py"),
            validate=path_exists,
        ).ask()
    else:
        app_file_val = app_file

    if app_file_val is None:
        sys.exit(1)

    app_path = Path(app_file_val)

    if not app_path.exists():
        click.echo(f"❌ Error: App file does not exist: {app_path}")
        sys.exit(1)

    if output_file is None:
        suggested_output = app_path.parent / f"test_{app_path.stem}.py"

        def output_path_valid(x: str) -> bool | str:
            if not isinstance(x, (str, Path)):
                return False
            path = Path(x)
            if path.is_dir():
                return "Please provide a file path for your test file."
            if path.exists():
                return "Test file already exists. Please provide a new file name."
            if not path.name.startswith("test_"):
                return "Test file must start with 'test_'"
            return True

        output_file_val = questionary.path(
            "Enter the path for the generated test file:",
            default=str(suggested_output),
            validate=output_path_valid,
        ).ask()
    else:
        output_file_val = output_file

    if output_file_val is None:
        sys.exit(1)

    output_path = Path(output_file_val)

    if output_path.exists():
        click.echo(f"❌ Error: Test file already exists: {output_path}")
        sys.exit(1)

    if not output_path.name.startswith("test_"):
        click.echo("❌ Error: Test file must start with 'test_'")
        sys.exit(1)

    try:
        from .testing import ShinyTestGenerator
    except ImportError as e:
        click.echo(f"❌ Error: Could not import ShinyTestGenerator: {e}")
        click.echo("Make sure the shiny testing dependencies are installed.")
        sys.exit(1)

    import os

    if provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            click.echo("❌ Error: ANTHROPIC_API_KEY environment variable is not set.")
            click.echo("Please set your Anthropic API key:")
            click.echo("  export ANTHROPIC_API_KEY='your-api-key-here'")
            click.echo()
            click.echo("Get your API key from: https://console.anthropic.com/")
            sys.exit(1)
    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            click.echo("❌ Error: OPENAI_API_KEY environment variable is not set.")
            click.echo("Please set your OpenAI API key:")
            click.echo("  export OPENAI_API_KEY='your-api-key-here'")
            click.echo()
            click.echo("Get your API key from: https://platform.openai.com/api-keys")
            sys.exit(1)

    click.echo(f"🤖 Generating test using {provider} provider...")
    if model:
        click.echo(f"📝 Using model: {model}")

    try:
        generator = ShinyTestGenerator(provider=provider)  # type: ignore

        # Generate the test
        _, test_file_path = generator.generate_test_from_file(
            app_file_path=str(app_path),
            model=model,
            output_file=str(output_path),
        )

        click.echo(f"✅ Test file generated successfully: {test_file_path}")
        click.echo()
        click.echo(cli_action(cli_bold("Next steps:")))
        click.echo(
            f"- Run {cli_code('pytest ' + str(test_file_path))} to run the generated test"
        )
        click.echo("- Review and customize the test as needed")

    except Exception as e:
        click.echo(f"❌ Error generating test: {e}")
        sys.exit(1)
