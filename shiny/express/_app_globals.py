from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from ..session import session_context

__all__ = ("app_globals",)


@contextmanager
def app_globals() -> Generator[None, None, None]:
    with session_context(None):
        yield
