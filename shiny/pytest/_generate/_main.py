import importlib.resources
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Tuple, Union

from chatlas import ChatAnthropic, ChatOpenAI
from dotenv import load_dotenv

__all__ = [
    "ShinyTestGenerator",
]


@dataclass
class Config:
    """Configuration class for ShinyTestGenerator"""

    # Model aliases for both providers
    MODEL_ALIASES = {
        # Anthropic models
        "haiku3.5": "claude-3-5-haiku-20241022",
        "sonnet": "claude-sonnet-4-20250514",
        # OpenAI models
        "gpt-5": "gpt-5-2025-08-07",
        "gpt-5-mini": "gpt-5-mini-2025-08-07",
        "o4-mini": "o4-mini-2025-04-16",
        "gpt-5-nano": "gpt-5-nano-2025-08-07",
    }

    DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
    DEFAULT_OPENAI_MODEL = "gpt-5-mini-2025-08-07"
    DEFAULT_PROVIDER = "anthropic"

    MAX_TOKENS = 8092
    LOG_FILE = "llm_test_generator.log"
    COMMON_APP_PATTERNS = ["app.py", "app_*.py"]


class ShinyTestGenerator:
    CODE_PATTERN = re.compile(r"```python(.*?)```", re.DOTALL)

    def __init__(
        self,
        provider: Literal["anthropic", "openai"] = Config.DEFAULT_PROVIDER,
        api_key: Optional[str] = None,
        log_file: str = Config.LOG_FILE,
        setup_logging: bool = True,
    ):
        """
        Initialize the ShinyTestGenerator.
        """
        self.provider = provider
        self._client = None
        self._documentation = None
        self._system_prompt = None
        self.api_key = api_key
        self.log_file = log_file

        if setup_logging:
            self.setup_logging()

    @property
    def client(self) -> Union[ChatAnthropic, ChatOpenAI]:
        """Lazy-loaded chat client based on provider"""
        if self._client is None:
            if self.provider == "anthropic":
                self._client = (
                    ChatAnthropic(api_key=self.api_key)
                    if self.api_key
                    else ChatAnthropic()
                )
            elif self.provider == "openai":
                self._client = (
                    ChatOpenAI(api_key=self.api_key) if self.api_key else ChatOpenAI()
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        return self._client

    @property
    def documentation(self) -> str:
        """Lazy-loaded documentation"""
        if self._documentation is None:
            self._documentation = self._load_documentation()
        return self._documentation

    @property
    def system_prompt(self) -> str:
        """Lazy-loaded system prompt"""
        if self._system_prompt is None:
            self._system_prompt = self._read_system_prompt()
        return self._system_prompt

    @property
    def default_model(self) -> str:
        """Get default model for current provider"""
        if self.provider == "anthropic":
            return Config.DEFAULT_ANTHROPIC_MODEL
        elif self.provider == "openai":
            return Config.DEFAULT_OPENAI_MODEL
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    @staticmethod
    def setup_logging():
        load_dotenv()
        logging.basicConfig(
            filename=Config.LOG_FILE,
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def _load_documentation(self) -> str:
        """Load documentation from package resources"""
        try:
            doc_path = (
                importlib.resources.files("shiny.pytest._generate")
                / "_data"
                / "_docs"
                / "documentation_testing.json"
            )
            with doc_path.open("r") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                "Documentation file not found for app type: testing"
            )

    def _read_system_prompt(self) -> str:
        """Read and combine system prompt with documentation"""
        try:
            prompt_path = (
                importlib.resources.files("shiny.pytest._generate")
                / "_data"
                / "_prompts"
                / "SYSTEM_PROMPT_testing.md"
            )
            with prompt_path.open("r") as f:
                system_prompt_file = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                "System prompt file not found for app type: testing"
            )

        return f"{system_prompt_file}\n\nHere is the function reference documentation for Shiny for Python: {self.documentation}"

    def _resolve_model(self, model: str) -> str:
        """Resolve model alias to actual model name"""
        return Config.MODEL_ALIASES.get(model, model)

    def _validate_model_for_provider(self, model: str) -> str:
        """Validate that the model is compatible with the current provider"""
        resolved_model = self._resolve_model(model)

        # Check if model is appropriate for provider
        if self.provider == "anthropic":
            if resolved_model.startswith("gpt-") or resolved_model.startswith("o1-"):
                raise ValueError(
                    f"Model '{model}' is an OpenAI model but provider is set to 'anthropic'. "
                    f"Either use an Anthropic model or switch provider to 'openai'."
                )
        elif self.provider == "openai":
            if resolved_model.startswith("claude-"):
                raise ValueError(
                    f"Model '{model}' is an Anthropic model but provider is set to 'openai'. "
                    f"Either use an OpenAI model or switch provider to 'anthropic'."
                )

        return resolved_model

    def get_llm_response(self, prompt: str, model: Optional[str] = None) -> str:
        """Get response from LLM using the configured provider"""
        if model is None:
            model = self.default_model
        else:
            model = self._validate_model_for_provider(model)

        try:
            # Create chat client with the specified model
            if self.provider == "anthropic":
                chat = ChatAnthropic(
                    model=model,
                    system_prompt=self.system_prompt,
                    max_tokens=Config.MAX_TOKENS,
                    api_key=self.api_key,
                )
            elif self.provider == "openai":
                chat = ChatOpenAI(
                    model=model,
                    system_prompt=self.system_prompt,
                    api_key=self.api_key,
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            response = chat.chat(prompt)

            if hasattr(response, "content"):
                return response.content
            elif hasattr(response, "text"):
                return response.text
            else:
                return str(response)
        except Exception as e:
            logging.error(f"Error getting LLM response from {self.provider}: {e}")
            raise

    def extract_test(self, response: str) -> str:
        """Extract test code using pre-compiled regex pattern"""
        match = self.CODE_PATTERN.search(response)
        return match.group(1).strip() if match else ""

    def _compute_relative_app_path(
        self, app_file_path: Path, test_file_path: Path
    ) -> str:
        """Compute POSIX-style relative path from the test file directory to the app file."""
        # Make sure both paths are absolute
        app_file_abs = app_file_path.resolve()
        test_file_abs = test_file_path.resolve()

        # Compute relative path from test file directory to app file
        rel = os.path.relpath(str(app_file_abs), start=str(test_file_abs.parent))
        return Path(rel).as_posix()

    def _rewrite_fixture_path(self, test_code: str, relative_app_path: str) -> str:
        """Rewrite create_app_fixture path to be relative to the test file directory.

        Handles common patterns like:
        - create_app_fixture(["app.py"]) -> create_app_fixture(["../app.py"]) (or appropriate)
        - create_app_fixture("app.py") -> create_app_fixture("../app.py")
        Keeps other arguments intact if present.
        """
        logging.debug(f"Rewriting fixture path to: {relative_app_path}")

        # First check if create_app_fixture exists in the code
        if "create_app_fixture" not in test_code:
            logging.warning("No create_app_fixture found in generated test code")
            return test_code

        # Pattern for list form: create_app_fixture(["app.py"]) or with spaces
        pattern_list = re.compile(
            r"(create_app_fixture\(\s*\[\s*)(['\"])([^'\"]+)(\\2)(\\s*)([,\]])",
            re.DOTALL,
        )

        def repl_list(m: re.Match) -> str:
            logging.debug(
                f"Replacing list form: '{m.group(3)}' with '{relative_app_path}'"
            )
            return f"{m.group(1)}{m.group(2)}{relative_app_path}{m.group(2)}{m.group(5)}{m.group(6)}"

        new_code, list_count = pattern_list.subn(repl_list, test_code)

        if list_count > 0:
            logging.debug(f"Replaced {list_count} list-form fixture path(s)")

        # Pattern for direct string form: create_app_fixture("app.py")
        pattern_str = re.compile(
            r"(create_app_fixture\(\s*)(['\"])([^'\"]+)(\\2)(\\s*)([,\)])",
            re.DOTALL,
        )

        def repl_str(m: re.Match) -> str:
            logging.debug(
                f"Replacing string form: '{m.group(3)}' with '{relative_app_path}'"
            )
            return f"{m.group(1)}{m.group(2)}{relative_app_path}{m.group(2)}{m.group(5)}{m.group(6)}"

        new_code2, str_count = pattern_str.subn(repl_str, new_code)

        if str_count > 0:
            logging.debug(f"Replaced {str_count} string-form fixture path(s)")

        # If no replacements were made, there might be a pattern we're not catching
        if list_count == 0 and str_count == 0:
            logging.warning(
                f"Found create_app_fixture but couldn't replace path. Code snippet: {test_code[:200]}..."
            )

            # Fallback regex with more generous pattern matching
            fallback_pattern = re.compile(
                r"(create_app_fixture\([^\)]*?['\"])([^'\"]+)(['\"][^\)]*?\))",
                re.DOTALL,
            )

            def fallback_repl(m: re.Match) -> str:
                logging.debug(
                    f"Fallback replacement: '{m.group(2)}' with '{relative_app_path}'"
                )
                return f"{m.group(1)}{relative_app_path}{m.group(3)}"

            new_code2, fallback_count = fallback_pattern.subn(fallback_repl, new_code)

            if fallback_count > 0:
                logging.debug(f"Fallback replaced {fallback_count} fixture path(s)")

        return new_code2

    def _create_test_prompt(self, app_text: str, app_file_name: str) -> str:
        """Create test generation prompt with app file name"""
        return (
            f"Given this Shiny for Python app code from file '{app_file_name}':\n{app_text}\n"
            "Please only add controllers for components that already have an ID in the shiny app.\n"
            "Do not add tests for ones that do not have an existing ids since controllers need IDs to locate elements.\n"
            "and server functionality of this app. Include appropriate assertions \\n"
            "and test cases to verify the app's behavior.\n\n"
            "CRITICAL: In the create_app_fixture call, you MUST pass a RELATIVE path from the test file's directory to the app file.\n"
            "For example:\n"
            "- If test is in 'tests/test_app.py' and app is in 'app.py', use: '../app.py'\n"
            "- If test is in 'tests/subdir/test_app.py' and app is in 'apps/subdir/app.py', use: '../../apps/subdir/app.py'\n"
            "- Always compute the correct relative path from the test file to the app file\n"
            "- NEVER use absolute paths or paths that aren't relative from the test location\n\n"
            "IMPORTANT: Only output the Python test code in a single code block. Do not include any explanation, justification, or extra text."
        )

    def _infer_app_file_path(
        self, app_code: Optional[str] = None, app_file_path: Optional[str] = None
    ) -> Path:
        if app_file_path:
            # Return absolute path to avoid any ambiguity
            return Path(app_file_path).resolve()

        current_dir = Path.cwd()

        found_files = []
        for pattern in Config.COMMON_APP_PATTERNS:
            found_files.extend(current_dir.glob(pattern))

        if found_files:
            # Return absolute path of found file
            return found_files[0].resolve()

        if app_code:
            # For inferred app paths, use absolute path in current directory
            return Path("inferred_app.py").resolve()

        raise FileNotFoundError(
            "Could not infer app file path. Please provide app_file_path parameter."
        )

    def _generate_test_file_path(
        self, app_file_path: Path, output_dir: Optional[Path] = None
    ) -> Path:
        output_dir = output_dir or app_file_path.parent
        test_file_name = f"test_{app_file_path.stem}.py"
        # Return absolute path for test file
        return (output_dir / test_file_name).resolve()

    def generate_test(
        self,
        app_code: Optional[str] = None,
        app_file_path: Optional[str] = None,
        app_name: str = "app",
        model: Optional[str] = None,
        output_file: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> Tuple[str, Path]:
        if app_code and not app_file_path:
            inferred_app_path = Path(f"{app_name}.py")
        else:
            inferred_app_path = self._infer_app_file_path(app_code, app_file_path)

        if app_code is None:
            if not inferred_app_path.exists():
                raise FileNotFoundError(f"App file not found: {inferred_app_path}")
            app_code = inferred_app_path.read_text(encoding="utf-8")

        user_prompt = self._create_test_prompt(app_code, inferred_app_path.name)
        response = self.get_llm_response(user_prompt, model)
        test_code = self.extract_test(response)

        if output_file:
            test_file_path = Path(output_file)
        else:
            output_dir_path = Path(output_dir) if output_dir else None
            test_file_path = self._generate_test_file_path(
                inferred_app_path, output_dir_path
            )

        try:
            # Log the paths for debugging
            logging.info(f"App file path: {inferred_app_path}")
            logging.info(f"Test file path: {test_file_path}")

            relative_app_path = self._compute_relative_app_path(
                inferred_app_path, test_file_path
            )

            logging.info(f"Computed relative path: {relative_app_path}")

            # Explicitly check for app.py - this is a common problematic case
            if relative_app_path == "app.py" and "../" not in relative_app_path:
                logging.warning(
                    f"Detected possibly incorrect relative path: {relative_app_path}"
                )
                # Force a proper relative path if needed
                if test_file_path.parent != inferred_app_path.parent:
                    logging.info(
                        "Test and app are in different directories, adjusting relative path"
                    )
                    relative_app_path = f"../{relative_app_path}"
                    logging.info(f"Adjusted relative path: {relative_app_path}")

            test_code = self._rewrite_fixture_path(test_code, relative_app_path)
        except Exception as e:
            logging.error(f"Error computing relative path: {e}")
            # Don't silently ignore - use the best path we can
            try:
                # Fallback: just use the absolute path as string if we can't compute relative
                logging.warning("Falling back to using absolute path in test file")
                test_code = self._rewrite_fixture_path(
                    test_code, str(inferred_app_path.resolve())
                )
            except Exception as e2:
                logging.error(f"Error in fallback path handling: {e2}")

        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        test_file_path.write_text(test_code, encoding="utf-8")

        return test_code, test_file_path

    def generate_test_from_file(
        self,
        app_file_path: str,
        model: Optional[str] = None,
        output_file: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> Tuple[str, Path]:
        return self.generate_test(
            app_file_path=app_file_path,
            model=model,
            output_file=output_file,
            output_dir=output_dir,
        )

    def generate_test_from_code(
        self,
        app_code: str,
        app_name: str = "app",
        model: Optional[str] = None,
        output_file: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> Tuple[str, Path]:
        return self.generate_test(
            app_code=app_code,
            app_name=app_name,
            model=model,
            output_file=output_file,
            output_dir=output_dir,
        )

    def switch_provider(
        self, provider: Literal["anthropic", "openai"], api_key: Optional[str] = None
    ):
        self.provider = provider
        if api_key:
            self.api_key = api_key
        self._client = None  # Reset client to force recreation with new provider

    @classmethod
    def create_anthropic_generator(
        cls, api_key: Optional[str] = None, **kwargs
    ) -> "ShinyTestGenerator":
        return cls(provider="anthropic", api_key=api_key, **kwargs)

    @classmethod
    def create_openai_generator(
        cls, api_key: Optional[str] = None, **kwargs
    ) -> "ShinyTestGenerator":
        return cls(provider="openai", api_key=api_key, **kwargs)

    def get_available_models(self) -> list[str]:
        if self.provider == "anthropic":
            return [
                model
                for model in Config.MODEL_ALIASES.keys()
                if not (model.startswith("gpt-") or model.startswith("o1-"))
            ]
        elif self.provider == "openai":
            return [
                model
                for model in Config.MODEL_ALIASES.keys()
                if (model.startswith("gpt-") or model.startswith("o1-"))
            ]
        else:
            return []


def cli():
    import argparse

    parser = argparse.ArgumentParser(description="Generate Shiny tests using LLM")
    parser.add_argument("app_file", help="Path to the Shiny app file")
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        default=Config.DEFAULT_PROVIDER,
        help="LLM provider to use",
    )
    parser.add_argument("--model", help="Model to use (optional)")
    parser.add_argument("--output-dir", help="Output directory for test files")
    parser.add_argument("--api-key", help="API key (optional, can use env vars)")

    args = parser.parse_args()

    app_file_path = Path(args.app_file)
    if not app_file_path.is_file():
        print(f"Error: File not found at {app_file_path}")
        sys.exit(1)

    try:
        generator = ShinyTestGenerator(provider=args.provider, api_key=args.api_key)

        test_code, test_file_path = generator.generate_test_from_file(
            str(app_file_path),
            model=args.model,
            output_dir=args.output_dir,
        )

        print(f"✅ Test file generated successfully: {test_file_path}")
        print(f"📝 Used provider: {args.provider}")
        if args.model:
            print(f"🤖 Used model: {args.model}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
