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
  filters?: boolean;
  width?: string;
  height?: string;
  fill?: boolean;
}

export interface PandasData<TIndex> {
  columns: ReadonlyArray<string>;
  // index: ReadonlyArray<TIndex>;
  data: unknown[][];
  options: DataGridOptions;
  typeHints?: ReadonlyArray<TypeHint>;
  editable?: boolean;
  htmlColumns?: ReadonlyArray<number>;
}

export interface PatchInfo {
  key: string;
}
