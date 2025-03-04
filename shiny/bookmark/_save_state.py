# TODO: barret - Set / Load SaveState for Connect. Ex: Connect https://github.com/posit-dev/connect/blob/8de330aec6a61cf21e160b5081d08a1d3d7e8129/R/connect.R#L915
# Might need to have independent save/load functions to register to avoid a class constructor

import pickle
from pathlib import Path
from typing import TYPE_CHECKING, Any, Awaitable, Callable
from urllib.parse import urlencode as urllib_urlencode

from .._utils import private_random_id
from ..reactive import isolate
from ._bookmark_state import BookmarkState, BookmarkStateLocal
from ._utils import is_hosted, to_json_str

if TYPE_CHECKING:
    from .. import Inputs
else:
    Inputs = Any


class ShinySaveState:
    # session: ?
    # * Would get us access to inputs, possibly app dir, registered on save / load classes (?), exclude
    #
    input: Inputs
    values: dict[str, Any]
    exclude: list[str]
    # _bookmark_: A special value that is always excluded from the bookmark.
    on_save: (
        Callable[["ShinySaveState"], Awaitable[None]] | None
    )  # A callback to invoke during the saving process.

    # These are set not in initialize(), but by external functions that modify
    # the ShinySaveState object.
    dir: Path | None

    def __init__(
        self,
        input: Inputs,
        exclude: list[str],
        on_save: Callable[["ShinySaveState"], Awaitable[None]] | None,
    ):
        self.input = input
        self.exclude = exclude
        self.on_save = on_save
        self.dir = None  # This will be set by external functions.
        self.values = {}

        self._always_exclude: list[str] = ["._bookmark_"]

    async def _call_on_save(self):
        # Allow user-supplied save function to do things like add state$values, or
        # save data to state dir.
        if self.on_save:
            with isolate():
                await self.on_save(self)

    def _exclude_bookmark_value(self):
        # If the bookmark value is not in the exclude list, add it.
        if "._bookmark_" not in self.exclude:
            self.exclude.append("._bookmark_")

    async def _save_state(self) -> str:
        """
        Save a state to disk (pickle).

        Returns
        -------
        str
            A query string which can be used to restore the session.
        """
        id = private_random_id(prefix="", bytes=8)

        # Pass the saveState function to the save interface function, which will
        # invoke saveState after preparing the directory.

        # TODO: FUTURE - Get the save interface from the session object?
        # Look for a save.interface function. This will be defined by the hosting
        # environment if it supports bookmarking.
        save_interface_loaded: BookmarkState | None = None

        if save_interface_loaded is None:
            if is_hosted():
                # TODO: Barret
                raise NotImplementedError(
                    "The hosting environment does not support server-side bookmarking."
                )
            else:
                # We're running Shiny locally.
                save_interface_loaded = BookmarkStateLocal()

        if not isinstance(save_interface_loaded, BookmarkState):
            raise TypeError(
                "The save interface retrieved must be an instance of `shiny.bookmark.BookmarkStateLocal`."
            )

        save_dir = Path(await save_interface_loaded.save_dir(id))

        # Save the state to disk.
        self.dir = save_dir
        await self._call_on_save()

        self._exclude_bookmark_value()

        input_values_json = await self.input._serialize(
            exclude=self.exclude,
            state_dir=self.dir,
        )
        assert self.dir is not None
        with open(self.dir / "input.pickle", "wb") as f:
            pickle.dump(input_values_json, f)

        if len(self.values) > 0:
            with open(self.dir / "values.pickle", "wb") as f:
                pickle.dump(self.values, f)
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

        self._exclude_bookmark_value()

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
