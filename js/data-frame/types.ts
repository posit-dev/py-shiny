import { StyleInfo } from "./style-info";

export type ValueOf<T> = T[keyof T];

export const EditModeEnum = {
  None: "none",
  Edit: "edit",
} as const;
export type EditMode = ValueOf<typeof EditModeEnum>;

export interface TypeHint {
  type: "string" | "numeric" | "categorical" | "unknown" | "html";
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
}

export interface PatchInfo {
  key: string;
}
