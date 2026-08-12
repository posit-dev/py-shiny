import { StyleInfo } from "./style-info";

import type { ColumnDef, ColumnMeta } from "@tanstack/react-table";
import type { HtmlDep } from "rstudio-shiny/srcts/types/src/shiny/render";

export type ValueOf<T> = T[keyof T];

export const EditModeEnum = {
  None: "none",
  Edit: "edit",
} as const;
export type EditMode = ValueOf<typeof EditModeEnum>;

export interface TypeHint {
  type:
    | "string"
    | "numeric"
    | "boolean"
    | "date"
    | "datetime"
    | "duration"
    | "object"
    | "unknown"
    | "html"
    | "categorical";
}

export interface CategoricalTypeHint extends TypeHint {
  type: "categorical";
  categories: ReadonlyArray<string>;
}

export interface DataGridOptions {
  style?: "table" | "grid";
  summary?: boolean | string;
  filters?: boolean;
  width?: string;
  height?: string;
  fill?: boolean;
  styles?: StyleInfo[];
  editable?: boolean;
}

export interface PandasData<TIndex> {
  columns: ReadonlyArray<string>;
  // index: ReadonlyArray<TIndex>;
  data: unknown[][];
  options: DataGridOptions;
  typeHints?: ReadonlyArray<TypeHint>;
  htmlDeps?: ReadonlyArray<HtmlDep>;
}

export interface PatchInfo {
  key: string;
}

/**
 * A column definition carrying the fields that this data frame always sets.
 *
 * `id` and `meta` are both optional on TanStack Table's `ColumnDef`, but every
 * column definition built in `index.tsx` provides them. Requiring them here
 * lets consumers read the fields without a non-null assertion, which would
 * otherwise silently degrade to a no-op if a column definition ever stopped
 * setting one -- e.g. the html-column sort guard in `sort.ts` would collect a
 * set of `undefined` and quietly stop guarding anything.
 */
export type DataFrameColumnDef = ColumnDef<unknown[], unknown> & {
  id: string;
  meta: ColumnMeta<unknown[], unknown>;
};
