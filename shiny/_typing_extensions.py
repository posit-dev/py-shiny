# # Within file flags to ignore unused imports
# flake8: noqa: F401
# pyright: reportUnusedImport=false

__all__ = (
    "Concatenate",
    "ParamSpec",
    "TypeGuard",
    "NotRequired",
    "TypedDict",
    "assert_type",
)


import sys

if sys.version_info >= (3, 10):
    from typing import Concatenate, ParamSpec, TypeGuard
else:
    from typing_extensions import Concatenate, ParamSpec, TypeGuard

# Even though TypedDict is available in Python 3.8, because it's used with NotRequired,
# they should both come from the same typing module.
# https://peps.python.org/pep-0655/#usage-in-python-3-11
if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict, assert_type
else:
    from typing_extensions import NotRequired, TypedDict, assert_type
