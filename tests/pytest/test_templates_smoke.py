"""Load every bundled app template without keys, network, or a browser.

`shiny create` copies `shiny/templates/` verbatim, so a template that raises
on import is a broken first run for a new user. Nothing else in CI imports
these files (see posit-dev/py-shiny#2488), where five chat templates shipped
a `Chat(messages=...)` call that raised on startup.

Each template entrypoint must therefore build its `shiny.App` with dummy
credentials and stubbed optional LLM providers. The test runs the UI phase
only: server callbacks never execute, so no key or model server is needed.
"""

from __future__ import annotations

import ast
import importlib.util
import re
import sys
import textwrap
import traceback
import types
from collections.abc import Iterator
from operator import attrgetter
from pathlib import Path

import pytest

from shiny._app import App
from shiny._main._create import find_templates
from shiny.express import wrap_express_app

REPO_ROOT = Path(__file__).parents[2]
TEMPLATE_ROOT = REPO_ROOT / "shiny" / "templates"
SKILL_REFERENCES = (
    REPO_ROOT / "shiny" / ".agents" / "skills" / "shiny-for-python" / "references"
)

# Credentials are never used: server callbacks do not run during this test.
# Dummy values get past constructor-time validation (e.g. ChatAzureOpenAI).
DUMMY_ENV_VARS = {
    "OPENAI_API_KEY": "dummy",
    "ANTHROPIC_API_KEY": "dummy",
    "GOOGLE_API_KEY": "dummy",
    "AZURE_OPENAI_API_KEY": "dummy",
}

# Modules purged from `sys.modules` around each template load. Sibling helpers
# (`app_utils`, `shared`) share names across template directories, so a cached
# copy from one template would leak into the next.
_PURGED_HELPERS = {"app_utils", "shared", "globals"}

# Third-party packages a template may import. A template that fails only
# because one of these is missing is untestable here, so the test skips it.
# Anything else missing (a typo'd helper name, a deleted sibling file) is a
# template bug and must fail, so the allowlist stays exactly this set.
_OPTIONAL_TEMPLATE_DEPS = frozenset(
    {
        "chatlas",
        "dotenv",
        "faicons",
        "langchain_openai",
        "pandas",
        "plotly",
        "seaborn",
        "shinywidgets",
    }
)

# Provider constructors are stubbed, not real. Their validation behavior changes
# across chatlas releases (newer versions query the model server and require
# provider packages at construction time), so real constructors make this test
# depend on upstream behavior, installed packages, and local servers. The
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


class _DummyChatClient:
    """Stand-in for an LLM provider client (never called, only constructed)."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    async def stream_async(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError  # pragma: no cover

    def stream(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError  # pragma: no cover


def _noop_load_dotenv(*args: object, **kwargs: object) -> bool:
    return False


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

    if importlib.util.find_spec("dotenv") is None:
        dotenv_stub = types.ModuleType("dotenv")
        # `app_utils.load_dotenv` calls `dotenv.load_dotenv(...)` and warns
        # when the import fails. The stub keeps the call a no-op instead.
        dotenv_stub.__dict__["load_dotenv"] = _noop_load_dotenv
        monkeypatch.setitem(sys.modules, "dotenv", dotenv_stub)


@pytest.fixture
def _isolated_template_modules():
    """Drop cached sibling helpers so each template loads its own copy."""
    for name in _PURGED_HELPERS:
        sys.modules.pop(name, None)
    yield
    for name in _PURGED_HELPERS:
        sys.modules.pop(name, None)


def _template_import_lines(path: Path) -> set[int]:
    """Line numbers of top-level `import` statements in a template file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    }


def _iter_causes(exc: BaseException) -> Iterator[BaseException]:
    """An exception and everything it was raised from (`__cause__`, `__context__`)."""
    seen: set[int] = set()
    stack: list[BaseException] = [exc]
    while stack:
        current = stack.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        yield current
        for nxt in (current.__cause__, current.__context__):
            if isinstance(nxt, BaseException):
                stack.append(nxt)


def _fails_at_template_import(path: Path, exc: BaseException) -> bool:
    """Did the template fail inside a third-party import?

    True when the template's own frame sits on an `import` line and no other
    template-side file (a sibling helper such as `shared.py`) is on the
    traceback. That combination says the dependency is unusable in this
    environment -- a version floor that no longer imports cleanly, for
    example -- not that the template is wrong. Anything else (a bad
    `Chat(...)` call, a helper that raises while loading data) is a template
    bug and must fail.

    Express wraps load errors in `RuntimeError`, so walk the whole cause
    chain instead of only the outer traceback.
    """
    try:
        import_lines = _template_import_lines(path)
    except SyntaxError:
        return False
    resolved = path.resolve()
    template_dir = resolved.parent
    saw_import_frame = False
    for cause in _iter_causes(exc):
        for frame in traceback.extract_tb(cause.__traceback__):
            frame_path = Path(frame.filename).resolve()
            if frame_path == resolved:
                if frame.lineno not in import_lines:
                    return False
                saw_import_frame = True
            elif template_dir in frame_path.parents and frame_path.suffix == ".py":
                # A sibling helper raised: template-side bug, not an env issue.
                return False
    return saw_import_frame


