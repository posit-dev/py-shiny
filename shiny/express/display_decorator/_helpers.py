from __future__ import annotations

import ast
from types import CodeType, FunctionType
from typing import Callable

CodeEqual = Callable[[CodeType, CodeType], bool]


def match_name_and_lineno(candidate: CodeType, target: CodeType) -> bool:
    return (
        candidate.co_name == target.co_name
        and candidate.co_firstlineno == target.co_firstlineno
    )


def find_code_for_func(
    code: CodeType, func: FunctionType, equals: CodeEqual = match_name_and_lineno
) -> CodeType | None:
    """
    Given a code object, recurses into it trying to find the code sub-object that is a
    match (for a user-defined definition of "match") for the given function.
    """
    if not isinstance(code, CodeType):
        return None

    if equals(code, func.__code__):
        return code

    for const in code.co_consts:
        if not isinstance(const, CodeType):
            continue

        found = find_code_for_func(const, func, equals)
        if found is not None:
            return found

    return None


def ast_matches_func(node: ast.AST, func: FunctionType) -> bool:
    if not isinstance(node, ast.FunctionDef):
        return False
    linenos = [*[dec.lineno for dec in node.decorator_list], node.lineno]
    return func.__code__.co_firstlineno in linenos and func.__name__ == node.name
