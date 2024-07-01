from __future__ import annotations

from typing import Callable, TypeVar, cast

from ..._typing_extensions import TypeGuard
from ...types import ListOrTuple

T = TypeVar("T")


def to_tuple_or_none[
    T
](x: T | ListOrTuple[T] | None, is_instance: Callable[[object], TypeGuard[T]]) -> (
    tuple[T, ...] | None
):
    if x is None:
        return None
    if is_instance(x):
        return (x,)

    assert isinstance(x, (list, tuple))
    x = tuple(cast(ListOrTuple[T], x))
    for i in x:
        assert is_instance(i)
    return x


def is_int(x: object) -> TypeGuard[int]:
    return isinstance(x, int)


def to_int_tuple_or_none(x: int | ListOrTuple[int] | None) -> tuple[int, ...] | None:
    return to_tuple_or_none(x, is_int)


def is_bool(x: object) -> TypeGuard[bool]:
    return isinstance(x, bool)


def to_bool_tuple_or_none(
    x: bool | ListOrTuple[bool] | None,
) -> tuple[bool, ...] | None:
    return to_tuple_or_none(x, is_bool)


def is_intstr(x: object) -> TypeGuard[int | str]:
    return isinstance(x, (int, str))


def to_intstr_tuple_or_none(
    x: int | str | ListOrTuple[int | str] | None,
) -> tuple[int | str, ...] | None:
    return to_tuple_or_none(x, is_intstr)
