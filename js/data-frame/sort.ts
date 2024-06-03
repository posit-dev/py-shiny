import {
  SortingOptions,
  SortingState,
  getSortedRowModel,
} from "@tanstack/react-table";
import React, { useState } from "react";

import type { ColumnSort } from "@tanstack/react-table";

export type { ColumnSort, SortingState };

export function useSort<TData>(): {
  sorting: SortingState;
  setSorting: React.Dispatch<React.SetStateAction<SortingState>>;
  sortState: { sorting: SortingState };
  sortingTableOptions: SortingOptions<TData>;
} {
  const [sorting, setSorting] = useState<SortingState>([]);

  return {
    sorting,
    sortState: {
      sorting,
    },
    sortingTableOptions: {
      onSortingChange: setSorting,
      getSortedRowModel: getSortedRowModel(),
    },
    setSorting,
  };
}
