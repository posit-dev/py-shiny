from __future__ import annotations

import pickle
import warnings
from contextlib import contextmanager
from contextvars import ContextVar, Token
from pathlib import Path
from typing import Any, Literal, Optional
from urllib.parse import parse_qs, parse_qsl

from shiny.types import MISSING_TYPE

from . import _external as bookmark_external
from ._bookmark_state import local_restore_dir
from ._types import GetBookmarkRestoreDir
from ._utils import from_json_str, is_hosted


class RestoreContextState:
    input: dict[str, Any]
    values: dict[str, Any]
    dir: Path | None

    def __init__(
        self,
        *,
        input: dict[str, Any],
        values: dict[str, Any],
        dir: Path | None,
    ):
        self.input = input
        self.values = values
        self.dir = dir

    def _name_has_namespace(self, name: str, prefix: str) -> bool:
        return name.startswith(prefix)

    def _un_namespace(self, name: str, prefix: str) -> str:
        if not self._name_has_namespace(name, prefix):
            raise ValueError(f"Name (`{name}`) does not have namespace: `{prefix}`")

        return name.removeprefix(prefix)

    def _state_within_namespace(self, prefix: str) -> "RestoreContextState":
        # Given a restore state object, return a modified version that's scoped to this
        # namespace.

        # Keep only `input` that are in the scope, and rename them
        input = {
            self._un_namespace(name, prefix): value
            for name, value in self.input.items()
            if self._name_has_namespace(name, prefix)
        }

        # Keep only `values` that are in the scope, and rename them
        values = {
            self._un_namespace(name, prefix): value
            for name, value in self.values.items()
            if self._name_has_namespace(name, prefix)
        }

        # TODO: Barret; Is this for bookmarking?!?
        dir = self.dir
        if dir is not None:
            dir = dir / prefix
            # Here was a check for if dir doesn't exist, then dir <- NULL
            # But this is confounded with url vs file system, so we'll just
            # assume that the directory exists.
            # if not dir.exists():
            #     dir = None

        return RestoreContextState(input=input, values=values, dir=dir)


