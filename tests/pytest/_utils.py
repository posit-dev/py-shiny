from __future__ import annotations

import sys
from typing import Any, Callable, TypeVar

import pytest

CallableT = TypeVar("CallableT", bound=Callable[..., Any])


def skip_on_windows(fn: CallableT) -> CallableT:
    fn = pytest.mark.skipif(
        sys.platform.startswith("win"),
        reason="Does not run on windows",
    )(fn)

    return fn
