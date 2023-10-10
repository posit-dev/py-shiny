from __future__ import annotations

from ..._typing_extensions import TypeGuard


def is_01_scalar(x: object) -> TypeGuard[float]:
    return isinstance(x, (int, float)) and x >= 0.0 and x <= 1.0
