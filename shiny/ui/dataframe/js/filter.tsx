import {
  FiltersOptions,
  Header,
  TableOptions,
  getFacetedMinMaxValues,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
} from "@tanstack/react-table";
import React, { FC, useCallback } from "react";

export function useFilter<TData>(enabled: boolean): FiltersOptions<TData> {
  if (enabled) {
    return {
      getFilteredRowModel: getFilteredRowModel(),
      getFacetedRowModel: getFacetedRowModel(),
      getFacetedUniqueValues: getFacetedUniqueValues(),
      getFacetedMinMaxValues: getFacetedMinMaxValues(),
      filterFns: {
        substring: (row, columnId, value, addMeta) => {
          return row.getValue(columnId).toString().includes(value);
        },
      },
    };
  } else {
    return {};
  }
}

export interface FilterProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  header: Header<unknown[], unknown>;
}

export const Filter: FC<FilterProps> = (props) => {
  const { header, className } = props;

  return (
    <input
      {...props}
      className={`form-control form-control-sm ${className}`}
      type="text"
      onChange={(e) => header.column.setFilterValue(e.target.value)}
    />
  );
};
