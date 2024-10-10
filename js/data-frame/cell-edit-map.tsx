import { enableMapSet } from "immer";
import { DraftFunction, Updater, useImmer } from "use-immer";
import type { CellState } from "./cell";

// const [cellEditMap, setCellEditMap] = useImmer<
//   Map<string, { value: string; state: CellState; save_error?: string }>
// >(new Map<string, { value: string; state: CellState }>());
// enableMapSet();

export type CellEdit = {
  // rowIndex: number;
  // columnIndex: number;
  value?: string;
  state?: CellState;
  errorTitle?: string;
  isEditing?: boolean;
  editValue?: string;
  // selection location info
  // cursor position info
};
export type CellEditMap = Map<string, CellEdit>;
export type SetCellEditMap = Updater<CellEditMap>;
export type SetCellEditMapAtLoc = (
  rowIndex: number,
  columnIndex: number,
  obj_fn: DraftFunction<CellEdit>
) => void;
export const useCellEditMap = () => {
  const [cellEditMap, setCellEditMap] = useImmer<CellEditMap>(
    new Map<string, CellEdit>()
  );
  enableMapSet();
  const setCellEditMapAtLoc: SetCellEditMapAtLoc = (
    rowIndex: number,
    columnIndex: number,
    obj_fn: DraftFunction<CellEdit>
  ) => {
    setCellEditMap((draft) => {
      const key = makeCellEditMapKey(rowIndex, columnIndex);
      const obj = draft.get(key) ?? ({} as CellEdit);
      obj_fn(obj);
      // obj.rowIndex = rowIndex;
      // obj.columnIndex = columnIndex;
      draft.set(key, obj);
    });
  };
  return {
    cellEditMap,
    // setCellEditMap,
    setCellEditMapAtLoc,
    resetCellEditMap: () => {
      setCellEditMap(new Map<string, CellEdit>());
    },
  } as const;
};

export const makeCellEditMapKey = (rowIndex: number, columnIndex: number) => {
  return `[${rowIndex}, ${columnIndex}]`;
};

export const cellEditMapHasKey = (
  x: CellEditMap,
  rowIndex: number,
  columnIndex: number
) => {
  return x.has(makeCellEditMapKey(rowIndex, columnIndex));
};
export const getCellEditMapObj = (
  x: CellEditMap,
  rowIndex: number,
  columnIndex: number
): [CellEdit, string] => {
  const key = makeCellEditMapKey(rowIndex, columnIndex);
  return [x.get(key) ?? ({} as CellEdit), key];
};
