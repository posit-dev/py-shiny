# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

import re
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Pattern, Union


class ResolvedId(str):
    def __call__(self, id: Id) -> ResolvedId:
        if isinstance(id, ResolvedId):
            return id

        validate_id(id)

        if self == "":
            return ResolvedId(id)
        else:
            return ResolvedId(self + "-" + id)


Root: ResolvedId = ResolvedId("")


Id = Union[str, ResolvedId]


def current_namespace() -> ResolvedId:
    return _current_namespace.get()


def resolve_id(id: Id) -> ResolvedId:
    """
    Resolve an ID, possibly with a module namespace.

    Parameters
    ----------
    Args
        id: An ID.

    Returns
        An ID (if in a module, this will contain a namespace prefix).
    """
    curr_ns = _current_namespace.get()
    return curr_ns(id)


# \w is a large set for unicode patterns, that's fine; we mostly want to avoid some
# special characters like space, comma, period, and especially dash
re_valid_id: Pattern[str] = re.compile("^\\.?\\w+$")


def validate_id(id: str):
    if not re_valid_id.match(id):
        raise ValueError(
            f"The string '{id}' is not a valid id; only letters, numbers, and "
            "underscore are permitted"
        )


_current_namespace: ContextVar[ResolvedId] = ContextVar(
    "current_namespace", default=Root
)


@contextmanager
def namespace_context(id: Id | None):
    namespace = resolve_id(id) if id else Root
    token: Token[ResolvedId] = _current_namespace.set(namespace)
    try:
        yield
    finally:
        _current_namespace.reset(token)
