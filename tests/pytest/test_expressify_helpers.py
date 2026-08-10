# pyright: reportUnusedExpression=false
# flake8: noqa
"""
Direct unit tests for the AST/code-object matching helpers that back
`@expressify` and `@render.express`.

These helpers are how expressify locates the `def` for a function in its source
file so it can re-transform the body. The matching rule is intentionally narrow
(name + line number), so these tests pin down exactly which nodes do and do not
match.
"""

from __future__ import annotations

import ast
import types
from typing import Any

from shiny.express.expressify_decorator._helpers import (
    ast_matches_func,
    find_code_for_func,
    match_name_and_lineno,
)

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

FILENAME = "<test-src>"


def compile_src(src: str) -> tuple[dict[str, Any], ast.Module]:
    """
    Compile a source string, returning both the resulting namespace and the parsed
    AST. Because both come from the same source text, line numbers in the AST line
    up with `co_firstlineno` of the resulting code objects -- which is precisely the
    invariant that `ast_matches_func()` relies on.
    """
    tree = ast.parse(src, filename=FILENAME)
    ns: dict[str, Any] = {}
    exec(compile(tree, FILENAME, "exec"), ns)
    return ns, tree


def find_node(tree: ast.AST, name: str, *, nth: int = 0) -> ast.FunctionDef:
    """Find the `nth` FunctionDef named `name`."""
    matches = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    return matches[nth]


def rename(fn: Any, new_name: str) -> Any:
    """Mimic a decorator that rewrites `__name__` without touching the code object."""
    fn.__name__ = new_name
    return fn


# ----------------------------------------------------------------------------
# ast_matches_func: the happy path
# ----------------------------------------------------------------------------


def test_matches_plain_def():
    ns, tree = compile_src("def foo():\n    pass\n")
    assert ast_matches_func(find_node(tree, "foo"), ns["foo"])


def test_matches_def_with_decorators():
    """
    `co_firstlineno` may point at the first decorator line or at the `def` line,
    depending on how the code was compiled. Both must match.
    """
    src = "def deco(f):\n    return f\n\n\n@deco\n@deco\ndef foo():\n    pass\n"
    ns, tree = compile_src(src)
    node = find_node(tree, "foo")

    # Sanity check that this source really does have two decorators above `def`.
    assert len(node.decorator_list) == 2
    assert [d.lineno for d in node.decorator_list] == [5, 6]
    assert node.lineno == 7

    assert ast_matches_func(node, ns["foo"])

    # Both the decorator lines and the `def` line are accepted.
    for lineno in (5, 6, 7):
        fake = types.FunctionType(
            ns["foo"].__code__.replace(co_firstlineno=lineno), {}, "foo"
        )
        assert ast_matches_func(node, fake), f"lineno {lineno} should match"


# ----------------------------------------------------------------------------
# ast_matches_func: renamed functions (the regression this guards -- #2016)
# ----------------------------------------------------------------------------


def test_matches_when_dunder_name_was_rewritten():
    """
    A decorator applied between the `def` and `expressify()` may rewrite
    `__name__`. Matching must key off the code object's name, which always
    reflects the name at the `def` site. https://github.com/posit-dev/py-shiny/issues/2016
    """
    ns, tree = compile_src("def foo():\n    pass\n")
    fn = rename(ns["foo"], "foo_renamed")

    assert fn.__name__ == "foo_renamed"
    assert fn.__code__.co_name == "foo"
    assert ast_matches_func(find_node(tree, "foo"), fn)


def test_rename_does_not_match_the_colliding_def():
    """
    The nastiest case: a function is renamed to the name of a *different* function
    in the same file. We must match the renamed function's own `def`, and must not
    match the unrelated function that happens to share the new name.
    """
    src = "def other():\n    pass\n\n\ndef foo():\n    pass\n"
    ns, tree = compile_src(src)
    fn = rename(ns["foo"], "other")

    assert ast_matches_func(find_node(tree, "foo"), fn)
    assert not ast_matches_func(find_node(tree, "other"), fn)


