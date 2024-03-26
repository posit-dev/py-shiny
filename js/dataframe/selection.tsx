import * as React from "react";
import { useState } from "react";
import { ImmutableSet } from "./immutable-set";

import type { ValueOf } from "./types";

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

export const SelectionModeEnum = {
  None: "none",
  Single: "single_row",
  Multiple: "multiple_row",
  MultiNative: "multi-native_row",
} as const;
const selectionModes = Object.values(SelectionModeEnum);
export type SelectionMode = ValueOf<typeof SelectionModeEnum>;

export function initRowSelectionMode(
  mode_option: string | undefined
): SelectionMode {
  // If no option was provided, default to multinative mode
  const selectionMode = mode_option ?? SelectionModeEnum.MultiNative;

  // If a row selection mode matches one of the enum values, use it. Otherwise, fall back to none (e.g. `dataFrameMode == "edit"`).
  if (!selectionModes.includes(selectionMode as SelectionMode)) {
    return SelectionModeEnum.None;
  } else {
    return selectionMode as SelectionMode;
  }
}

export function useSelection<TKey, TElement extends HTMLElement>(
  mode: SelectionMode,
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
    if (mode === SelectionModeEnum.None) {
      return;
    }

    const el = event.currentTarget as TElement;
    const key = keyAccessor(el);

    const result = performMouseDownAction<TKey, TElement>(
      mode,
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
    if (mode === SelectionModeEnum.None) {
      return;
    }

    const el = event.currentTarget as TElement;
    const key = keyAccessor(el);
    const selected = selectedKeys.has(key);

    if (mode === SelectionModeEnum.Single) {
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
    } else if (mode === SelectionModeEnum.Multiple) {
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
  mode: SelectionMode,
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

  if (mode === SelectionModeEnum.Multiple) {
    return { selection: selectedKeys.toggle(key), anchor: true };
  } else if (mode === SelectionModeEnum.Single) {
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
  } else if (mode === SelectionModeEnum.MultiNative) {
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
  }
  return null;
}
