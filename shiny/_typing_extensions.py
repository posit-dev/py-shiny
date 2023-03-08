import sys

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol, runtime_checkable
else:
    from typing_extensions import Literal, Protocol, runtime_checkable

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

# Even though TypedDict is available in Python 3.8, because it's used with NotRequired,
# they should both come from the same typing module.
# https://peps.python.org/pep-0655/#usage-in-python-3-11
if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict

if sys.version_info >= (3, 11):
    from typing import assert_type
else:
    from typing_extensions import assert_type

if sys.version_info < (3, 10):
    from typing_extensions import Concatenate, ParamSpec
else:
    from typing import Concatenate, ParamSpec


if False:
    TypeGuard[object]
    TypedDict[object, object]
    Literal["False"]
    Protocol
    assert_type[object]
    Concatenate[object, object]
    ParamSpec[object]
    NotRequired[object]
    runtime_checkable[object]
