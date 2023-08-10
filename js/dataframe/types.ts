import { SelectionMode } from "./selection";

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
  row_selection_mode?: SelectionMode;
  filters?: boolean;
  width?: string;
  height?: string;
}

export interface PandasData<TIndex> {
  columns: ReadonlyArray<string>;
  index: ReadonlyArray<TIndex>;
  data: unknown[][];
  type_hints?: ReadonlyArray<TypeHint>;
  options: DataGridOptions;
}
