from __future__ import annotations

# TODO-barret-render.data_frame; Docs
# TODO-barret-render.data_frame; Add examples of patch!
from typing import Protocol, Sequence

from ._types import CellPatch, CellValue


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


class PatchFnSync(Protocol):
    def __call__(
        self,
        *,
        patch: CellPatch,
    ) -> CellValue: ...


class PatchesFnSync(Protocol):
    def __call__(
        self,
        *,
        patches: list[CellPatch],
    ) -> list[CellPatch]: ...


def assert_patches_shape(x: Sequence[CellPatch]) -> None:
    assert isinstance(x, Sequence)

    for patch in x:
        assert isinstance(patch, dict)
        assert "row_index" in patch
        assert "column_index" in patch
        assert "value" in patch