class RestoreContext:
    active: bool
    """This will be set to TRUE if there's actually a state to restore"""
    _init_error_msg: str | None
    """
    This is set to an error message string in case there was an initialization
    error. Later, after the app has started on the client, the server can send
    this message as a notification on the client.
    """

    # This is a RestoreInputSet for input values. This is a key-value store with
    # some special handling.
    input: "RestoreInputSet"

    # Directory for extra files, if restoring from state that was saved to disk.
    dir: Path | None

    # For values other than input values. These values don't need the special
    # handling that's needed for input values, because they're only accessed
    # from the onRestore function.
    values: dict[str, Any]

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.active = False
        self._init_error_msg = None
        self.input = RestoreInputSet()
        self.values = {}
        self.dir = None

    @staticmethod
    async def from_query_string(query_string: str) -> "RestoreContext":
        res_ctx = RestoreContext()

        if query_string.startswith("?"):
            query_string = query_string[1:]

        try:
            # withLogErrors

            query_string_dict = parse_qs(query_string)
            if (
                "__subapp__" in query_string_dict
                and query_string_dict["__subapp__"]
                and query_string_dict["__subapp__"][0] == "1"
            ):
                # Ignore subapps in shiny docs
                res_ctx.reset()

            elif "_state_id_" in query_string_dict and query_string_dict["_state_id_"]:
                # If we have a "_state_id_" key, restore from saved state and
                # ignore other key/value pairs. If not, restore from key/value
                # pairs in the query string.
                res_ctx.active = True
                await res_ctx._load_state_qs(query_string)

            else:
                # The query string contains the saved keys and values
                res_ctx.active = True
                await res_ctx._decode_state_qs(query_string)

        except Exception as e:
            res_ctx.reset()
            res_ctx._init_error_msg = str(e)
            print(e)

        return res_ctx

    # def set(
    #     self,
    #     *,
    #     active: bool = False,
    #     init_error_msg: str | None = None,
    #     input_: dict[str, Any] = {},
    #     values: dict[str, Any] = {},
    #     dir_: Path | None = None,
    # ) -> None:
    #     self.active = active
    #     self._init_error_msg = init_error_msg
    #     self.input = RestoreInputSet()
    #     self.input._values = input_
    #     self.values = values
    #     self.dir = dir_

    # This should be called before a restore context is popped off the stack.
    def flush_pending(self) -> None:
        self.input.flush_pending()

    def as_state(self) -> RestoreContextState:
        """
        Returns a dict representation of the RestoreContext object. This is passed
        to the app author's onRestore function. An important difference between
        the RestoreContext object and the dict is that the former's `input` field
        is a RestoreInputSet object, while the latter's `input` field is just a
        list.
        """
        return RestoreContextState(
            # Shallow copy
            input={**self.input.as_dict()},
            # Shallow copy
            values={**self.values},
            dir=self.dir,
        )

    async def _load_state_qs(self, query_string: str) -> None:
        """Given a query string with a _state_id_, load saved state with that ID."""
        values = parse_qs(query_string)
        id = values.get("_state_id_", None)

        if not id:
            raise ValueError("Missing `_state_id_` from query string")

        id = id[0]

        load_bookmark_fn: GetBookmarkRestoreDir | None = None
        if not isinstance(bookmark_external._bookmark_restore_dir, MISSING_TYPE):
            load_bookmark_fn = bookmark_external._bookmark_restore_dir

        if load_bookmark_fn is None:
            if is_hosted():
                # TODO: Barret; Implement Connect's `bookmark_load_dir` function
                raise NotImplementedError(
                    "The hosting environment does not support server-side bookmarking."
                )
            else:
                # We're running Shiny locally.
                load_bookmark_fn = local_restore_dir

        # Load the state from disk.
        self.dir = Path(await load_bookmark_fn(id))

        if not self.dir.exists():
            raise ValueError("Bookmarked state directory does not exist.")

        with open(self.dir / "input.pickle", "rb") as f:
            input_values = pickle.load(f)
        self.input = RestoreInputSet(input_values)

        values_file = self.dir / "values.pickle"
        if values_file.exists():
            with open(values_file, "rb") as f:
                self.values = pickle.load(f)
        # End load state from disk

        return

    async def _decode_state_qs(self, query_string: str) -> None:
        """Given a query string with values encoded in it, restore saved state from those values."""
        # Remove leading '?'
        if query_string.startswith("?"):
            query_string = query_string[1:]

        qs_pairs = parse_qsl(query_string, keep_blank_values=True)

        inputs_count = 0
        values_count = 0
        storing_to: Literal["ignore", "inputs", "values"] = "ignore"
        input_vals: dict[str, Any] = {}
        value_vals: dict[str, Any] = {}

        # For every query string pair, store the inputs / values in the appropriate
        # dictionary.
        # Error if multiple '_inputs_' or '_values_' found (respectively).
        for qs_key, qs_value in qs_pairs:
            if qs_key == "_inputs_":
                inputs_count += 1
                storing_to = "inputs"
                if inputs_count > 1:
                    raise ValueError(
                        "Invalid state string: more than one '_inputs_' found"
                    )
            elif qs_key == "_values_":
                values_count += 1
                storing_to = "values"
                if values_count > 1:
                    raise ValueError(
                        "Invalid state string: more than one '_values_' found"
                    )
            else:

                if storing_to == "ignore":
                    continue

                try:
                    if storing_to == "inputs":
                        input_vals[qs_key] = from_json_str(qs_value)
                    elif storing_to == "values":
                        value_vals[qs_key] = from_json_str(qs_value)
                except Exception as e:
                    warnings.warn(
                        f'Failed to parse URL parameter "{qs_key}"', stacklevel=3
                    )
                    print(e, storing_to, qs_key, qs_value)

        self.input = RestoreInputSet(input_vals)
        self.values = value_vals


