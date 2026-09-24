"""Load every bundled app template without keys, network, or a browser.

`shiny create` copies `shiny/templates/` verbatim, so a template that raises
on import is a broken first run for a new user. Nothing else in CI imports
these files (see posit-dev/py-shiny#2488), where five chat templates shipped
a `Chat(messages=...)` call that raised on startup.

Each template entrypoint must build its `shiny.App`, with LLM provider
constructors stubbed: the Shiny side stays real, server callbacks never run,
so no key or model server is needed. Any load failure fails the test; there
are no skips here. The reduced oldest-deps job exempts this file via
`SHINY_SKIP_TEMPLATE_SMOKE` (see `.github/workflows/pytest.yaml`) instead of
special-casing environments inside the test.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import re
import sys
import types
from collections.abc import Iterator
from operator import attrgetter
from pathlib import Path

import pytest
from htmltools import Tag

from shiny._app import App
from shiny._main._create import find_templates
from shiny.express import ui, wrap_express_app
from shiny.express._run import ExpressStubSession
from shiny.session import session_context
from shiny.types import Jsonifiable

REPO_ROOT = Path(__file__).parents[2]
TEMPLATE_ROOT = REPO_ROOT / "shiny" / "templates"
TEMPLATE_ROOT_RESOLVED = TEMPLATE_ROOT.resolve()
SKILL_REFERENCES = (
    REPO_ROOT / "shiny" / ".agents" / "skills" / "shiny-for-python" / "references"
)

# Credentials are never used: server callbacks do not run during this test.
DUMMY_ENV_VARS = {
    "OPENAI_API_KEY": "dummy",
    "ANTHROPIC_API_KEY": "dummy",
    "GOOGLE_API_KEY": "dummy",
    "AZURE_OPENAI_API_KEY": "dummy",
}

# Provider constructors are stubbed, not real. They reach for API keys,
# provider packages, and model servers, and their validation behavior changes
# across chatlas releases -- none of which this test should depend on. The
# Shiny side (`ui.Chat`, `chat.ui`, `enable_bookmarking`) stays real, which is
# what caught the `Chat(messages=...)` startup failure in #2488.
_LLM_CLIENT_NAMES = (
    "ChatOpenAI",
    "ChatAnthropic",
    "ChatGoogle",
    "ChatOllama",
    "ChatAzureOpenAI",
    "ChatBedrockAnthropic",
)

# Module names created while loading a template (Express app packages and
# Core test modules). Dropped afterwards; each load mints a fresh one.
_GENERATED_MODULE_PREFIXES = ("shiny_express_app_", "_template_smoke_")

requires_full_deps = pytest.mark.skipif(
    os.environ.get("SHINY_SKIP_TEMPLATE_SMOKE") == "1",
    reason="Template smoke test needs the full test dependencies.",
)


class _DummyChatClient:
    """Stand-in for an LLM provider client (never called, only constructed)."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    async def stream_async(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError  # pragma: no cover

    def stream(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError  # pragma: no cover


class _StubBookmarkClient:
    """Minimal `ClientWithState`, never touched under a stub session."""

    async def get_state(self) -> Jsonifiable:
        return {}

    async def set_state(self, state: object) -> None:
        pass


def _template_entrypoints() -> list[tuple[str, Path]]:
    """Every loadable app entrypoint as `(test id, path)` pairs."""
    cases: list[tuple[str, Path]] = []
    for template in sorted(find_templates(TEMPLATE_ROOT), key=attrgetter("id")):
        if template.type == "package":
            # Package templates ship a component scaffold, not a runnable app.
            continue
        single = template.path / "app.py"
        if single.is_file():
            cases.append((f"{template.id}/app.py", single))
            continue
        for name in ("app-core.py", "app-express.py"):
            path = template.path / name
            if path.is_file():
                cases.append((f"{template.id}/{name}", path))
    assert cases, f"No app templates found under {TEMPLATE_ROOT}"
    return cases


@pytest.fixture
def _stub_llm_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in DUMMY_ENV_VARS.items():
        monkeypatch.setenv(key, value)

    if importlib.util.find_spec("langchain_openai") is None:
        stub = types.ModuleType("langchain_openai")
        # `__dict__` assignment: `stub.ChatOpenAI = ...` fails pyright
        # (ModuleType has no such attribute) and `setattr` trips flake8-bugbear.
        stub.__dict__["ChatOpenAI"] = _DummyChatClient
        monkeypatch.setitem(sys.modules, "langchain_openai", stub)
    else:
        langchain_openai = importlib.import_module("langchain_openai")
        monkeypatch.setattr(langchain_openai, "ChatOpenAI", _DummyChatClient)

    if importlib.util.find_spec("chatlas") is not None:
        import chatlas

        for client_name in _LLM_CLIENT_NAMES:
            if hasattr(chatlas, client_name):
                monkeypatch.setattr(chatlas, client_name, _DummyChatClient)


@pytest.fixture
def _isolated_template_modules() -> Iterator[None]:
    """Drop modules a template load brings in from its own directory.

    Sibling helpers (`app_utils`, `shared`) share names across template
    directories. Purge by file location instead of by name, so a future
    helper file cannot leak state into the next template unnoticed.
    """
    before = set(sys.modules)
    yield
    for name in set(sys.modules) - before:
        if name.startswith(_GENERATED_MODULE_PREFIXES):
            sys.modules.pop(name, None)
            continue
        filename = getattr(sys.modules.get(name), "__file__", None)
        if (
            filename is not None
            and TEMPLATE_ROOT_RESOLVED in Path(filename).resolve().parents
        ):
            sys.modules.pop(name, None)


def _load_core_app(path: Path) -> App:
    module_name = f"_template_smoke_{path.parent.name}_{path.stem}".replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    app = getattr(module, "app", None)
    assert isinstance(app, App), f"{path} did not define `app` as a shiny App"
    return app


@requires_full_deps
@pytest.mark.parametrize(
    "case_id,path",
    _template_entrypoints(),
    ids=[case_id for case_id, _ in _template_entrypoints()],
)
def test_template_loads_without_keys(
    case_id: str,
    path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _stub_llm_providers: None,
    _isolated_template_modules: None,
) -> None:
    monkeypatch.setattr(sys, "path", [str(path.parent), *sys.path])
    # Evict cached modules this template directory shadows, so a stale
    # `shared` (or any future helper) from an earlier test cannot win.
    for shadowed in path.parent.glob("*.py"):
        sys.modules.pop(shadowed.stem, None)
    if path.name == "app-core.py":
        _load_core_app(path)
    else:
        app = wrap_express_app(path.resolve())
        assert isinstance(app, App), f"{path} did not build a shiny App"


def test_minimum_shinychat_api() -> None:
    """The shinychat API surface the chat templates rely on.

    The template smoke test is exempt in oldest-deps, so this guard keeps
    running there: it fails if the installed shinychat floor ever drops the
    constructor `greeting=`, `bookmark_store=` bookmarking, or the
    `on_user_submit` handler the templates use (the `shinychat>=0.5.0` floor
    in `pyproject.toml`). It needs no API key: everything runs under a stub
    session, so no callback ever executes.
    """
    with session_context(ExpressStubSession()):
        chat = ui.Chat(id="chat", greeting="Hello")
        chat.enable_bookmarking(_StubBookmarkClient(), bookmark_store="url")

        @chat.on_user_submit
        async def handle_user_input(user_input: str) -> None:
            pass

        assert isinstance(chat.ui(), Tag)


def _deprecated_messages_calls(tree: ast.AST) -> list[int]:
    """Line numbers of `Chat`/`chat_ui`/`chat.ui` calls using `messages=`."""
    lines: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_chat_constructor = (isinstance(func, ast.Name) and func.id == "Chat") or (
            isinstance(func, ast.Attribute) and func.attr in ("Chat", "chat_ui")
        )
        is_chat_ui_method = (
            isinstance(func, ast.Attribute)
            and func.attr == "ui"
            and isinstance(func.value, ast.Name)
            and func.value.id == "chat"
        )
        if not (is_chat_constructor or is_chat_ui_method):
            continue
        keywords = {kw.arg for kw in node.keywords}
        if "messages" in keywords and "history" not in keywords:
            lines.append(node.lineno)
    return lines


def test_no_deprecated_chat_messages_kwarg() -> None:
    """Fail on the exact regression from #2486: `messages=` without `history=`."""
    offenders: list[str] = []
    for path in sorted(TEMPLATE_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for lineno in _deprecated_messages_calls(
            ast.parse(path.read_text(encoding="utf-8"))
        ):
            offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}")

    fence_re = re.compile(r"```python\n(.*?)```", re.DOTALL)
    for path in sorted(SKILL_REFERENCES.glob("*.md")):
        for fence in fence_re.findall(path.read_text(encoding="utf-8")):
            try:
                tree = ast.parse(fence)
            except SyntaxError:
                continue
            for lineno in _deprecated_messages_calls(tree):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:python-fence:{lineno}")

    assert not offenders, (
        "`messages=` on a Chat call raises since shinychat 0.7.0 unless "
        f"`history=False` is also passed. Use `greeting=` instead: {offenders}"
    )
