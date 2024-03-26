import { enableMapSet } from "immer";
import { Updater, useImmer } from "use-immer";
import type { CellState } from "./cell";

// const [cellEditMap, setCellEditMap] = useImmer<
//   Map<string, { value: string; state: CellState; save_error?: string }>
// >(new Map<string, { value: string; state: CellState }>());
// enableMapSet();

export type CellEdit = {
  value: string;
  state: CellState;
  save_error?: string;
};
export type CellEditMap = Map<string, CellEdit>;
export type SetCellEditMap = Updater<CellEditMap>;
export const useCellEditMap = () => {
  const [cellEditMap, setCellEditMap] = useImmer<CellEditMap>(
    new Map<string, CellEdit>()
  );
  enableMapSet();
  return [cellEditMap, setCellEditMap] as const;
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
export const getCellEditMapValue = (
  x: CellEditMap,
  rowIndex: number,
  columnIndex: number
) => {
  return x.get(makeCellEditMapKey(rowIndex, columnIndex));
};
