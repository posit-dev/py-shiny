import { SelectionMode } from "./selection";

export enum EditMode {
  None = "none",
  Edit = "edit",
}

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
  // row_selection_mode?: SelectionMode;
  // editable?: boolean;
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
