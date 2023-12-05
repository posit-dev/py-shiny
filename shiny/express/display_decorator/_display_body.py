from __future__ import annotations

import ast
import functools
import inspect
import linecache
import sys
import types
from typing import Any, Callable, Dict, Protocol, TypeVar, cast, runtime_checkable

from ._func_displayhook import _display_decorator_function_def
from ._helpers import find_code_for_func
from ._node_transformers import (
    DisplayFuncsTransformer,
    FuncBodyDisplayHookTransformer,
    TargetFunctionTransformer,
    display_decorator_func_name,
    sys_alias,
)

# It's quite expensive to decorate with display_body, and it could be done to
# inner functions where the outer function is called a lot. Use a cache to save
# us from having to do the expensive stuff (parsing, transforming, compiling)
# more than once.
code_cache: Dict[types.CodeType, types.CodeType] = {}

T = TypeVar("T")
TFunc = TypeVar("TFunc", bound=Callable[..., Any])


def auto_displayhook(x: T) -> T:
    if x is not None:
        sys.displayhook(x)
    return x


@runtime_checkable
class WrappedFunction(Protocol):
    __wrapped__: types.FunctionType


def unwrap(fn: TFunc) -> TFunc:
    while isinstance(fn, WrappedFunction):
        fn = fn.__wrapped__
    return fn


display_body_attr = "__display_body__"


def display_body_unwrap_inplace():
    """
    Like `display_body`, but far more violent. This will attempt to traverse any
    decorators between this one and the function, and then modify the function _in
    place_. It will then return the function that was passed in.
    """

    def decorator(fn: TFunc) -> TFunc:
        unwrapped_fn = unwrap(fn)

        # Check if we've already done this
        if hasattr(unwrapped_fn, display_body_attr):
            return fn

        if unwrapped_fn.__code__ in code_cache:
            fcode = code_cache[fn.__code__]
        else:
            # Save for next time
            fcode = _transform_body(cast(types.FunctionType, unwrapped_fn))
            code_cache[unwrapped_fn.__code__] = fcode

        unwrapped_fn.__code__ = fcode
        setattr(unwrapped_fn, display_body_attr, True)
        return fn

    return decorator


def display_body():
    def decorator(fn: TFunc) -> TFunc:
        if fn.__code__ in code_cache:
            fcode = code_cache[fn.__code__]
        else:
            # Save for next time
            fcode = _transform_body(cast(types.FunctionType, fn))
            code_cache[fn.__code__] = fcode

        # Create a new function from the code object
        new_func = types.FunctionType(
            code=fcode,
            # We add calls to sys.displayhook, but we use our own alias for
            # `sys` so we don't have to worry about whether the user happens to
            # have a different `sys` alias in scope.
            globals={
                sys_alias: auto_displayhook,
                display_decorator_func_name: _display_decorator_function_def,
                **fn.__globals__,
            },
            name=fn.__name__,
            argdefs=fn.__defaults__,
            closure=fn.__closure__,
        )
        # Need to copy over some attributes, for some reason FunctionType()
        # doesn't include all of these
        new_func.__kwdefaults__ = fn.__kwdefaults__
        new_func.__dict__.update(fn.__dict__)
        return cast(TFunc, functools.wraps(fn)(new_func))

    return decorator


def _transform_body(fn: types.FunctionType) -> types.CodeType:
    # The approach we take here is much more complicated than what you'd expect.
    #
    # The simple approach is to use ast.parse() to get an AST for the function,
    # use an ast.NodeTransformer to modify the AST, and then compile() and
    # exec() each top-level node. However, this approach does not work correctly
    # with closures, because compile/exec do not support scopes besides global
    # and local.
    #
    # Instead, we need to ast.parse(), transform just the part of the AST that
    # is the function we care about, and compile the entire module, and then
    # find the code object for the function we want. We then use that code
    # object to programmatically create a new function.

    filename = inspect.getsourcefile(fn)
    if filename is None:
        raise RuntimeError(
            f"Failed to find source code for function '{fn.__name__}'."
            " This should never happen, please file an issue!"
        )

    parsed_ast = read_ast(filename)
    if parsed_ast is None:
        raise RuntimeError(
            f"Failed to read source code for function '{fn.__name__}'."
            " This should never happen, please file an issue!"
        )

    tft = TargetFunctionTransformer(
        fn,
        # If we find `fn` in the AST, use transform its body to use displayhook
        _transform_function_ast,
    )

    new_ast = tft.visit(parsed_ast)
    if not tft.found:
        raise RuntimeError(
            f"Failed to find function '{fn.__name__}' in AST."
            " This should never happen, please file an issue!"
        )

    # The new AST contains new nodes; give them locations so the compiler will
    # accept them
    new_ast = ast.fix_missing_locations(new_ast)

    # Compile the new AST into a code object
    compiled_code = compile(
        new_ast,
        filename=filename,
        mode="exec",
    )

    fcode = find_code_for_func(
        compiled_code, fn, compare_decorated_code_objects(tft.found)
    )
    if fcode is None:
        raise RuntimeError(
            f"Failed to find code object for function '{fn.__name__}'."
            " This should never happen, please file an issue!"
        )

    return fcode


def read_ast(filename: str) -> ast.Module | None:
    # This is the logic we originally used to read the AST, but it doesn't work when the
    # function being decorated is defined in a Jupyter notebook cell. However, the code
    # is available in linecache (without which, tracebacks wouldn't work right).

    # with open(filename) as fd:
    #     return ast.parse(fd.read(), filename=filename)

    lines = linecache.getlines(filename)
    if len(lines) == 0:
        return None
    return ast.parse("".join(lines), filename=filename)


def _transform_function_ast(node: ast.AST) -> ast.AST:
    if not isinstance(node, ast.FunctionDef):
        return node
    func_node = cast(ast.FunctionDef, FuncBodyDisplayHookTransformer().visit(node))
    func_node.body = [
        DisplayFuncsTransformer().visit(child) for child in func_node.body
    ]
    return func_node


def compare_decorated_code_objects(func_ast: ast.FunctionDef):
    linenos = [*[x.lineno for x in func_ast.decorator_list], func_ast.lineno]

    def comparator(candidate: types.CodeType, target: types.CodeType) -> bool:
        if candidate.co_name == target.co_name:
            if candidate.co_firstlineno == target.co_firstlineno:
                return True
            elif candidate.co_firstlineno in linenos:
                # Ordinarily we'd just compare co_name (or co_qualname if possible) and
                # co_firstlineno for equality, but sometimes the co_firstlineno points
                # to the first decorator (most cases) and other times it points to the
                # def line (when compiling node-by-node, as in express mode).
                return True

        return False

    return comparator


__builtins__[sys_alias] = auto_displayhook
__builtins__[display_decorator_func_name] = _display_decorator_function_def
