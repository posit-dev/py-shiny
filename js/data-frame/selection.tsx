import * as React from "react";
import { useState } from "react";
import { ImmutableSet } from "./immutable-set";

import { CellStateClassEnum, CellStateEnum } from "./cell";
import type { ValueOf } from "./types";

type CellSelectionNone = { type: "none" };
type CellSelectionRow = { type: "row"; rows: readonly number[] };
type CellSelectionCol = { type: "col"; cols: readonly number[] };
type CellSelectionRect = {
  type: "rect";
  rows: readonly [number, number];
  cols: readonly [number, number];
};

// For sending and receiving selection info to python
export type CellSelection =
  | CellSelectionNone
  | CellSelectionRow
  | CellSelectionCol
  | CellSelectionRect;

export interface SelectionSet<TKey, TElement extends HTMLElement> {
  has(key: TKey): boolean;
  set(key: TKey, selected: boolean): void;
  setMultiple(key_arr: TKey[]): void;
  clear(): void;
  keys(): ImmutableSet<TKey>;
  itemHandlers(): {
    onMouseDown: (event: React.MouseEvent<TElement, MouseEvent>) => void;
    onKeyDown: (event: React.KeyboardEvent<TElement>) => void;
  };
  focusOffset: (start: TKey, offset: number) => TKey | null;
}

// Keep as strings (and not pointer types) as this is a shape defined by the python side
export type SelectionModesProp = {
  row: "none" | "single" | "multiple";
  col: "none" | "single" | "multiple";
  rect: "none" | "cell" | "region";
};
export class SelectionModes {
  static readonly _NONE = "none";
  static readonly _ROW_SINGLE = "single";
  static readonly _ROW_MULTIPLE = "multiple";
  static readonly _COL_SINGLE = "single";
  static readonly _col_multiple = "multiple";
  static readonly _RECT_CELL = "cell";
  static readonly _RECT_REGION = "region";

  static readonly _rowEnum = {
    NONE: SelectionModes._NONE,
    SINGLE: SelectionModes._ROW_SINGLE,
    MULTIPLE: SelectionModes._ROW_MULTIPLE,
  } as const;
  static readonly _colEnum = {
    NONE: SelectionModes._NONE,
    SINGLE: SelectionModes._COL_SINGLE,
    MULTIPLE: SelectionModes._col_multiple,
  } as const;
  static readonly _rectEnum = {
    NONE: SelectionModes._NONE,
    REGION: SelectionModes._RECT_REGION,
    CELL: SelectionModes._RECT_CELL,
  } as const;

  row: ValueOf<typeof SelectionModes._rowEnum>;
  col: ValueOf<typeof SelectionModes._colEnum>;
  rect: ValueOf<typeof SelectionModes._rectEnum>;

  constructor({
    row,
    col,
    rect,
  }: {
    row: SelectionModesProp["row"];
    col: SelectionModesProp["col"];
    rect: SelectionModesProp["rect"];
  }) {
    if (!Object.values(SelectionModes._rowEnum).includes(row)) {
      throw new Error(`Invalid row selection mode: ${row}`);
    }
    if (!Object.values(SelectionModes._colEnum).includes(col)) {
      throw new Error(`Invalid col selection mode: ${col}`);
    }
    if (!Object.values(SelectionModes._rectEnum).includes(rect)) {
      throw new Error(`Invalid rect selection mode: ${rect}`);
    }
    this.row = row;
    this.col = col;
    this.rect = rect;
  }

  isNone(): boolean {
    return (
      this.row === SelectionModes._rowEnum.NONE &&
      this.col === SelectionModes._colEnum.NONE &&
      this.rect === SelectionModes._rectEnum.NONE
    );
  }
}

export function initSelectionModes(
  selectionModesOption: SelectionModesProp | undefined
): SelectionModes {
  // If no option was provided, default to multinative mode
  if (!selectionModesOption) {
    selectionModesOption = { row: "multiple", col: "none", rect: "none" };
  }
  return new SelectionModes({
    row: selectionModesOption.row,
    col: selectionModesOption.col,
    rect: selectionModesOption.rect,
  });
}

