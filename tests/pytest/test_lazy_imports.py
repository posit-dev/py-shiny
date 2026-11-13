"""Guard the PEP 810 lazy-import declarations for Python 3.15+.

``__lazy_modules__`` is ignored on Python 3.14 and older, so startup-heavy
modules (``shinychat``, ``narwhals``, the CLI stack) are only deferred when the
interpreter supports PEP 810. These tests pin both halves of the contract: the
deferral, and reification on first use. If someone adds an eager import back
into one of these import paths, the deferral test fails here instead of
silently costing every Python 3.15 user the load time.

Each check runs in a fresh subprocess, because ``sys.modules`` in the test
process is already polluted by earlier tests.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 15),
    reason="Lazy imports (PEP 810) require Python 3.15+",
)


def run_python(code: str) -> None:
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_import_shiny_defers_heavy_modules() -> None:
    run_python("""
import sys
import shiny

heavy = [
    "shiny._main",
    "shinychat",
    "narwhals",
    "questionary",
    "prompt_toolkit",
    "uvicorn",
    "watchfiles",
]
loaded = [name for name in heavy if name in sys.modules]
assert not loaded, f"eagerly imported: {loaded}"
""")


def test_heavy_modules_reify_on_first_use() -> None:
    run_python("""
import sys
import shiny

assert "shinychat" not in sys.modules
_ = shiny.ui.Chat
assert "shinychat" in sys.modules

assert "narwhals" not in sys.modules
_ = shiny.render.text
assert "narwhals" in sys.modules

assert "shiny._main" not in sys.modules
_ = shiny.run_app
assert "shiny._main" in sys.modules
""")


def test_express_ui_defers_shinychat() -> None:
    run_python("""
import sys
from shiny.express import ui

assert "shinychat" not in sys.modules
_ = ui.Chat
assert "shinychat" in sys.modules
""")
