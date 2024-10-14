import { StyleInfo } from "./style-info";

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