export function useSelection<TKey, TElement extends HTMLElement>({
  isEditingCell,
  editCellsIsAllowed,
  selectionModes,
  keyAccessor,
  focusOffset,
  focusEscape,
  onKeyDownEnter,
  between,
}: {
  // cellBeingEdited: { rowIndex: number; columnIndex: number } | null;
  isEditingCell: boolean;
  editCellsIsAllowed: boolean;
  selectionModes: SelectionModes;
  keyAccessor: (el: TElement) => TKey;
  focusOffset: (start: TKey, offset: number) => TKey | null;
  focusEscape: (el: TElement) => void;
  onKeyDownEnter: (el: TElement) => void;
  between: (from: TKey, to: TKey) => ReadonlyArray<TKey>;
}): SelectionSet<TKey, TElement> {
  const [selectedKeys, setSelectedKeys] = useState<ImmutableSet<TKey>>(
    ImmutableSet.empty()
  );

  // The anchor is the item that was most recently selected with a click or ctrl-click,
  // and is used to determine the "other end" of a shift-click selection operation.
  const [anchor, setAnchor] = useState<TKey | null>(null);

  const onMouseDown = (event: React.MouseEvent<TElement, MouseEvent>): void => {
    if (selectionModes.isNone()) {
      return;
    }

    const el = event.currentTarget as TElement;
    const key = keyAccessor(el);
    if (isEditingCell) {
      // Only quit early if that cell is in edit mode
      if (el.classList.contains(CellStateClassEnum[CellStateEnum.Editing])) {
        return;
      }
    }

    const result = performMouseDownAction<TKey, TElement>(
      selectionModes,
      between,
      selectedKeys,
      event,
      key,
      anchor
    );
    if (result) {
      setSelectedKeys(result.selection);
      if (result.anchor) {
        setAnchor(key);
        el.focus();
      }
      event.preventDefault();
    }
  };

  const onKeyDown = (event: React.KeyboardEvent<TElement>): void => {
    if (isEditingCell) {
      return;
    }
    if (selectionModes.isNone()) {
      return;
    }

    const el = event.currentTarget as TElement;
    const key = keyAccessor(el);
    const selected = selectedKeys.has(key);

    if (event.key === "Escape") {
      focusEscape(el);
      event.preventDefault();
      return;
    }

    // For both row and rows, do not allow for alphanumeric keys to trigger edit mode.
    // Only allow for this once the anchor is a single cell, such as region selection.
    // For region selection, allow for alphanumeric keys to trigger edit mode of current cell.
    // For region selection, allow for enter key to trigger edit mode of current cell.

    if (selectionModes.row === SelectionModes._rowEnum.SINGLE) {
      if (event.key === " " || event.key === "Enter") {
        event.preventDefault();
        if (editCellsIsAllowed && event.key === "Enter") {
          onKeyDownEnter(el);
        } else {
          if (selectedKeys.has(key)) {
            setSelectedKeys(ImmutableSet.empty());
          } else {
            setSelectedKeys(ImmutableSet.just(key));
          }
        }
      } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
        const targetKey = focusOffset(key, event.key === "ArrowUp" ? -1 : 1);
        if (targetKey) {
          event.preventDefault();
          if (selected) {
            setSelectedKeys(ImmutableSet.just(targetKey));
          }
        }
      }
    } else if (selectionModes.row === SelectionModes._rowEnum.MULTIPLE) {
      if (event.key === " " || event.key === "Enter") {
        event.preventDefault();
        if (editCellsIsAllowed && event.key === "Enter") {
          onKeyDownEnter(el);
        } else {
          setSelectedKeys(selectedKeys.toggle(key));
        }
      } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
        if (focusOffset(key, event.key === "ArrowUp" ? -1 : 1)) {
          event.preventDefault();
        }
      }
    }
  };

  const selection = {
    has(key: TKey): boolean {
      return selectedKeys.has(key);
    },

    set(key: TKey, selected: boolean) {
      if (selected) {
        setSelectedKeys(selectedKeys.add(key));
      } else {
        setSelectedKeys(selectedKeys.delete(key));
      }
    },

    setMultiple(keyArr: TKey[]) {
      setSelectedKeys(ImmutableSet.just(...keyArr));
    },

    clear() {
      setSelectedKeys(selectedKeys.clear());
    },

    keys() {
      return selectedKeys;
    },

    itemHandlers() {
      return { onMouseDown, onKeyDown };
    },

    focusOffset,
  };

  return selection;
}

declare global {
  interface Navigator {
    readonly userAgentData?: NavigatorUAData;
  }
  interface NavigatorUAData {
    readonly brands?: { brand: string; version: string }[];
    readonly mobile?: boolean;
    readonly platform?: string;
  }
}

const isMac = /^mac/i.test(
  window.navigator.userAgentData?.platform ?? window.navigator.platform
);

function performMouseDownAction<TKey, TElement>(
  selectionModes: SelectionModes,
  between: ((from: TKey, to: TKey) => readonly TKey[]) | undefined,
  selectedKeys: ImmutableSet<TKey>,
  event: React.MouseEvent<TElement, MouseEvent>,
  key: TKey,
  anchor: TKey | null
): { selection: ImmutableSet<TKey>; anchor?: true } | null {
  const { shiftKey, altKey } = event;
  const ctrlKey = isMac ? event.metaKey : event.ctrlKey;
  const metaKey = isMac ? event.ctrlKey : event.metaKey;

  if (metaKey || altKey) {
    return null;
  }

  if (selectionModes.row === SelectionModes._rowEnum.NONE) {
    return null;
  } else if (selectionModes.row === SelectionModes._rowEnum.SINGLE) {
    if (ctrlKey && !shiftKey) {
      // Ctrl-click is like simple click, except it removes selection if an item is
      // already selected
      if (selectedKeys.has(key)) {
        return { selection: ImmutableSet.empty(), anchor: true };
      } else {
        return { selection: ImmutableSet.just(key), anchor: true };
      }
    } else {
      // Simple click sets selection, always
      return { selection: ImmutableSet.just(key), anchor: true };
    }
    // TODO-barret; multinative should be the new definition of `rows`!
  } else if (selectionModes.row === SelectionModes._rowEnum.MULTIPLE) {
    if (shiftKey && ctrlKey) {
      // Ctrl-Shift-click: Add anchor row through current row to selection
      if (anchor !== null && between) {
        const toSelect = between(anchor, key);
        return { selection: selectedKeys.add(...toSelect) };
      }
    } else if (ctrlKey) {
      // Ctrl-click: toggle the current row and make it anchor
      return { selection: selectedKeys.toggle(key), anchor: true };
    } else if (shiftKey) {
      // Shift-click: replace selection with anchor row through current row
      if (anchor !== null && between) {
        const toSelect = between(anchor, key);
        return { selection: ImmutableSet.just(...toSelect) };
      }
    } else {
      // Regular click: Select the current row and make it anchor
      return { selection: ImmutableSet.just(key), anchor: true };
    }
  } else {
    throw new Error(`Unsupported row selection mode: ${selectionModes.row}`);
  }
  return null;
}
