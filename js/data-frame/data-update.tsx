import { ResponseValue, makeRequestPromise } from "./request";

import { CellStateEnum } from "./cell";
import { SetCellEditMapAtLoc } from "./cell-edit-map";
import type { PatchInfo } from "./types";

export type CellPatch = {
  rowIndex: number;
  columnIndex: number;
  value: any; // eslint-disable-line @typescript-eslint/no-explicit-any
  // prev: unknown;
};
export type CellPatchPy = {
  row_index: number;
  column_index: number;
  value: unknown;
  // prev: unknown;
};

type SetDataFn = (fn: (draft: unknown[][]) => void) => void;

export function addPatchToData({
  setData,
  newPatches,
  setCellEditMapAtLoc,
}: {
  setData: SetDataFn;
  newPatches: CellPatch[];
  setCellEditMapAtLoc: SetCellEditMapAtLoc;
}): void {
  // Update data
  setData((draft) => {
    newPatches.forEach(({ rowIndex, columnIndex, value }) => {
      draft[rowIndex]![columnIndex] = value;
    });
  });
  // Set the new patches in cell edit map info
  newPatches.forEach(({ rowIndex, columnIndex, value }) => {
    setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
      obj_draft.value = value;
      obj_draft.state = CellStateEnum.EditSuccess;
      // Remove save_error if it exists
      obj_draft.errorTitle = undefined;
    });
  });
}

export function cellPatchPyArrToCellPatchArr(
  patchesPy: CellPatchPy[]
): CellPatch[] {
  const patches: CellPatch[] = patchesPy.map(
    (patch: CellPatchPy): CellPatch => {
      return {
        rowIndex: patch.row_index,
        columnIndex: patch.column_index,
        value: patch.value,
      };
    }
  );
  return patches;
}

export function cellPatchArrToCellPatchPyArr(
  patches: CellPatch[]
): CellPatchPy[] {
  const patchesPy: CellPatchPy[] = patches.map((patch) => {
    return {
      row_index: patch.rowIndex,
      column_index: patch.columnIndex,
      value: patch.value,
    };
  });
  return patchesPy;
}

export function updateCellsData({
  patchInfo,
  patches,
  onSuccess,
  onError,
  columns,
  setData,
  setCellEditMapAtLoc,
}: {
  patchInfo: PatchInfo;
  patches: CellPatch[];
  onSuccess: (values: CellPatch[]) => void;
  onError: (err: string) => void;
  columns: readonly string[];
  setData: SetDataFn;
  setCellEditMapAtLoc: SetCellEditMapAtLoc;
}) {
  // // Skip page index reset until after next rerender
  // skipAutoResetPageIndex();

  const patchesPy = cellPatchArrToCellPatchPyArr(patches);

  makeRequestPromise({
    method: patchInfo.key,
    args: [
      // list[CellPatch]
      patchesPy,
    ],
  })
    .then((newPatchesPy: ResponseValue) => {
      // Assert type of values is list
      if (!Array.isArray(newPatchesPy)) {
        throw new Error("Expected a response of a list of patches");
      }

      for (const patch of newPatchesPy) {
        if (
          !("row_index" in patch && "column_index" in patch && "value" in patch)
        ) {
          throw new Error(
            "Expected list of patches containing `row_index`, `column_index`, and `value`"
          );
        }
      }
      newPatchesPy = newPatchesPy as CellPatchPy[];

      const newPatches = cellPatchPyArrToCellPatchArr(newPatchesPy);

      // Set the old patches locations back to success state
      // This may be overkill, but it guarantees that the incoming patches exit the saving state
      patches.forEach(({ rowIndex, columnIndex, value }) => {
        setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
          // If the cell is still saving, then set it back to ready.
          // If not, then something else has changed the cell state, so don't change it.
          if (obj_draft.state !== CellStateEnum.EditSaving) return;

          obj_draft.state = CellStateEnum.Ready;
          obj_draft.value = value;
          obj_draft.errorTitle = undefined;
        });
      });

      // Update data and cell edit map with new patches
      addPatchToData({ setData, newPatches, setCellEditMapAtLoc });

      onSuccess(newPatches);
    })
    .catch((err: string) => {
      patches.forEach(({ rowIndex, columnIndex, value }) => {
        setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
          obj_draft.value = String(value);

          obj_draft.state = CellStateEnum.EditFailure;
          obj_draft.errorTitle = String(err);
        });
      });
      onError(err);
    });
}
