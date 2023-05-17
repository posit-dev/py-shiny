import React from "react";
import { CellData, SortEntry } from "./types";
import { Rectangle } from "@glideapps/glide-data-grid";

export function useSortColumns(args: { rows: ReadonlyArray<CellData> }): {
  currentSort: SortEntry | null;
  sortedData: CellData;
  onSortClick: (col: number, screenPosition: Rectangle) => void;
  mapSortedRowToUnsorted: (row: number) => number;
} {
  const { rows } = args;

  const [sortList, setSortList] = React.useState<readonly SortEntry[]>([]);

  const { data: sortedData, rowNums: originalRowNums } = React.useMemo<{
    data: CellData;
    rowNums: ReadonlyArray<number>;
  }>(() => {
    return sortDataUsingSortList(rows, sortList, (rowA, rowB, columnIndex) => {
      const a = rowA[columnIndex];
      const b = rowB[columnIndex];
      return a < b ? -1 : a > b ? 1 : 0;
    });
  }, [rows, sortList]);

  const onSortClick = React.useCallback(
    (col: number, screenPosition: Rectangle): void => {
      setSortList(changeSortList(sortList, col));
    },
    [sortList]
  );

  // Function for converting post-sort row index to pre-sort row index
  const mapSortedRowToUnsorted = React.useCallback(
    (row: number) => originalRowNums[row],
    [originalRowNums]
  );

  const currentSort =
    sortList.length === 0 ? null : sortList[sortList.length - 1];

  return {
    currentSort,
    sortedData,
    onSortClick,
    mapSortedRowToUnsorted,
  };
}

function sortDataUsingSortList<T>(
  data: readonly T[],
  sortList: readonly SortEntry[],
  comparator: (a: T, b: T, columnIndex: number) => number
): { data: readonly T[]; rowNums: readonly number[] } {
  if (sortList.length === 0) {
    return { data, rowNums: data.map((_, i) => i) };
  }
  let newRows = [...data] as readonly T[];
  let originalRowNums = newRows.map((_, i) => i) as readonly number[];
  sortList.forEach(({ columnIndex, desc }) => {
    const descFactor = desc ? -1 : 1;
    const sortIndices = sortOrder(
      newRows,
      (a, b) => descFactor * comparator(a, b, columnIndex)
    );
    newRows = mget(newRows, sortIndices);
    originalRowNums = mget(originalRowNums, sortIndices);
  });
  return { data: newRows, rowNums: originalRowNums };
}

/**
 * Retrieve items[indices]
 */
function mget<T>(
  items: ReadonlyArray<T>,
  indices: ReadonlyArray<number>
): ReadonlyArray<T> {
  return indices.map((i) => items[i]);
}

/**
 * Sorts items by the comparator, but instead of returning a sorted array, returns the
 * indices of the items in sorted order.
 */
function sortOrder<T>(
  items: ReadonlyArray<T>,
  comparator: (a: T, b: T) => number
): Array<number> {
  const indices = items.map((_, index) => index);
  indices.sort((indexA, indexB) => comparator(items[indexA], items[indexB]));
  return indices;
}

function changeSortList(sortList: ReadonlyArray<SortEntry>, col: number) {
  // Decide whether we should sort descending or ascending.
  let desc: boolean;
  const idx = sortList.findIndex(({ columnIndex }) => columnIndex === col);
  if (idx >= 0) {
    if (idx === sortList.length - 1) {
      // 1. If the most recent sort entry is for this column, flip the direction.
      desc = !sortList[idx].desc;
    } else {
      // 2. If we have an earlier sort entry for this column, use that direction.
      //    I'm hoping this is convenient when repeatedly flipping back and forth
      //    between two columns, one of which only makes sense in descending order.)
      desc = sortList[idx].desc;
    }
  } else {
    // 3. In the absence of other info, use ascending.
    desc = false;
  }

  return (
    sortList
      // Remove existing sort entry for this column
      .filter(({ columnIndex }) => columnIndex !== col)
      // Add a new entry to the end
      .concat({ columnIndex: col, desc: desc })
  );
}
