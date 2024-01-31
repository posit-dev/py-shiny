# pyright: reportUnusedExpression=false
# flake8: noqa
from __future__ import annotations

import contextlib
import inspect
import sys as sys1
from typing import Generator, cast

import pytest
from htmltools import Tagifiable

from shiny import render, ui
from shiny.express import expressify


@contextlib.contextmanager
def capture_display() -> Generator[list[object], None, None]:
    old_displayhook = sys1.displayhook
    displayed: list[object] = []
    sys1.displayhook = displayed.append
    try:
        yield displayed
    finally:
        sys1.displayhook = old_displayhook


@expressify()
def display_repeated(value: str, /, times: int, *, sep: str = " ") -> None:
    sep.join([value] * times)


def test_simple():
    with capture_display() as d:
        display_repeated("hello", 3)
        assert d == ["hello hello hello"]

    with capture_display() as d:
        display_repeated("hello", 3, sep=", ")
        assert d == ["hello, hello, hello"]

    with capture_display() as d:
        display_repeated("hello", times=3, sep=", ")
        assert d == ["hello, hello, hello"]

    with pytest.raises(TypeError):
        display_repeated("hello")  # type: ignore


@expressify()
def display_variadic(*args: object, **kwargs: object):
    "# args"
    for arg in args:
        arg
    "# kwargs"
    for key, value in kwargs.items():
        (key, value)


def test_null_filtered():
    @expressify()
    def has_none():
        1
        None
        2

    with capture_display() as d:
        has_none()
        assert d == [1, 2]


def test_variadic():
    with capture_display() as d:
        display_variadic("one", "two", three="four")
        assert d == ["# args", "one", "two", "# kwargs", ("three", "four")]


def nested(z: int = 1):
    x = 2

    @expressify()
    def inner():
        x * 10 * z

    with capture_display() as d:
        inner()
        assert d == [x * 10 * z]


def test_caching():
    import shiny.express.expressify_decorator._expressify as _expressify

    nested()
    cache_len_before = len(_expressify.code_cache)
    nested(z=3)
    cache_len_after = len(_expressify.code_cache)
    assert cache_len_before == cache_len_after


def test_duplicate_func_names_ok():
    """
    The two inner() functions should be treated as different from each other,
    and different from the third copy in test_nested()
    """

    x = "hello"

    @expressify()
    def inner():  # pyright: ignore[reportRedeclaration]
        x + " world"

    inner_old = inner

    @expressify()
    def inner():  # pyright: ignore[reportRedeclaration]
        x + " universe"

    with capture_display() as d:
        inner_old()
        assert d == ["hello world"]

    with capture_display() as d:
        inner()
        assert d == ["hello universe"]

    # Here's yet another one, just to be mean
    @expressify()
    def inner():
        x + " nobody"


def test_not_decorated():
    def not_decorated():
        1
        2
        3

    decorated = expressify()(not_decorated)

    with capture_display() as d:
        decorated()
        assert d == [1, 2, 3]

    with capture_display() as d:
        not_decorated()
        assert d == []

    assert inspect.getsource(decorated) == inspect.getsource(not_decorated)


def test_annotations():
    @expressify()
    def annotated(x: int, y: int) -> int:
        """Here's a docstring"""
        x + y
        return 0

    assert annotated.__name__ == "annotated"
    assert annotated.__annotations__ == {"x": "int", "y": "int", "return": "int"}
    assert annotated.__doc__ == "Here's a docstring"

    assert inspect.getsource(annotated) == inspect.getsource(annotated.__wrapped__)  # type: ignore


def test_implicit_output():
    @expressify()
    def has_implicit_outputs():
        @render.code
        def foo():
            return "hello"

    with capture_display() as d:
        has_implicit_outputs()
        assert len(d) == 1
        d0 = cast(Tagifiable, d[0])
        assert d0.tagify() == ui.output_code("foo")


def test_no_nested_transform_unless_explicit():
    @expressify()
    def inner1():
        1
        2
        None

        def inner2():
            # Doesn't transform, it doesn't have the decorator
            3
            4

            @expressify()
            def inner3():
                # Does transform, it has the decorator again
                5
                6

            inner3()

        inner2()

    with capture_display() as d:
        inner1()
        assert d == [1, 2, 5, 6]
