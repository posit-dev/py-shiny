import { SelectionMode } from "./selection";

export type ValueOf<T> = T[keyof T];

export const EditModeEnum = {
  None: "none",
  Edit: "edit",
} as const;
export type EditMode = ValueOf<typeof EditModeEnum>;

export interface TypeHint {
  type: "string" | "numeric" | "categorical" | "unknown";
}

export interface CategoricalTypeHint extends TypeHint {
  type: "categorical";
  categories: ReadonlyArray<string>;
}

export interface DataGridOptions {
  style?: "table" | "grid";
  summary?: boolean | string;
  mode?: SelectionMode | EditMode;
  filters?: boolean;
  width?: string;
  height?: string;
  fill?: boolean;
}

export interface PandasData<TIndex> {
  columns: ReadonlyArray<string>;
  // index: ReadonlyArray<TIndex>;
  data: unknown[][];
  type_hints?: ReadonlyArray<TypeHint>;
  options: DataGridOptions;
}
