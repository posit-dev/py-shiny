export type CellData = ReadonlyArray<ReadonlyArray<any>>;

export interface SortEntry {
  readonly columnIndex: number;
  readonly desc: boolean;
}
