import * as React from "react";
import { useState } from "react";
import { ImmutableSet } from "./immutable-set";

import type { ValueOf } from "./types";

type BrowserCellSelectionNone = { type: "none" };
type BrowserCellSelectionRow = { type: "row"; rows: readonly number[] };
type BrowserCellSelectionCol = { type: "col"; cols: readonly number[] };
type BrowserCellSelectionRegion = {
  type: "region";
  rows: readonly [number, number];
  cols: readonly [number, number];
};

// For sending and receiving selection info to python
export type BrowserCellSelection =
  | BrowserCellSelectionNone
  | BrowserCellSelectionRow
  | BrowserCellSelectionCol
  | BrowserCellSelectionRegion;

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
}

// Keep as strings (and not pointer types) as this is a shape defined by the python side
export type SelectionModesProp = {
  row: "none" | "single" | "multiple";
  col: "none" | "single" | "multiple";
  rect: "none" | "region" | "cell";
};
export class SelectionModes {
  static readonly _NONE = "none";
  static readonly _ROW_SINGLE = "single";
  static readonly _ROW_MULTIPLE = "multiple";
  static readonly _COL_SINGLE = "single";
  static readonly _col_multiple = "multiple";
  static readonly _RECT_REGION = "region";
  static readonly _RECT_CELL = "cell";

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

  is_none(): boolean {
    return (
      this.row === SelectionModes._rowEnum.NONE &&
      this.col === SelectionModes._colEnum.NONE &&
      this.rect === SelectionModes._rectEnum.NONE
    );
  }
}

export function initRowSelectionModes(
  selectionModesOption: SelectionModesProp | undefined
): SelectionModes {
  // If no option was provided, default to multinative mode
  if (!selectionModesOption) {
    selectionModesOption = { row: "multi-native", col: "none", rect: "none" };
  }
  return new SelectionModes({
    row: selectionModesOption.row,
    col: selectionModesOption.col,
    rect: selectionModesOption.rect,
  });
}

export function useSelection<TKey, TElement extends HTMLElement>(
  selectionModes: SelectionModes,
  keyAccessor: (el: TElement) => TKey,
  focusOffset: (start: TKey, offset: number) => TKey | null,
  between?: (from: TKey, to: TKey) => ReadonlyArray<TKey>
): SelectionSet<TKey, TElement> {
  const [selectedKeys, setSelectedKeys] = useState<ImmutableSet<TKey>>(
    ImmutableSet.empty()
  );

  // The anchor is the item that was most recently selected with a click or ctrl-click,
  // and is used to determine the "other end" of a shift-click selection operation.
  const [anchor, setAnchor] = useState<TKey | null>(null);

  const onMouseDown = (event: React.MouseEvent<TElement, MouseEvent>): void => {
    if (selectionModes.is_none()) {
      return;
    }

    const el = event.currentTarget as TElement;
    const key = keyAccessor(el);

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
    if (selectionModes.is_none()) {
      return;
    }

    const el = event.currentTarget as TElement;
    const key = keyAccessor(el);
    const selected = selectedKeys.has(key);

    if (selectionModes.row === SelectionModes._rowEnum.SINGLE) {
      if (event.key === " " || event.key === "Enter") {
        if (selectedKeys.has(key)) {
          setSelectedKeys(ImmutableSet.empty());
        } else {
          setSelectedKeys(ImmutableSet.just(key));
        }
        event.preventDefault();
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
        setSelectedKeys(selectedKeys.toggle(key));
        event.preventDefault();
      } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
        if (focusOffset(key, event.key === "ArrowUp" ? -1 : 1)) {
          event.preventDefault();
        }
      }
    }
  };

  return {
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

    setMultiple(key_arr: TKey[]) {
      setSelectedKeys(ImmutableSet.just(...key_arr));
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
  };
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
    if (selectedKeys.has(key)) {
      // If the item is already selected, clicking on it again should clear the selection
      return { selection: ImmutableSet.empty(), anchor: true };
    } else {
      // Simple click sets selection
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
