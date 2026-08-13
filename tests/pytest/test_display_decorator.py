# pyright: reportUnusedExpression=false
# flake8: noqa
from __future__ import annotations

import contextlib
import functools
import inspect
import sys as sys1
from typing import Any, Callable, Generator, TypeVar, cast

import pytest
from htmltools import Tagifiable

from shiny import render, ui
from shiny.express import expressify
from shiny.express.expressify_decorator._expressify import (
    _describe_func,
    expressify_unwrap_inplace,
)

TFunc = TypeVar("TFunc", bound=Callable[..., Any])


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


# ============================================================================
# Renaming decorators (https://github.com/posit-dev/py-shiny/issues/2016)
#
# A common Express idiom is to generate several `@render.express` outputs in a
# loop, using a decorator to give each one a unique `__name__` (and therefore a
# unique output id). That decorator mutates `__name__` but leaves the code
# object alone, so expressify must locate the `def` in the AST by the code
# object's name rather than by `__name__`.
# ============================================================================


def rename(new_name: str) -> Callable[[TFunc], TFunc]:
    """A decorator that rewrites `__name__` in place, leaving the function itself."""

    def decorator(fn: TFunc) -> TFunc:
        fn.__name__ = new_name
        return fn

    return decorator


def test_renamed_func():
    @expressify()
    @rename("renamed")
    def original():
        1
        2

    assert original.__name__ == "renamed"
    assert original.__code__.co_name == "original"  # type: ignore[attr-defined]

    with capture_display() as d:
        original()
        assert d == [1, 2]


def test_renamed_func_preserves_metadata():
    @expressify(has_docstring=True)
    @rename("renamed_with_docstring")
    def original(x: int) -> None:
        """A docstring that must not be displayed."""
        x + 1

    assert original.__name__ == "renamed_with_docstring"
    assert original.__doc__ == "A docstring that must not be displayed."
    assert original.__annotations__ == {"x": "int", "return": "None"}
    assert inspect.getsource(original) == inspect.getsource(original.__wrapped__)  # type: ignore

    with capture_display() as d:
        original(41)
        assert d == [42]


def test_rename_colliding_with_another_func_name():
    """
    The dangerous case: the new name collides with a *different* function defined in
    this same file. We must transform the renamed function's own body, not the
    unrelated same-named function's body.
    """

    def decoy():
        "decoy body should never be displayed"

    @expressify()
    @rename("decoy")
    def real():
        "real body"

    assert real.__name__ == "decoy"

    with capture_display() as d:
        real()
        assert d == ["real body"]

    # The decoy is untouched -- it was never expressified.
    with capture_display() as d:
        decoy()
        assert d == []


def test_rename_colliding_with_an_expressified_func():
    """Same as above, but the decoy is itself expressified, so both are in the cache."""

    @expressify()
    def twin():
        "twin body"

    @expressify()
    @rename("twin")
    def other():
        "other body"

    with capture_display() as d:
        twin()
        assert d == ["twin body"]

    with capture_display() as d:
        other()
        assert d == ["other body"]


def test_renamed_funcs_in_a_loop_keep_distinct_closures():
    """
    The exact shape of #2016: one `def` inside a loop, renamed per iteration. All
    iterations share a single code object (and therefore a single `code_cache`
    entry), so this also guards against the cache leaking state between them.
    """
    funcs: list[Callable[[], None]] = []

    for label in ["a", "b", "c"]:

        @expressify()
        @rename(f"boxed_{label}")
        def boxed(label: str = label):
            "value for " + label

        funcs.append(boxed)

    assert [f.__name__ for f in funcs] == ["boxed_a", "boxed_b", "boxed_c"]

    with capture_display() as d:
        for f in funcs:
            f()
        assert d == ["value for a", "value for b", "value for c"]


def test_renamed_funcs_in_a_loop_via_closure_cell():
    """As above, but capturing the loop variable via a closure cell rather than a
    default argument -- the pattern used in the original bug report."""
    funcs: list[Callable[[], None]] = []

    for label in ["x", "y"]:

        def make(label: str) -> Callable[[], None]:
            @expressify()
            @rename(f"boxed_{label}")
            def boxed():
                "value for " + label

            return boxed

        funcs.append(make(label))

    assert [f.__name__ for f in funcs] == ["boxed_x", "boxed_y"]

    with capture_display() as d:
        for f in funcs:
            f()
        assert d == ["value for x", "value for y"]


