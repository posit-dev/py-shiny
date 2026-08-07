from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Awaitable, Callable
from urllib.parse import urlencode as urllib_urlencode

from .._utils import private_random_id
from ..reactive import isolate
from ._bookmark_state import local_save_dir
from ._global import get_bookmark_save_dir_fn
from ._types import BookmarkSaveDirFn
from ._utils import in_shiny_server, to_json_file, to_json_str

if TYPE_CHECKING:
    from .. import Inputs
    from .._app import App


class BookmarkState:
    """
    The state being written while a bookmark is saved.

    Shiny creates one of these each time a bookmark is taken and passes it to any
    `session.bookmark.on_bookmark()` callback, which may add entries to
    `values` or write files into `dir` before the state is persisted.

    App authors do not construct this class directly.
    """

    # session: ?
    # * Would get us access to inputs, possibly app dir, registered on save / load classes (?), exclude
    #
    input: Inputs
    """The session's inputs. Every value except those named in `exclude` is saved."""

    values: dict[str, Any]
    """
    Arbitrary extra values to save alongside the inputs.

    Starts empty. Add to it from an `on_bookmark()` callback to store state that is
    not held in an input, and read it back from
    `RestoreState.values` when restoring.
    """

    exclude: list[str]
    """Scoped input names to leave out of the bookmark."""

    _on_save: (
        Callable[["BookmarkState"], Awaitable[None]] | None
    )  # A callback to invoke during the saving process.

    # These are set not in initialize(), but by external functions that modify
    # the ShinySaveState object.
    dir: Path | None
    """
    Directory to write bookmark files into, or `None`.

    Only set when the bookmark is saved server-side (`store="server"`), in which case
    Shiny creates the directory and sets this before invoking `on_bookmark()`. It stays
    `None` for `store="url"`, which encodes the state into a query string and never
    touches disk.
    """

    def __init__(
        self,
        input: Inputs,
        exclude: list[str],
        on_save: Callable[["BookmarkState"], Awaitable[None]] | None,
    ):
        self.input = input
        self.exclude = exclude
        self._on_save = on_save
        self.dir = None  # This will be set by external functions.
        self.values = {}

    async def _call_on_save(self):
        # Allow user-supplied save function to do things like add state$values, or
        # save data to state dir.
        if self._on_save:
            with isolate():
                await self._on_save(self)

    async def _save_state(self, *, app: App) -> str:
        """
        Save a bookmark state to disk (JSON).

        Returns
        -------
        str
            A query string which can be used to restore the session.
        """
        id = private_random_id(prefix="", bytes=8)

        # Get the save directory from the `bookmark_save_dir` function.
        # Then we invoke `.on_save(state)` via `._call_on_save() with the directory set
        # to `self.dir`.

        # This will be defined by the hosting environment if it supports bookmarking.
        save_bookmark_fn: BookmarkSaveDirFn | None = get_bookmark_save_dir_fn(
            app._bookmark_save_dir_fn
        )

        if save_bookmark_fn is None:
            if in_shiny_server():
                raise NotImplementedError(
                    "The hosting environment does not support server-side bookmarking."
                )
            else:
                # We're running Shiny locally.
                save_bookmark_fn = local_save_dir

        # Save the state to disk.
        self.dir = Path(await save_bookmark_fn(id))
        await self._call_on_save()

        input_values_json = await self.input._serialize(
            exclude=self.exclude,
            state_dir=self.dir,
        )
        assert self.dir is not None

        to_json_file(input_values_json, self.dir / "input.json")

        if len(self.values) > 0:
            to_json_file(self.values, self.dir / "values.json")
        # End save to disk

        # No need to encode URI component as it is only ascii characters.
        return f"_state_id_={id}"

    async def _encode_state(self) -> str:
        """
        Encode the state to a URL.

        This does not save to disk!

        Returns
        -------
        str
            A query string which can be used to restore the session.
        """
        # Allow user-supplied onSave function to do things like add state$values.
        await self._call_on_save()

        input_values_serialized = await self.input._serialize(
            exclude=self.exclude,
            # Do not include directory as we are not saving to disk.
            state_dir=None,
        )

        # Using an array to construct string to avoid multiple serial concatenations.
        qs_str_parts: list[str] = []

        # If any input values are present, add them.
        if len(input_values_serialized) > 0:
            input_qs = urllib_urlencode(
                {
                    key: to_json_str(value)
                    for key, value in input_values_serialized.items()
                }
            )

            qs_str_parts.append("_inputs_&")
            qs_str_parts.append(input_qs)

        if len(self.values) > 0:
            if len(qs_str_parts) > 0:
                qs_str_parts.append("&")

            # print("\n\nself.values", self.values)
            values_qs = urllib_urlencode(
                {key: to_json_str(value) for key, value in self.values.items()}
            )

            qs_str_parts.append("_values_&")
            qs_str_parts.append(values_qs)

        return "".join(qs_str_parts)