class RestoreInputSet:
    """
    Restore input set.

    This is basically a key-value store, except for one important difference: When the
    user `get()`s a value, the value is marked as pending; when `._flush_pending()` is
    called, those pending values are marked as used. When a value is marked as used,
    `get()` will not return it, unless called with `force=True`. This is to make sure
    that a particular value can be restored only within a single call to `with
    restore_context(ctx):`. Without this, if a value is restored in a dynamic UI, it
    could completely prevent any other (non- restored) kvalue from being used.
    """

    _values: dict[str, Any]
    _pending: set[str]
    """Names of values which have been marked as pending"""
    _used: set[str]
    """Names of values which have been used"""

    def __init__(self, values: Optional[dict[str, Any]] = None):

        self._values = {} if values is None else values
        self._pending = set()
        self._used = set()

    def exists(self, name: str) -> bool:
        return name in self._values

    def available(self, name: str) -> bool:
        return self.exists(name) and not self.is_used(name)

    def is_pending(self, name: str) -> bool:
        return name in self._pending

    def is_used(self, name: str) -> bool:
        return name in self._used

    # Get a value. If `force` is TRUE, get the value without checking whether
    # has been used, and without marking it as pending.
    def get(self, name: str, force: bool = False) -> Any:
        if force:
            return self._values[name]

        if not self.available(name):
            return None

        self._pending.add(name)
        return self._values[name]

    # Take pending names and mark them as used, then clear pending list.
    def flush_pending(self) -> None:
        self._used.update(self._pending)
        self._pending.clear()

    def as_dict(self) -> dict[str, Any]:
        return self._values


# #############################################################################
# Restore context stack
# #############################################################################

# import queue
# restore_ctx_stack = queue.LifoQueue()


_current_restore_context: ContextVar[Optional[RestoreContext]] = ContextVar(
    "current_restore_context",
    default=None,
)


# `with restore_context(r_ctx): ...`
@contextmanager
def restore_context(restore_ctx: RestoreContext | None):
    token: Token[RestoreContext | None] = _current_restore_context.set(restore_ctx)
    try:

        yield
    finally:
        if isinstance(restore_ctx, RestoreContext):
            restore_ctx.flush_pending()
        _current_restore_context.reset(token)


def has_current_restore_context() -> bool:
    if _current_restore_context.get() is not None:
        return True
    from ..session import get_current_session

    cur_session = get_current_session()
    if cur_session is not None and cur_session.bookmark._restore_context is not None:
        return True
    return False


# Call to access the current restore context. First look on the restore
# context stack, and if not found, then see if there's one on the current
# reactive domain. In practice, the only time there will be a restore context
# on the stack is when executing the UI function; when executing server code,
# the restore context will be attached to the domain/session.
def get_current_restore_context() -> RestoreContext | None:
    ctx = _current_restore_context.get()
    if ctx is not None:
        return ctx

    from ..session import get_current_session

    cur_session = get_current_session()
    if cur_session is None or cur_session.bookmark._restore_context is None:
        raise RuntimeError("No restore context found")

    ctx = cur_session.bookmark._restore_context
    return ctx


def restore_input(id: str, default: Any) -> Any:
    """
    Restore an input value

    This restores an input value from the current restore context. It should be
    called early on inside of input functions (like `input_text()`).

    Parameters
    ----------
    id
        Name of the input value to restore.
    default
        A default value to use, if there's no value to restore.
    """
    # Will run even if the domain is missing
    if not has_current_restore_context():
        return default

    # Requires a domain or restore context
    ctx = get_current_restore_context()
    if isinstance(ctx, RestoreContext):
        old_inputs = ctx.input
        if old_inputs.available(id):
            return old_inputs.get(id)

    return default
