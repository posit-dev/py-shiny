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

  const typeHint = header.column.columnDef.meta?.typeHint;
  if (typeHint.type === "string" || typeHint.type === "unknown") {
    return (
      <input
        {...props}
        className={`form-control form-control-sm ${className}`}
        type="text"
        onChange={(e) => header.column.setFilterValue(e.target.value)}
      />
    );
  }

  if (typeHint.type === "numeric") {
    const [from, to] = (props.header.column.getFilterValue() as
      | [number | undefined, number | undefined]
      | undefined) ?? [undefined, undefined];
    const [min, max] = header.column.getFacetedMinMaxValues();

    return FilterNumeric({
      from,
      to,
      min,
      max,
      onRangeChange: (from, to) => header.column.setFilterValue([from, to]),
    });
  }
};
