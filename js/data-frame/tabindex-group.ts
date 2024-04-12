import React, { useState } from "react";
import { findFirstItemInView } from "./dom-utils";

export interface TabindexGroup<TElement extends HTMLElement> {
  containerTabIndex: number;
  containerHandlers: {
    onFocus: (event: React.FocusEvent<TElement>) => void;
    onBlur: (event: React.FocusEvent<TElement>) => void;
  };
}

export function useTabindexGroup<TContainerElement extends HTMLElement>(
  container: TContainerElement | null,
  focusableItems: () => NodeList,
  extraPadding?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  }
): TabindexGroup<TContainerElement> {
  const [tabIndex, setTabIndex] = useState(0);

  const onFocus = React.useCallback(
    (event: React.FocusEvent<TContainerElement>) => {
      // When focus is within (or on, but we only really care about within) the
      // container, remove it from the tab order. If we don't set the tab stop to -1,
      // then the logic below (that, on container focus, moves focus to the first item)
      // causes Shift-Tab from a focused item to break, as focus moves to the container
      // and then (back) to the first item.
      setTabIndex(-1);

      if (event.target !== event.currentTarget) {
        // Not interested in capturing, only care about focus on the container itself
        return;
      }

      findFirstItemInView(container!, focusableItems(), extraPadding)?.focus();
    },
    [container, focusableItems, extraPadding]
  );

  const onBlur = React.useCallback(
    (event: React.FocusEvent<TContainerElement>) => {
      setTabIndex(0);
    },
    []
  );

  return {
    containerTabIndex: tabIndex,
    containerHandlers: {
      onFocus,
      onBlur,
    },
  };
}
