import os
from abc import ABC, abstractmethod
from pathlib import Path


class BookmarkState(ABC):
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


class BookmarkStateLocal(BookmarkState):
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
