import { ResponseValue, makeRequestPromise } from "./request";

import type { CellState } from "./cell";
import { CellStateEnum } from "./cell";
import { CellEdit, SetCellEditMap, makeCellEditMapKey } from "./cell-edit-map";
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

export function updateCellsData({
  id,
  patchInfo,
  patches,
  onSuccess,
  onError,
  columns,
  setData,
  setCellEditMap,
}: {
  id: string | null;
  patchInfo: PatchInfo;
  patches: CellPatch[];
  onSuccess: (values: CellPatch[]) => void;
  onError: (err: string) => void;
  columns: readonly string[];
  setData: (fn: (draft: unknown[][]) => void) => void;
  setCellEditMap: SetCellEditMap;
}) {
  // // Skip page index reset until after next rerender
  // skipAutoResetPageIndex();

  const patchesPy: CellPatchPy[] = patches.map((patch) => {
    return {
      row_index: patch.rowIndex,
      column_index: patch.columnIndex,
      value: patch.value,
      // prev: patch.prev,
    };
  });

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

      const newPatches = newPatchesPy.map((patch: CellPatchPy) => {
        return {
          rowIndex: patch.row_index,
          columnIndex: patch.column_index,
          value: patch.value,
        };
      });

      setData((draft) => {
        newPatches.forEach(({ rowIndex, columnIndex, value }) => {
          draft[rowIndex][columnIndex] = value;
        });
      });
      setCellEditMap((draft) => {
        newPatches.forEach(({ rowIndex, columnIndex, value }) => {
          const key = makeCellEditMapKey(rowIndex, columnIndex);
          const obj = draft.get(key) ?? ({} as CellEdit);
          obj.value = value;
          obj.state = CellStateEnum.EditSuccess;
          // Remove save_error if it exists
          delete obj.save_error;

          draft.set(key, obj);
        });
      });
      onSuccess(newPatches);
    })
    .catch((err: string) => {
      setCellEditMap((draft) => {
        patches.forEach(({ rowIndex, columnIndex, value }) => {
          const key = makeCellEditMapKey(rowIndex, columnIndex);
          const obj = draft.get(key) ?? ({} as CellEdit);

          // Do not overwrite value!
          obj.value = String(value);

          obj.state = CellStateEnum.EditFailure;
          obj.save_error = String(err);
          // console.log("Setting cell edit map");
          draft.set(key, obj);
        });
      });
      onError(err);
    });
}
