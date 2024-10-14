import {
  SortingOptions,
  SortingState,
  getSortedRowModel,
} from "@tanstack/react-table";
import React, { useState } from "react";

import type { ColumnDef, ColumnSort, Updater } from "@tanstack/react-table";

export type { ColumnSort, SortingState };

export function useSort<TData>({
  getColDefs,
}: {
  getColDefs: () => ColumnDef<unknown[], unknown>[];
}): {
  sorting: SortingState;
  setSorting: React.Dispatch<React.SetStateAction<SortingState>>;
  sortTableStateOptions: { sorting: SortingState };
  sortTableOptions: SortingOptions<TData>;
} {
  const [sorting, setSorting] = useState<SortingState>([]);

  return {
    sorting,
    sortTableStateOptions: {
      sorting,
    },
    sortTableOptions: {
      onSortingChange: (sortUpdater: Updater<SortingState>) => {
        const newSorting: SortingState =
          typeof sortUpdater === "function"
            ? sortUpdater(sorting)
            : sortUpdater;
        const coldefs = getColDefs();
        const htmlColumnsSet = new Set(
          coldefs
            .filter((col) => col.meta!.isHtmlColumn)
            .map((col) => col.header!)
        );

        const filteredSort =
          htmlColumnsSet.size == 0
            ? newSorting
            : newSorting.filter((sort) => {
                return !htmlColumnsSet.has(sort.id);
              });

        setSorting(filteredSort);
      },
      getSortedRowModel: getSortedRowModel(),
    },
    setSorting,
  };
}
