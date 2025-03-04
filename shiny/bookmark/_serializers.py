from __future__ import annotations

from pathlib import Path
from shutil import copyfile
from typing import Any, TypeVar

from typing_extensions import TypeIs


class Unserializable: ...


T = TypeVar("T")


def is_unserializable(x: Any) -> TypeIs[Unserializable]:
    return isinstance(x, Unserializable)


async def serializer_unserializable(
    value: Any = None, state_dir: Path | None = None
) -> Unserializable:
    return Unserializable()


async def serializer_default(value: T, state_dir: Path | None) -> T:
    return value


# TODO-barret; Integrate
def serializer_file_input(
    value: Any,
    state_dir: Path | None,
) -> Any | Unserializable:
    if state_dir is None:
        return Unserializable()

    # TODO: barret; Double check this logic!

    # `value` is a data frame. When persisting files, we need to copy the file to
    # the persistent dir and then strip the original path before saving.
    datapath = Path(value["datapath"])
    new_paths = state_dir / datapath.name

    if new_paths.exists():
        new_paths.unlink()
    copyfile(datapath, new_paths)

    value["datapath"] = new_paths.name

    return value
