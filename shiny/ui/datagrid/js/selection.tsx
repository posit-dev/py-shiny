import * as React from "react";
import { useState } from "react";
import { ImmutableSet } from "./immutable-set";

export interface SelectionSet<TKey, TElement extends HTMLElement> {
  has(key: TKey): boolean;
  set(key: TKey, selected: boolean): void;
  clear(): void;
  handlers(): {
    onMouseDown: (event: React.MouseEvent<TElement, MouseEvent>) => void;
  };
}

export enum SelectionMode {
  None = "none",
  Single = "single",
  Multi = "multi",
  MultiSet = "multi-set",
}

export function useSelection<TKey, TElement extends HTMLElement>(
  mode: SelectionMode,
  keyAccessor: (el: TElement) => TKey,
  between?: (from: TKey, to: TKey) => ReadonlyArray<TKey>
): SelectionSet<TKey, TElement> {
  const [selectedKeys, setSelectedKeys] = useState<ImmutableSet<TKey>>(
    ImmutableSet.empty()
  );

  // The anchor is the item that was most recently selected with a click or ctrl-click,
  // and is used to determine the "other end" of a shift-click selection operation.
  const [anchor, setAnchor] = useState<TKey | null>(null);

  const onMouseDown = (event: React.MouseEvent<TElement, MouseEvent>): void => {
    if (mode === SelectionMode.None) {
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
      if (typeof result.anchor !== "undefined") {
        setAnchor(result.anchor);
      }
      event.preventDefault();
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

    clear() {
      setSelectedKeys(selectedKeys.clear());
    },

    handlers() {
      return { onMouseDown };
    },
  };
}

const isMac = /^Mac/.test(window.navigator.platform);

function performMouseDownAction<TKey, TElement>(
  mode: SelectionMode,
  between: (from: TKey, to: TKey) => readonly TKey[],
  selectedKeys: ImmutableSet<TKey>,
  event: React.MouseEvent<TElement, MouseEvent>,
  key: TKey,
  anchor: TKey | null
): { selection: ImmutableSet<TKey>; anchor?: TKey | null } {
  const { shiftKey, altKey } = event;
  const ctrlKey = isMac ? event.metaKey : event.ctrlKey;
  const metaKey = isMac ? event.ctrlKey : event.metaKey;

  if (metaKey || altKey) {
    return null;
  }

  if (mode === SelectionMode.MultiSet) {
    return { selection: selectedKeys.toggle(key) };
  } else if (mode === SelectionMode.Single) {
    return { selection: ImmutableSet.empty<TKey>().add(key) };
  } else if (mode === SelectionMode.Multi) {
    if (shiftKey && ctrlKey) {
      // Ctrl-Shift-click: Add anchor row through current row to selection
      const toSelect = between(anchor, key);
      return { selection: selectedKeys.add(...toSelect) };
    } else if (ctrlKey) {
      // Ctrl-click: toggle the current row and make it anchor
      return { selection: selectedKeys.toggle(key), anchor: key };
    } else if (shiftKey) {
      // Shift-click: replace selection with anchor row through current row
      if (anchor !== null && between) {
        const toSelect = between(anchor, key);
        return { selection: ImmutableSet.empty<TKey>().add(...toSelect) };
      }
    } else {
      // Regular click: Select the current row and make it anchor
      return { selection: ImmutableSet.empty<TKey>().add(key), anchor: key };
    }
  }
}
