# TODO: barret - Set / Load SaveState for Connect. Ex: Connect https://github.com/posit-dev/connect/blob/8de330aec6a61cf21e160b5081d08a1d3d7e8129/R/connect.R#L915

import os
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Awaitable, Callable
from urllib.parse import urlencode as urllib_urlencode

from .._utils import private_random_id
from ..reactive import isolate
from ._utils import is_hosted, to_json

if TYPE_CHECKING:
    from .. import Inputs
else:
    Inputs = Any


class SaveState(ABC):
    """
    Class for saving and restoring state to/from disk.
    """

    @abstractmethod
    async def save_dir(
        self,
        id: str,
        # write_files: Callable[[Path], Awaitable[None]],
    ) -> Path:
        """
        Construct directory for saving state.

        Parameters
        ----------
        id
            The unique identifier for the state.

        Returns
        -------
        Path
            Directory location for saving state. This directory must exist.
        """
        # write_files
        #     A async function that writes the state to a serializable location. The method receives a path object and
        ...

    @abstractmethod
    async def load_dir(
        self,
        id: str,
        # read_files: Callable[[Path], Awaitable[None]],
    ) -> Path:
        """
        Construct directory for loading state.

        Parameters
        ----------
        id
            The unique identifier for the state.

        Returns
        -------
        Path | None
            Directory location for loading state. If `None`, state loading will be ignored. If a `Path`, the directory must exist.
        """
        ...


class SaveStateLocal(SaveState):
    """
    Function wrappers for saving and restoring state to/from disk when running Shiny
    locally.
    """

    def _local_dir(self, id: str) -> Path:
        # Try to save/load from current working directory as we do not know where the
        # app file is located
        return Path(os.getcwd()) / "shiny_bookmarks" / id

    async def save_dir(self, id: str) -> Path:
        state_dir = self._local_dir(id)
        if not state_dir.exists():
            state_dir.mkdir(parents=True)
        return state_dir

    async def load_dir(self, id: str) -> Path:
        return self._local_dir(id)

    # async def save(
    #     self,
    #     id: str,
    #     write_files: Callable[[Path], Awaitable[None]],
    # ) -> None:
    #     state_dir = self._local_dir(id)
    #     if not state_dir.exists():
    #         state_dir.mkdir(parents=True)

    #     await write_files(state_dir)

    # async def load(
    #     self,
    #     id: str,
    #     read_files: Callable[[Path], Awaitable[None]],
    # ) -> None:
    #     await read_files(self._local_dir(id))
    #     await read_files(self._local_dir(id))


# #############################################################################


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

        # TODO: barret move code to single call location
        # A function for saving the state object to disk, given a directory to save
        # to.
        async def save_state_to_dir(state_dir: Path) -> None:
            self.dir = state_dir

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

            return

        # Pass the saveState function to the save interface function, which will
        # invoke saveState after preparing the directory.

        # TODO: FUTURE - Get the save interface from the session object?
        # Look for a save.interface function. This will be defined by the hosting
        # environment if it supports bookmarking.
        save_interface_loaded: SaveState | None = None

        if save_interface_loaded is None:
            if is_hosted():
                # TODO: Barret
                raise NotImplementedError(
                    "The hosting environment does not support server-side bookmarking."
                )
            else:
                # We're running Shiny locally.
                save_interface_loaded = SaveStateLocal()

        if not isinstance(save_interface_loaded, SaveState):
            raise TypeError(
                "The save interface retrieved must be an instance of `shiny.bookmark.SaveState`."
            )

        save_dir = Path(await save_interface_loaded.save_dir(id))
        await save_state_to_dir(save_dir)

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
            input_qs = urllib_urlencode(to_json(input_values_serialized))

            qs_str_parts.append("_inputs_&")
            qs_str_parts.append(input_qs)

        if len(self.values) > 0:
            if len(qs_str_parts) > 0:
                qs_str_parts.append("&")

            values_qs = urllib_urlencode(to_json(self.values))

            qs_str_parts.append("_values_&")
            qs_str_parts.append(values_qs)

        return "".join(qs_str_parts)