def _skip_reason(path: Path, exc: BaseException) -> str | None:
    """Why this template failure is an environment issue, or `None` to fail.

    Skips stay narrow on purpose: a missing allowlisted package, or an error
    raised inside a third-party import. A typo'd helper name, a bad
    from-import, or helper code that raises all return `None` and fail.
    """
    if isinstance(exc, ModuleNotFoundError):
        missing_root = (exc.name or "").split(".")[0]
        if missing_root in _OPTIONAL_TEMPLATE_DEPS:
            return f"Template needs an optional dependency: {exc}"
        return None
    if isinstance(exc, ImportError) and "cannot import name" in str(exc):
        # The source module resolved, so the imported name is wrong -- a typo
        # in the template or a helper, not a missing package.
        return None
    if _fails_at_template_import(path, exc):
        return f"Template dependency is unusable in this env: {exc}"
    return None


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
    try:
        if path.name == "app-core.py":
            _load_core_app(path)
        else:
            app = wrap_express_app(path.resolve())
            assert isinstance(app, App), f"{path} did not build a shiny App"
    except Exception as e:
        reason = _skip_reason(path, e)
        if reason is not None:
            pytest.skip(reason)
        raise


def _write_app(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "app.py"
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


def _exec_app(path: Path) -> BaseException:
    try:
        exec(
            compile(path.read_text(encoding="utf-8"), str(path), "exec"),
            {"__file__": str(path), "__name__": "__main__"},
        )
    except Exception as e:
        return e
    raise AssertionError(f"{path} did not raise")


def test_skip_reason_unknown_module_fails(tmp_path: Path) -> None:
    # A typo'd helper name must fail, not skip.
    path = _write_app(tmp_path, "from app_util import load_dotenv\n")
    exc = ModuleNotFoundError("No module named 'app_util'", name="app_util")
    assert _skip_reason(path, exc) is None


def test_skip_reason_allowlisted_module_skips(tmp_path: Path) -> None:
    path = _write_app(tmp_path, "import seaborn\n")
    exc = ModuleNotFoundError("No module named 'seaborn'", name="seaborn")
    assert _skip_reason(path, exc) is not None


def test_skip_reason_nameless_module_fails(tmp_path: Path) -> None:
    path = _write_app(tmp_path, "import seaborn\n")
    assert _skip_reason(path, ModuleNotFoundError("boom")) is None


def test_skip_reason_bad_from_import_fails(tmp_path: Path) -> None:
    # The source module resolved, so the name is wrong -- a template typo.
    (tmp_path / "shared.py").write_text("x = 1\n", encoding="utf-8")
    path = _write_app(tmp_path, "from shared import dff\n")
    exc = _exec_app(path)
    assert isinstance(exc, ImportError)
    assert _skip_reason(path, exc) is None


def test_skip_reason_broken_dependency_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The import itself raises deep inside third-party code: env issue.
    # The broken package lives outside the template dir, like site-packages.
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    dep_dir = tmp_path / "deps"
    dep_dir.mkdir()
    (dep_dir / "brokenlib.py").write_text(
        'raise AttributeError("old lib vs new numpy")\n', encoding="utf-8"
    )
    monkeypatch.setattr(sys, "path", [str(dep_dir), *sys.path])
    path = _write_app(app_dir, "import brokenlib\n")
    exc = _exec_app(path)
    assert isinstance(exc, AttributeError)
    assert _skip_reason(path, exc) is not None


def test_skip_reason_helper_error_fails(tmp_path: Path) -> None:
    # A sibling helper that raises (a missing data file, for example) is a
    # template bug even though the template frame sits on an import line.
    (tmp_path / "shared.py").write_text(
        "raise RuntimeError('no data')\n", encoding="utf-8"
    )
    path = _write_app(tmp_path, "from shared import df\n")
    exc = _exec_app(path)
    assert _skip_reason(path, exc) is None


def test_skip_reason_template_code_error_fails(tmp_path: Path) -> None:
    path = _write_app(tmp_path, "import json\nundefined_name\n")
    exc = _exec_app(path)
    assert _skip_reason(path, exc) is None


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
