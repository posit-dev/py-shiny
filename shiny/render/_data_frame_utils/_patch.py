from __future__ import annotations

# TODO-barret; Docs
# TODO-barret; Add examples!
from typing import Protocol, cast

from ..._typing_extensions import TypedDict
from ..renderer._utils import JsonifiableDict

CellValue = str


class CellPatch(TypedDict):
    row_index: int
    column_index: int
    value: CellValue
    # prev_value: CellValue


def cell_patch_to_jsonifiable(cell_patch: CellPatch) -> JsonifiableDict:
    return cast(JsonifiableDict, dict(cell_patch))


class PatchFn(Protocol):
    async def __call__(
        self,
        *,
        patch: CellPatch,
    ) -> CellValue: ...


class PatchesFn(Protocol):
    async def __call__(
        self,
        *,
        patches: list[CellPatch],
    ) -> list[CellPatch]: ...


def assert_patches_shape(x: list[CellPatch]) -> None:
    assert isinstance(x, list)

    for patch in x:
        assert isinstance(patch, dict)
        assert "row_index" in patch
        assert "column_index" in patch
        assert "value" in patch
