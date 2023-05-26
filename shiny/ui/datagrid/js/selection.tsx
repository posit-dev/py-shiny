import * as React from "react";
import { useMemo, useState } from "react";

export interface SelectionSet<TKey, TElement extends HTMLElement> {
  has(key: TKey): boolean;
  set(key: TKey, selected: boolean): void;
  clear(): void;
  handlers(): {
    onMouseDown: (event: React.MouseEvent<TElement, MouseEvent>) => void;
  };
}

export enum SelectionMode {
  None = 0,
  Single,
  Multi,
  MultiSet,
}

export function useSelection<TKey, TElement extends HTMLElement>(
  mode: SelectionMode,
  keyAccessor: (el: TElement) => TKey,
  between?: (from: TKey, to: TKey) => ReadonlyArray<TKey>,
  selectionClassName = "selected"
): SelectionSet<TKey, TElement> {
  const [selectedKeys, setSelectedKeys] = useState<ImmutableSet<TKey>>(
    ImmutableSet.empty()
  );
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

class ImmutableSet<T> {
  private _set: Set<T>;

  private constructor(set: Set<T>) {
    this._set = set;
  }

  static empty<T>(): ImmutableSet<T> {
    return new ImmutableSet(new Set());
  }

  has(value: T): boolean {
    return this._set.has(value);
  }

  add(...values: T[]): ImmutableSet<T> {
    const newSet = new Set(this._set.keys());
    for (const value of values) {
      newSet.add(value);
    }
    return new ImmutableSet(newSet);
  }

  toggle(value: T): ImmutableSet<T> {
    if (this.has(value)) {
      return this.delete(value);
    } else {
      return this.add(value);
    }
  }

  delete(value: T): ImmutableSet<T> {
    const newSet = new Set(this._set.keys());
    newSet.delete(value);
    return new ImmutableSet(newSet);
  }

  clear(): ImmutableSet<T> {
    return ImmutableSet.empty();
  }
}
function performMouseDownAction<TKey, TElement>(
  mode: SelectionMode,
  between: (from: TKey, to: TKey) => readonly TKey[],
  selectedKeys: ImmutableSet<TKey>,
  event: React.MouseEvent<TElement, MouseEvent>,
  key: TKey,
  anchor: TKey | null
): { selection: ImmutableSet<TKey>; anchor?: TKey | null } {
  let { shiftKey, ctrlKey, altKey, metaKey } = event;
  if (window.navigator.platform.match(/^Mac/)) {
    [ctrlKey, metaKey] = [metaKey, ctrlKey];
  }

  if (mode === SelectionMode.MultiSet) {
    return { selection: selectedKeys.toggle(key) };
  } else if (mode === SelectionMode.Single) {
    return { selection: ImmutableSet.empty<TKey>().add(key) };
  } else if (mode === SelectionMode.Multi) {
    if (ctrlKey && !shiftKey) {
      // Ctrl-click: toggle the current row and make it anchor
      return { selection: selectedKeys.toggle(key), anchor: key };
    } else if (shiftKey && !ctrlKey) {
      // Shift-click: replace selection with anchor row through current row
      if (anchor !== null && between) {
        const toSelect = between(anchor, key);
        return { selection: ImmutableSet.empty<TKey>().add(...toSelect) };
      }
    } else if (shiftKey && ctrlKey) {
      // Ctrl-Shift-click: Add anchor row through current row to selection
      const toSelect = between(anchor, key);
      return { selection: selectedKeys.add(...toSelect) };
    } else if (!shiftKey && !ctrlKey) {
      // Regular click: Select the current row and make it anchor
      return { selection: ImmutableSet.empty<TKey>().add(key), anchor: key };
    } else {
      return;
    }
    event.preventDefault();
  }
}