def test_renamed_funcs_in_a_loop_share_one_cache_entry():
    import shiny.express.expressify_decorator._expressify as _expressify

    before = len(_expressify.code_cache)
    for label in ["p", "q", "r", "s"]:

        @expressify()
        @rename(f"cached_{label}")
        def cached():
            label

    after = len(_expressify.code_cache)
    # One `def` site == one code object == one cache entry, regardless of renames.
    assert after - before == 1


def test_stacked_renames():
    """Multiple renaming decorators between the `def` and `expressify()`."""

    @expressify()
    @rename("second")
    @rename("first")
    def original():
        "body"

    assert original.__name__ == "second"

    with capture_display() as d:
        original()
        assert d == ["body"]


def test_rename_above_expressify():
    """Renaming *after* expressify has run is unaffected by any of this."""

    @rename("renamed_after")
    @expressify()
    def original():
        "body"

    assert original.__name__ == "renamed_after"

    with capture_display() as d:
        original()
        assert d == ["body"]


def test_rename_on_nested_expressified_func():
    """A renamed inner function still resolves its enclosing closure correctly."""
    multiplier = 10

    def outer():
        @expressify()
        @rename("inner_renamed")
        def inner():
            multiplier * 5

        return inner

    with capture_display() as d:
        outer()()
        assert d == [50]


def test_rename_with_args_and_flow_control():
    """Renaming must not disturb signature handling or control-flow transforms."""

    @expressify()
    @rename("renamed_variadic")
    def variadic(*args: object, sep: str = "-", **kwargs: object):
        for arg in args:
            arg
        if kwargs:
            sep.join(sorted(kwargs))

    with capture_display() as d:
        variadic(1, 2, b="", a="")
        assert d == [1, 2, "a-b"]

    with capture_display() as d:
        variadic(1, sep="+", z="", y="")
        assert d == [1, "y+z"]


def test_rename_with_implicit_output():
    """A renamed expressify function still auto-displays inner renderers."""

    @expressify()
    @rename("renamed_outer")
    def has_implicit_outputs():
        @render.code
        def foo():
            return "hello"

    with capture_display() as d:
        has_implicit_outputs()
        assert len(d) == 1
        d0 = cast(Tagifiable, d[0])
        assert str(d0.tagify()) == str(ui.output_code("foo"))


# ----------------------------------------------------------------------------
# expressify_unwrap_inplace() -- the variant used by `@render.express`
# ----------------------------------------------------------------------------


def test_renamed_func_unwrap_inplace():
    def renamed_in_place():
        1
        2

    renamed_in_place.__name__ = "some_other_name"
    fn = expressify_unwrap_inplace()(renamed_in_place)

    # Transforms the function in place and hands back the same object.
    assert fn is renamed_in_place
    assert fn.__name__ == "some_other_name"

    with capture_display() as d:
        fn()
        assert d == [1, 2]


def test_unwrap_inplace_sees_through_wrapped_chain():
    """
    `expressify_unwrap_inplace()` follows `__wrapped__` to the real function. The
    wrapper's `__name__` (copied by `functools.wraps`) must not be used for matching.
    """

    def target():
        7
        8

    target.__name__ = "renamed_target"

    @functools.wraps(target)
    def wrapper():
        return target()

    fn = expressify_unwrap_inplace()(wrapper)

    assert fn is wrapper
    with capture_display() as d:
        fn()
        assert d == [7, 8]


def test_unwrap_inplace_is_idempotent_with_rename():
    def target():
        1
        2

    target.__name__ = "renamed_twice"
    once = expressify_unwrap_inplace()(target)
    twice = expressify_unwrap_inplace()(once)

    assert twice is target
    # Applying twice must not double-wrap the displayhook calls.
    with capture_display() as d:
        twice()
        assert d == [1, 2]


# ----------------------------------------------------------------------------
# @render.express -- the end-to-end path from the bug report
# ----------------------------------------------------------------------------


