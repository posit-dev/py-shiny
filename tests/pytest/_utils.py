from __future__ import annotations

import re
import sys
from typing import Any, Callable, Optional, TypeVar

import pytest

CallableT = TypeVar("CallableT", bound=Callable[..., Any])


def skip_on_windows(fn: CallableT) -> CallableT:
    fn = pytest.mark.skipif(
        sys.platform.startswith("win"),
        reason="Does not run on windows",
    )(fn)

    return fn


def skip_on_python_version(
    version: str,
    reason: Optional[str] = None,
) -> Callable[[CallableT], CallableT]:

    reason_str = reason or f"Do not run on python {version}"

    is_valid_version = (
        re.match(r"\d+", version)
        or re.match(r"\d+\.\d+", version)
        or re.match(r"\d+\.\d+\.\d+", version)
    ) is not None

    assert is_valid_version

    def _(fn: CallableT) -> CallableT:

        versions_match = True
        for i, v in enumerate(version.split(".")):
            if sys.version_info[i] != int(v):
                versions_match = False
                break

        fn = pytest.mark.skipif(
            versions_match,
            reason=reason_str,
        )(fn)

        return fn

    def _(fn: CallableT) -> CallableT:
        fn = pytest.mark.skipif(
            sys.platform.startswith("win"),
            reason="Does not run on windows",
        )(fn)

        return fn

    return _
