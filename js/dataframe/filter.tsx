import {
  FiltersOptions,
  Header,
  TableOptions,
  getFacetedMinMaxValues,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
} from "@tanstack/react-table";
import React, {
  FC,
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { FilterNumeric } from "./filter-numeric";

export function useFilter<TData>(
  enabled: boolean | undefined
): FiltersOptions<TData> {
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

export const Filter: FC<FilterProps> = ({ header, className, ...props }) => {
  const typeHint = header.column.columnDef.meta?.typeHint;

  if (typeHint.type === "html") {
    // Do not filter on html types
    return null;
  }
  if (typeHint.type === "numeric") {
    const [from, to] = (header.column.getFilterValue() as
      | [number | undefined, number | undefined]
      | undefined) ?? [undefined, undefined];

    const range = () => {
      return header.column.getFacetedMinMaxValues() ?? [undefined, undefined];
    };

    return FilterNumeric({
      from,
      to,
      range,
      onRangeChange: (from, to) => header.column.setFilterValue([from, to]),
    });
  }

  return (
    <input
      {...props}
      className={`form-control form-control-sm ${className}`}
      type="text"
      onChange={(e) => header.column.setFilterValue(e.target.value)}
    />
  );
};