def test_render_express_renamed_outputs_get_distinct_ids():
    """
    The user-visible payoff of #2016: renaming yields one output id per loop
    iteration, instead of every iteration colliding on the same id.
    """
    labels = ["human_animal", "environmental"]
    renderers: list[render.express] = []

    for label in labels:
        # A factory so each output captures its own `label` in a closure cell
        # (rather than a default arg, which `@render.express` warns about).
        def make(label: str) -> render.express:
            @render.express
            @rename(f"docs_label_{label}")
            def docs_label():
                "count for " + label

            return docs_label

        renderers.append(make(label))

    assert [r.output_id for r in renderers] == [
        "docs_label_human_animal",
        "docs_label_environmental",
    ]
    assert [r.__name__ for r in renderers] == [
        "docs_label_human_animal",
        "docs_label_environmental",
    ]

    # And each renders its own value rather than sharing one.
    for r, label in zip(renderers, labels):
        with capture_display() as d:
            r.fn._orig_fn()  # type: ignore[attr-defined]
            assert d == ["count for " + label]


# ----------------------------------------------------------------------------
# Documented limitations (pinned so any change here is deliberate)
# ----------------------------------------------------------------------------


def test_expressify_async_is_unsupported():
    """
    `ast_matches_func()` only matches `ast.FunctionDef`, never `ast.AsyncFunctionDef`,
    so `@expressify` cannot transform an async function. This is pre-existing behavior
    -- `@render.express` rejects async functions up front with a clearer message.
    """
    with pytest.raises(RuntimeError, match="Failed to find the definition of function"):

        @expressify()
        async def async_fn():
            1

    with pytest.raises(TypeError, match="does not support async functions"):

        @render.express
        async def async_out():
            1


# ----------------------------------------------------------------------------
# Error message diagnostics
# ----------------------------------------------------------------------------


def test_describe_func_reports_code_name():
    def target():
        pass

    assert _describe_func(target) == "'target'"

    target.__name__ = "renamed"
    described = _describe_func(target)
    # Both names must appear: the one we search the AST for, and the one the user sees.
    assert "'target'" in described
    assert "'renamed'" in described


def test_ast_lookup_failure_message_is_actionable():
    """
    The message must name the function as it appears in the *source* (its code-object
    name), not `__name__`, and must point at the file and line. Reporting only
    `__name__` sent the reporter of #2016 looking for a name that was never in the AST.
    """
    with pytest.raises(RuntimeError) as excinfo:

        @expressify()
        @rename("name_that_is_not_in_the_source")
        async def real_source_name():
            1

    msg = str(excinfo.value)

    # Identifies the function by the name actually present in the source...
    assert "'real_source_name'" in msg
    # ...while still mentioning the renamed `__name__`, so the user can connect it
    # back to the decorator they wrote.
    assert "name_that_is_not_in_the_source" in msg
    # Locates the definition.
    assert __file__ in msg or "test_display_decorator.py" in msg
    assert "line " in msg
    # And explains the likely causes rather than only "please file an issue".
    assert "async def" in msg
    assert "wrapper" in msg


def test_missing_source_file_message():
    """A function with no source file on disk cannot be expressified."""
    ns: dict[str, Any] = {}
    exec("def no_source():\n    1\n", ns)

    with pytest.raises(RuntimeError, match="Failed to (find|read) the source"):
        expressify()(ns["no_source"])


def test_expressify_cannot_see_through_a_wrapper_below_it():
    """
    When a *wrapping* decorator sits between the `def` and `expressify()`, the
    function handed to expressify is the wrapper. Expressify transforms the wrapper's
    body (which has no expressions of its own), so the inner function's expressions
    are not captured. Renaming decorators work because they return the original
    function; wrapping decorators do not.
    """

    def wrapping(fn: TFunc) -> TFunc:
        @functools.wraps(fn)
        def wrapper(*args: object, **kwargs: object):
            return fn(*args, **kwargs)

        return cast(TFunc, wrapper)

    @expressify()
    @wrapping
    def wrapped():
        1
        2

    with capture_display() as d:
        wrapped()
        assert d == []


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
        # `Renderer.tagify()` now returns a `TagifiedTag` (immutable
        # sibling of `Tag` from htmltools >= 0.7.0 / py-htmltools#120),
        # so `==` is never true across the two sibling types. Compare
        # rendered HTML instead.
        assert str(d0.tagify()) == str(ui.output_code("foo"))


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
