import { VirtualItem } from "@tanstack/react-virtual";
import React, { useMemo } from "react";

/**
 * Create a summary
 *
 * @param summaryTemplate A string with "{start}", "{end}", and "{total}"
 * @param scrollContainer Scrolling container of the table/grid
 * @param virtualRows VirtualItem objects that might currently be visible
 * @param thead The thead tag of the table
 * @param nrows Number of total rows of data that exist
 */
export function useSummary(
  summaryTemplate: string | boolean | undefined,
  scrollContainer: HTMLElement | null,
  virtualRows: VirtualItem<Element>[],
  thead: HTMLTableSectionElement | null,
  nrows: number
): JSX.Element | null {
  return useMemo(() => {
    const summaryOption = summaryTemplate ?? true;
    if (!summaryOption) {
      return null;
    }

    const template =
      typeof summaryOption === "string"
        ? summaryOption
        : "Viewing rows {start} through {end} of {total}";

    if (!scrollContainer) {
      return null;
    }
    if (virtualRows.length === 0) {
      return null;
    }

    if (!thead) return null;

    const top = scrollContainer.scrollTop + thead.clientHeight;
    const bot = scrollContainer.scrollTop + scrollContainer.clientHeight;

    const [firstIndex, lastIndex] = findRangeIndex(
      top,
      bot,
      virtualRows,
      (vrow, start) => vrow.start + vrow.size / 2
    );

    if (firstIndex === null || lastIndex === null) {
      // Something must've gone wrong if there are rows but none of them are within the
      // visible scroll area... shrug
      return null;
    }

    const firstRow = virtualRows[firstIndex];
    const lastRow = virtualRows[lastIndex];

    if (firstRow === undefined || lastRow === undefined) {
      // This should never happen, but just in case...
      return null;
    }

    if (firstRow.index === 0 && lastRow.index === nrows - 1) {
      // Viewing all rows; no need for a summary
      return null;
    }

    const summaryMessage = formatSummary(
      template,
      firstRow.index + 1,
      lastRow.index + 1,
      nrows
    );

    return <div className="shiny-data-grid-summary">{summaryMessage}</div>;
  }, [summaryTemplate, scrollContainer, virtualRows, thead, nrows]);
}

/**
 * Find the subset of (sorted) items that are between start and end (inclusive), where
 * each item's value to compare is calculated by a mapping function. The mapping
 * function may behave differently when comparing to start vs. end.
 *
 * @param start The smallest value to include.
 * @param end The largest value to include.
 * @param items A set of items to be evaluated, in sorted order.
 * @param map A function for converting from an item to a comparison value; for example,
 *   if 'start' and 'end' are vertical pixel coordinates, then the function might
 *   return the item's vertical top (for start) or bottom (for end) coordinate.
 * @returns The start and end indexes into the 'items' array indicating the first and
 *   last item that is included.
 */
function findRangeIndex<TItem>(
  start: number,
  end: number,
  items: TItem[],
  map: (x: TItem, start: boolean) => number
): [first: number | null, last: number | null] {
  let first: number | null = null;
  let last: number | null = null;

  for (let i = 0; i < items.length; i++) {
    const item: TItem = items[i]!;
    if (first === null) {
      if (map(item, true) >= start) {
        first = i;
        last = i;
      }
    } else {
      if (map(item, false) <= end) {
        last = i;
      } else {
        break;
      }
    }
  }

  return [first, last];
}

function formatSummary(
  template: string,
  start: number,
  end: number,
  total: number
) {
  return template.replace(/\{(start|end|total)\}/g, (substr, token) => {
    if (token === "start") {
      return start + "";
    } else if (token === "end") {
      return end + "";
    } else if (token === "total") {
      return total + "";
    } else {
      return substr;
    }
  });
}
