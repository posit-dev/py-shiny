from __future__ import annotations

import warnings
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, Any, TypeVar

from typing_extensions import TypeIs

if TYPE_CHECKING:
    from ..session import Session


class Unserializable: ...


T = TypeVar("T")


def is_unserializable(x: Any) -> TypeIs[Unserializable]:
    return isinstance(x, Unserializable)


async def serializer_unserializable(
    value: Any = None,
    state_dir: Path | None = None,
) -> Unserializable:
    return Unserializable()


async def serializer_default(value: T, state_dir: Path | None) -> T:
    return value


def serializer_file_input(
    value: list[dict[str, str | int]], state_dir: Path | None
) -> Any | Unserializable:
    if state_dir is None:
        warnings.warn(
            "`shiny.ui.input_file()` is attempting to save bookmark state. "
            'However the App\'s `bookmark_store=` is not set to `"server"`. '
            "Either exclude the input value (`session.bookmark.exclude.append(NAME)`) "
            'or set `bookmark_store="server"`.',
            UserWarning,
            stacklevel=1,
        )
        return Unserializable()

    # `value` is a "data frame" (list of arrays). When persisting files, we need to copy the file to
    # the persistent dir and then strip the original path before saving.

    if not isinstance(value, list):
        raise ValueError(
            f"Invalid value type for file input. Expected list, received: {type(value)}"
        )

    ret_file_infos = value.copy()

    for i, file_info in enumerate(ret_file_infos):
        if not isinstance(file_info, dict):
            raise ValueError(
                f"Invalid file info type for file input ({i}). "
                f"Expected dict, received: {type(file_info)}"
            )
        if "datapath" not in file_info:
            raise ValueError(f"Missing 'datapath' key in file info ({i}).")
        if not isinstance(file_info["datapath"], str):
            raise TypeError(
                f"Invalid type for 'datapath' in file info ({i}). "
                f"Expected str, received: {type(file_info['datapath'])}"
            )

        datapath = Path(file_info["datapath"])
        new_path = state_dir / datapath.name
        if new_path.exists():
            new_path.unlink()
        copyfile(datapath, new_path)

        # Store back into the file_info dict to update `ret_file_infos`
        file_info["datapath"] = new_path.name

    return ret_file_infos


def can_serialize_input_file(session: Session) -> bool:
    """
    Check if the session can serialize file input.

    Args:
        session (Session): The current session.

    Returns:
        bool: True if the session can serialize file input, False otherwise.
    """
    return session.bookmark.store == "server"