def test_rename_to_empty_or_odd_names_still_matches_own_def():
    ns, tree = compile_src("def foo():\n    pass\n")
    for new_name in ("", "  ", "foo.bar", "<lambda>", "foo" * 100):
        fn = rename(ns["foo"], new_name)
        assert ast_matches_func(find_node(tree, "foo"), fn)


# ----------------------------------------------------------------------------
# ast_matches_func: things that must NOT match
# ----------------------------------------------------------------------------


def test_does_not_match_different_function():
    src = "def foo():\n    pass\n\n\ndef bar():\n    pass\n"
    ns, tree = compile_src(src)
    assert not ast_matches_func(find_node(tree, "bar"), ns["foo"])
    assert not ast_matches_func(find_node(tree, "foo"), ns["bar"])


def test_same_name_different_lines_match_only_their_own_def():
    """Two same-named defs are disambiguated purely by line number."""
    src = (
        "def make():\n"
        "    def inner():\n"
        "        return 1\n"
        "    return inner\n"
        "\n"
        "def make2():\n"
        "    def inner():\n"
        "        return 2\n"
        "    return inner\n"
        "\n"
        "a = make()\n"
        "b = make2()\n"
    )
    ns, tree = compile_src(src)
    node_a = find_node(tree, "inner", nth=0)
    node_b = find_node(tree, "inner", nth=1)

    assert ast_matches_func(node_a, ns["a"])
    assert not ast_matches_func(node_b, ns["a"])
    assert ast_matches_func(node_b, ns["b"])
    assert not ast_matches_func(node_a, ns["b"])


def test_does_not_match_non_functiondef_nodes():
    ns, tree = compile_src("class Foo:\n    pass\n\n\ndef foo():\n    pass\n")
    fn = ns["foo"]

    class_node = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    assert not ast_matches_func(tree, fn)
    assert not ast_matches_func(class_node, fn)


def test_does_not_match_async_functiondef():
    """
    `ast.AsyncFunctionDef` is not an `ast.FunctionDef`, so async defs never match.
    This is why `@expressify` does not support async functions; see
    `test_expressify_async_is_unsupported()` in test_display_decorator.py.
    """
    ns, tree = compile_src("async def foo():\n    pass\n")
    async_node = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef))
    assert not ast_matches_func(async_node, ns["foo"])


# ----------------------------------------------------------------------------
# find_code_for_func / match_name_and_lineno
# ----------------------------------------------------------------------------


def test_find_code_for_func_finds_nested_code():
    src = (
        "def outer():\n"
        "    def middle():\n"
        "        def inner():\n"
        "            return 42\n"
        "        return inner\n"
        "    return middle\n"
        "inner = outer()()\n"
    )
    ns, tree = compile_src(src)
    module_code = compile(tree, FILENAME, "exec")

    found = find_code_for_func(module_code, ns["inner"])
    assert found is not None
    assert found.co_name == "inner"
    assert found is not ns["inner"].__code__  # a distinct but matching code object
    assert found.co_firstlineno == ns["inner"].__code__.co_firstlineno


def test_find_code_for_func_uses_code_name_not_dunder_name():
    """Renaming must not confuse the code-object search either."""
    ns, tree = compile_src("def foo():\n    return 1\n")
    module_code = compile(tree, FILENAME, "exec")
    fn = rename(ns["foo"], "totally_different")

    found = find_code_for_func(module_code, fn)
    assert found is not None
    assert found.co_name == "foo"


def test_find_code_for_func_returns_none_when_absent():
    ns, _ = compile_src("def foo():\n    return 1\n")
    other_code = compile("def bar():\n    return 2\n", FILENAME, "exec")
    assert find_code_for_func(other_code, ns["foo"]) is None


def test_find_code_for_func_ignores_non_code_input():
    ns, _ = compile_src("def foo():\n    return 1\n")
    assert find_code_for_func("not code", ns["foo"]) is None  # type: ignore[arg-type]


def test_match_name_and_lineno():
    ns, _ = compile_src("def foo():\n    return 1\n")
    code = ns["foo"].__code__

    assert match_name_and_lineno(code, code)
    assert not match_name_and_lineno(code.replace(co_name="bar"), code)
    assert not match_name_and_lineno(
        code.replace(co_firstlineno=code.co_firstlineno + 1), code
    )
