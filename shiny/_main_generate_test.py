from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable

import click
import questionary

from ._main_utils import cli_action, cli_bold, cli_code, path_rel_wd


class ValidationError(Exception):
    pass


def create_file_validator(
    file_type: str,
    must_exist: bool = True,
    prefix_required: str | None = None,
    must_not_exist: bool = False,
) -> Callable[[str], bool | str]:
    def validator(path_str: str) -> bool | str:
        if not isinstance(path_str, (str, Path)):
            return False

        path = Path(path_str)

        if path.is_dir():
            return f"Please provide a file path for your {file_type}"

        if must_exist and not path.exists():
            return f"{file_type.title()} file not found: {path_str}"

        if must_not_exist and path.exists():
            return f"{file_type.title()} file already exists. Please provide a new file name."

        if prefix_required and not path.name.startswith(prefix_required):
            return f"{file_type.title()} file must start with '{prefix_required}'"

        return True

    return validator


def validate_api_key(provider: str) -> None:
    api_configs = {
        "anthropic": {
            "env_var": "ANTHROPIC_API_KEY",
            "url": "https://console.anthropic.com/",
        },
        "openai": {
            "env_var": "OPENAI_API_KEY",
            "url": "https://platform.openai.com/api-keys",
        },
    }

    if provider not in api_configs:
        raise ValidationError(f"Unsupported provider: {provider}")

    config = api_configs[provider]
    if not os.getenv(config["env_var"]):
        raise ValidationError(
            f"{config['env_var']} environment variable is not set.\n"
            f"Please set your {provider.title()} API key:\n"
            f"  export {config['env_var']}='your-api-key-here'\n\n"
            f"Get your API key from: {config['url']}"
        )


def get_app_file_path(app_file: str | None) -> Path:
    if app_file is not None:
        app_path = Path(app_file)
        if not app_path.exists():
            raise ValidationError(f"App file does not exist: {app_path}")
        return app_path
    # Interactive mode
    app_file_val = questionary.path(
        "Enter the path to the app file:",
        default=path_rel_wd("app.py"),
        validate=create_file_validator("Shiny app", must_exist=True),
    ).ask()

    if app_file_val is None:
        sys.exit(1)

    return Path(app_file_val)


def get_output_file_path(output_file: str | None, app_path: Path) -> Path:
    if output_file is not None:
        output_path = Path(output_file)
        if output_path.exists():
            raise ValidationError(f"Test file already exists: {output_path}")
        if not output_path.name.startswith("test_"):
            raise ValidationError("Test file must start with 'test_'")
        return output_path
    # Interactive mode
    suggested_output = app_path.parent / f"test_{app_path.stem}.py"

    output_file_val = questionary.path(
        "Enter the path for the generated test file:",
        default=str(suggested_output),
        validate=create_file_validator(
            "test", must_exist=False, prefix_required="test_", must_not_exist=True
        ),
    ).ask()

    if output_file_val is None:
        sys.exit(1)

    return Path(output_file_val)


def generate_test_file(
    *,
    app_file: str | None,
    output_file: str | None,
    provider: str,
    model: str | None,
) -> None:

    try:
        validate_api_key(provider)

        app_path = get_app_file_path(app_file)
        output_path = get_output_file_path(output_file, app_path)

        try:
            from .pytest._generate import ShinyTestGenerator
        except ImportError as e:
            raise ValidationError(
                f"Could not import ShinyTestGenerator: {e}\n"
                "Make sure the shiny testing dependencies are installed."
            )

        click.echo(f"🤖 Generating test using {provider} provider...")
        if model:
            click.echo(f"📝 Using model: {model}")

        generator = ShinyTestGenerator(provider=provider, setup_logging=False)  # type: ignore
        _, test_file_path = generator.generate_test_from_file(
            app_file_path=str(app_path),
            model=model,
            output_file=str(output_path),
        )

        relative_test_file_path = test_file_path.relative_to(Path.cwd())

        click.echo(f"✅ Test file generated successfully: {relative_test_file_path}")
        click.echo()
        click.echo(cli_action(cli_bold("Next steps:")))
        click.echo(
            f"- Run {cli_code('pytest ' + str(relative_test_file_path))} to run the generated test"
        )
        click.echo("- Review and customize the test as needed")

    except ValidationError as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error generating test: {e}")
        sys.exit(1)
