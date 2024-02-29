import { ResponseValue, makeRequest } from "./request";

import { CellState } from "./cell";

export type UpdateCellData = {
  rowIndex: number;
  columnId: string;
  value: unknown;
  prev: unknown;
};
export type UpdateCellDataRequest = {
  row_index: number;
  column_id: string;
  value: unknown;
  prev: unknown;
};

export function updateCellsData(props: {
  id: string;
  cellInfos: UpdateCellData[];
  onSuccess: (values: ResponseValue[]) => void;
  onError: (err: string) => void;
  columns: readonly string[];
  setData: (fn: (draft: unknown[][]) => void) => void;
  setCellEditMap: (
    fn: (draft: Map<string, { value: string; state: CellState }>) => void
  ) => void;
}) {
  const {
    id,
    cellInfos,
    onSuccess,
    onError,
    columns,
    setData,
    setCellEditMap,
  } = props;
  // // Skip page index reset until after next rerender
  // skipAutoResetPageIndex();

  const updateInfos: UpdateCellDataRequest[] = cellInfos.map((cellInfo) => {
    return {
      row_index: cellInfo.rowIndex,
      column_id: cellInfo.columnId,
      value: cellInfo.value,
      prev: cellInfo.prev,
    };
  });

  console.log("Set data here! (Send info back to shiny)", cellInfos);

  makeRequest(
    "outputRPC",
    [
      // id: string
      id,
      // handler: string
      "cells_update",
      // list[OnCellUpdateParams]
      updateInfos,
    ],
    (values: ResponseValue[]) => {
      // console.log("cellsUpdate - success!", values);
      setData((draft) => {
        values.forEach((value: string, i: number) => {
          const { rowIndex, columnId } = cellInfos[i];
          const colIndex = columns.indexOf(columnId);
          const row = draft[rowIndex];
          // console.log(
          //   "Setting new value!",
          //   value,
          //   columnId,
          //   draft[rowIndex]
          // );

          draft[rowIndex][colIndex] = value;
        });
      });
      setCellEditMap((draft) => {
        values.forEach((value: string, i: number) => {
          const { rowIndex, columnId } = cellInfos[i];
          const key = `[${rowIndex}, ${columnId}]`;

          const obj =
            draft.get(key) ?? ({} as { value: string; state: CellState });
          obj.value = value;
          obj.state = CellState.EditSuccess;
          console.log("Setting cell edit map");
          draft.set(key, obj);
        });
      });
      onSuccess(values);
    },
    (err: string) => {
      console.error("error!", err);
      onError(err);
    },
    undefined
  );
}
