# # Within file flags to ignore unused imports
# flake8: noqa: F401
# pyright: reportUnusedImport=false


import sys

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol, runtime_checkable
else:
    from typing_extensions import Literal, Protocol, runtime_checkable

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


# The only purpose of the following line is so that pyright will put all of the
# conditional imports into the .pyi file when generating type stubs. Without this line,
# pyright will not include the above imports in the generated .pyi file, and it will
# result in a lot of red squiggles in user code.
_: 'Literal | Protocol | runtime_checkable | Concatenate[str, ParamSpec("P")] | ParamSpec | TypeGuard | NotRequired | TypedDict | assert_type'  # type:ignore
