import {
  ColumnFiltersOptions,
  ColumnFiltersState,
  FilterMeta,
  Header,
  Row,
  getFacetedMinMaxValues,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
} from "@tanstack/react-table";
import React, { FC, useState } from "react";
import { FilterNumeric } from "./filter-numeric";

type FilterValueString = string;
type FilterValueNumeric =
  | [number, number]
  | [number | undefined, number]
  | [number, number | undefined];
type FilterValue = FilterValueString | FilterValueNumeric;

export type { ColumnFiltersState, FilterValue };

export function useFilters<TData>(enabled: boolean | undefined): {
  columnFilters: ColumnFiltersState;
  setColumnFilters: React.Dispatch<React.SetStateAction<ColumnFiltersState>>;
  columnFiltersState: { columnFilters: ColumnFiltersState };
  filtersTableOptions: ColumnFiltersOptions<TData>;
} {
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]); // can set initial column filter state here

  const filtersTableOptions = enabled
    ? {
        getFilteredRowModel: getFilteredRowModel<TData>(),
        getFacetedRowModel: getFacetedRowModel<TData>(),
        getFacetedUniqueValues: getFacetedUniqueValues<TData>(),
        getFacetedMinMaxValues: getFacetedMinMaxValues<TData>(),
        filterFns: {
          substring: (
            row: Row<TData>,
            columnId: string,
            value: string,
            addMeta: (meta: FilterMeta) => void
          ): boolean => {
            return row.getValue(columnId)?.toString().includes(value) ?? false;
          },
        },
        onColumnFiltersChange: setColumnFilters,
      }
    : {};

  return {
    columnFilters,
    columnFiltersState: {
      columnFilters,
    },
    filtersTableOptions,
    setColumnFilters,
  };
}

export interface FilterProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  header: Header<unknown[], unknown>;
}

export const Filter: FC<FilterProps> = ({ header, className, ...props }) => {
  const typeHint = header.column.columnDef.meta?.typeHint;

  // Do not filter on unknown types
  if (!typeHint) return null;

  // Do not filter on html types
  if (typeHint.type === "html") return null;

  if (typeHint.type === "numeric") {
    const [from, to] = (header.column.getFilterValue() as
      | FilterValueNumeric
      | [undefined, undefined]
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
      // If there was a value and now there isn't,
      // set the filter value to `""` and not `undefined`.
      // `undefined` will not clear the displayed value.
      value={(header.column.getFilterValue() as string) || ""}
      className={`form-control form-control-sm ${className}`}
      type="text"
      onChange={(e) => header.column.setFilterValue(e.target.value)}
    />
  );
};
