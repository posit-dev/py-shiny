"""Guard the chat API floor and deprecated calls used by bundled templates.

Template startup and browser errors are covered in the Playwright example suite.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from htmltools import Tag

from shiny.express import ui
from shiny.express._run import ExpressStubSession
from shiny.session import session_context
from shiny.types import Jsonifiable

REPO_ROOT = Path(__file__).parents[2]
TEMPLATE_ROOT = REPO_ROOT / "shiny" / "templates"
SKILL_REFERENCES = (
    REPO_ROOT / "shiny" / ".agents" / "skills" / "shiny-for-python" / "references"
)


class _StubBookmarkClient:
    """Minimal `ClientWithState`, never touched under a stub session."""

    async def get_state(self) -> Jsonifiable:
        return {}

    async def set_state(self, state: object) -> None:
        pass


def test_minimum_shinychat_api() -> None:
    """The shinychat API surface the chat templates rely on.

    This guard runs in oldest-deps: it fails if the installed shinychat floor drops the
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
