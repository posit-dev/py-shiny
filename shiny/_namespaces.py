from __future__ import annotations

import re
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Generator, Pattern, Union, overload


class ResolvedId(str):
    _sep: str = "-"  # Shared object for all instances

    def __call__(self, id: Id) -> ResolvedId:
        if isinstance(id, ResolvedId):
            return id

        validate_id(id)

        if self == "":
            return ResolvedId(id)
        else:
            return ResolvedId(str(self) + self._sep + id)


Root: ResolvedId = ResolvedId("")


Id = Union[str, ResolvedId]


def current_namespace() -> ResolvedId:
    return _current_namespace.get() or _default_namespace


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
    curr_ns = current_namespace()
    return curr_ns(id)


@overload
def resolve_id_or_none(id: None) -> None: ...


@overload
def resolve_id_or_none(id: Id) -> ResolvedId: ...


# Do not export this method from `shiny`. Let developers handle it themselves.
def resolve_id_or_none(id: Id | None) -> ResolvedId | None:
    """
    Resolve an ID, possibly with a module namespace. With `None` support.

    This method should only be used if `None` values are allowed. If not, use `resolve_id(id=)`.

    Parameters
    ----------
    Args
        id: An ID or `None`.

    Returns
        If `id=None`, then `None`. Otherwise, an ID (if in a module, this will contain a namespace prefix).
    """
    if id is None:
        return None
    return resolve_id(id)


# \w is a large set for unicode patterns, that's fine; we mostly want to avoid some
# special characters like space, comma, period, and especially dash
re_valid_id: Pattern[str] = re.compile("^\\.?\\w+$")


def validate_id(id: str) -> None:
    if not isinstance(id, str):
        raise ValueError("`id` must be a single string")
    if id == "":
        raise ValueError("`id` must be a non-empty string")
    if not re_valid_id.match(id):
        raise ValueError(
            f"The string '{id}' is not a valid id; only letters, numbers, and "
            "underscore are permitted"
        )


_current_namespace: ContextVar[ResolvedId | None] = ContextVar(
    "current_namespace", default=None
)
_default_namespace: ResolvedId = Root


@contextmanager
def namespace_context(id: Id | None) -> Generator[None, None, None]:
    namespace = resolve_id(id) if id else Root
    token: Token[ResolvedId | None] = _current_namespace.set(namespace)
    try:
        yield
    finally:
        _current_namespace.reset(token)
