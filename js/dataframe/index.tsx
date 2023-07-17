import css from "./styles.scss";

import {
  Column,
  ColumnDef,
  RowData,
  RowModel,
  TableOptions,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { Virtualizer, useVirtualizer } from "@tanstack/react-virtual";
import React, {
  FC,
  StrictMode,
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
} from "react";
import { Root, createRoot } from "react-dom/client";
import { ErrorsMessageValue } from "rstudio-shiny/srcts/types/src/shiny/shinyapp";
import { findFirstItemInView, getStyle } from "./dom-utils";
import { Filter, useFilter } from "./filter";
import { SelectionMode, useSelection } from "./selection";
import { SortArrow } from "./sort-arrows";
import { useTabindexGroup } from "./tabindex-group";
import { useSummary } from "./table-summary";
import { PandasData, TypeHint } from "./types";

declare module "@tanstack/table-core" {
  interface ColumnMeta<TData extends RowData, TValue> {
    typeHint: TypeHint;
  }
}
// TODO: Right-align numeric columns, maybe change font
// TODO: Explicit column widths
// TODO: Filtering
// TODO: Editing
// TODO: Pagination
// TODO: Range selection + copying
// TODO: Find
// TODO: Server-side mode (don't pull all data to client at once)
// TODO: Localization of summary
// TODO: Accessibility review
// TODO: Drag to resize columns
// TODO: Drag to resize table/grid
// TODO: Row numbers

interface ShinyDataGridProps<TIndex> {
  id: string | null;
  data: PandasData<TIndex>;
  bgcolor?: string;
}

const ShinyDataGrid: FC<ShinyDataGridProps<unknown>> = (props) => {
  const { id, data, bgcolor } = props;
  const { columns, index, type_hints, data: rowData } = data;
  const { width, height, filters: withFilters } = data.options;
  const keyToIndex: Record<string, unknown> = {};
  index.forEach((value) => {
    keyToIndex[value + ""] = value;
  });

  const containerRef = useRef<HTMLDivElement>(null);
  const theadRef = useRef<HTMLTableSectionElement>(null);
  const tbodyRef = useRef<HTMLTableSectionElement>(null);

  const coldefs = useMemo<ColumnDef<unknown[], unknown>[]>(
    () =>
      columns.map((colname, i) => {
        const typeHint = type_hints?.[i];

        return {
          accessorFn: (row, index) => {
            return row[i];
          },
          // TODO: delegate this decision to something in filter.tsx
          filterFn:
            typeHint.type === "numeric" ? "inNumberRange" : "includesString",
          header: colname,
          meta: {
            typeHint: typeHint,
          },
        };
      }),
    [columns]
  );

  // Not sure if it's even necessary to clone
  const dataClone = useMemo(() => [...rowData], [rowData]);

  const filterOpts = useFilter<unknown[]>(withFilters);

  const options: TableOptions<unknown[]> = {
    data: dataClone,
    columns: coldefs,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    ...filterOpts,
    //debugAll: true,
  };
  const table = useReactTable(options);

  const rowVirtualizer = useVirtualizer({
    count: table.getFilteredRowModel().rows.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 31,
    paddingStart: theadRef.current?.clientHeight ?? 0,
    // In response to https://github.com/rstudio/py-shiny/pull/538/files#r1228352446
    // (the default scrollingDelay is 150)
    scrollingDelay: 10,
  });

  // Reset scroll when dataset changes
  useLayoutEffect(() => {
    rowVirtualizer.scrollToOffset(0);
  }, [data]);

  const totalSize = rowVirtualizer.getTotalSize();
  const virtualRows = rowVirtualizer.getVirtualItems();

  // paddingTop and paddingBottom are to force the <tbody> to add up to the correct
  // virtual height.
  // paddingTop must subtract out the thead height, since thead is inside the scroll
  // container but not virtualized.
  const paddingTop =
    (virtualRows.length > 0 ? virtualRows?.[0]?.start || 0 : 0) -
      theadRef.current?.clientHeight ?? 0;
  const paddingBottom =
    virtualRows.length > 0
      ? totalSize - (virtualRows?.[virtualRows.length - 1]?.end || 0)
      : 0;

  const summary = useSummary(
    data.options["summary"],
    containerRef?.current,
    virtualRows,
    theadRef.current,
    rowVirtualizer.options.count
  );

  const tableStyle = data.options["style"] ?? "grid";
  const containerClass =
    tableStyle === "grid" ? "shiny-data-grid-grid" : "shiny-data-grid-table";
  const tableClass = tableStyle === "table" ? "table table-sm" : null;

  const rowSelectionMode =
    data.options["row_selection_mode"] ?? SelectionMode.MultiNative;
  const canSelect = rowSelectionMode !== SelectionMode.None;
  const canMultiSelect =
    rowSelectionMode === SelectionMode.MultiNative ||
    rowSelectionMode === SelectionMode.Multiple;

  const rowSelection = useSelection<string, HTMLTableRowElement>(
    rowSelectionMode,
    (el) => el.dataset.key,
    (key, offset) => {
      const rowModel = table.getSortedRowModel();
      let index = rowModel.rows.findIndex((row) => row.id === key);
      if (index < 0) {
        return null;
      }
      index += offset;
      if (index < 0 || index >= rowModel.rows.length) {
        return null;
      }
      const targetKey = rowModel.rows[index].id;
      rowVirtualizer.scrollToIndex(index);
      setTimeout(() => {
        const targetEl = containerRef.current?.querySelector(
          `[data-key='${targetKey}']`
        ) as HTMLElement | null;
        targetEl?.focus();
      }, 0);
      return targetKey;
    },
    (fromKey, toKey) =>
      findKeysBetween(table.getSortedRowModel(), fromKey, toKey)
  );

  useEffect(() => {
    if (id) {
      if (rowSelectionMode === SelectionMode.None) {
        Shiny.setInputValue(`${id}_selected_rows`, null);
      } else {
        Shiny.setInputValue(
          `${id}_selected_rows`,
          rowSelection
            .keys()
            .toList()
            .map((key) => keyToIndex[key])
        );
      }
    }
  }, [[...rowSelection.keys()]]);

  const tbodyTabItems = React.useCallback(
    () => tbodyRef.current.querySelectorAll("[tabindex='-1']"),
    [tbodyRef.current]
  );
  const tbodyTabGroup = useTabindexGroup(containerRef.current, tbodyTabItems, {
    top: theadRef.current?.clientHeight ?? 0,
  });

  // Reset sorting and selection whenever dataset changes. (Should we do this?)
  useEffect(() => {
    return () => {
      table.resetSorting();
      rowSelection.clear();
    };
  }, [data]);

  const headerRowCount = table.getHeaderGroups().length;

  const scrollingClass =
    containerRef.current?.scrollHeight > containerRef.current?.clientHeight
      ? "scrolling"
      : "";

  const makeHeaderKeyDown =
    (column: Column<unknown[], unknown>) => (event: React.KeyboardEvent) => {
      if (event.key === " " || event.key === "Enter") {
        column.toggleSorting(undefined, event.shiftKey);
      }
    };

  const measureEl = useVirtualizerMeasureWorkaround(rowVirtualizer);

  return (
    <>
      <div
        className={`shiny-data-grid ${containerClass} ${scrollingClass}`}
        ref={containerRef}
        style={{ width, maxHeight: height, overflow: "auto" }}
      >
        <table
          className={tableClass + (withFilters ? " filtering" : "")}
          aria-rowcount={rowData.length}
          aria-multiselectable={canMultiSelect}
          style={{ width: width === null || width === "auto" ? null : "100%" }}
        >
          <thead ref={theadRef} style={{ backgroundColor: bgcolor }}>
            {table.getHeaderGroups().map((headerGroup, i) => (
              <tr key={headerGroup.id} aria-rowindex={i + 1}>
                {headerGroup.headers.map((header) => {
                  return (
                    <th
                      key={header.id}
                      colSpan={header.colSpan}
                      style={{ width: header.getSize() }}
                      scope="col"
                      tabIndex={0}
                      onClick={header.column.getToggleSortingHandler()}
                      onKeyDown={makeHeaderKeyDown(header.column)}
                    >
                      {header.isPlaceholder ? null : (
                        <div
                          style={{
                            cursor: header.column.getCanSort()
                              ? "pointer"
                              : null,
                            userSelect: header.column.getCanSort()
                              ? "none"
                              : null,
                          }}
                        >
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                          <SortArrow direction={header.column.getIsSorted()} />
                        </div>
                      )}
                    </th>
                  );
                })}
              </tr>
            ))}
            {withFilters && (
              <tr className="filters">
                {table.getFlatHeaders().map((header) => {
                  return (
                    <th key={`filter-${header.id}`}>
                      <Filter header={header} />
                    </th>
                  );
                })}
              </tr>
            )}
          </thead>
          <tbody
            ref={tbodyRef}
            tabIndex={tbodyTabGroup.containerTabIndex}
            {...tbodyTabGroup.containerHandlers}
          >
            {paddingTop > 0 && <tr style={{ height: `${paddingTop}px` }}></tr>}
            {virtualRows.map((virtualRow) => {
              const row = table.getRowModel().rows[virtualRow.index];
              return (
                row && (
                  <tr
                    key={virtualRow.key}
                    data-index={virtualRow.index}
                    aria-rowindex={virtualRow.index + headerRowCount}
                    data-key={row.id}
                    ref={measureEl}
                    aria-selected={rowSelection.has(row.id)}
                    tabIndex={-1}
                    {...rowSelection.itemHandlers()}
                  >
                    {row.getVisibleCells().map((cell) => {
                      return (
                        <td key={cell.id}>
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </td>
                      );
                    })}
                  </tr>
                )
              );
            })}
            {paddingBottom > 0 && (
              <tr style={{ height: `${paddingBottom}px` }}></tr>
            )}
          </tbody>
        </table>
      </div>
      {summary}
    </>
  );
};

function findKeysBetween<TData>(
  rowModel: RowModel<TData>,
  fromKey: string,
  toKey: string
): readonly string[] {
  let fromIdx = rowModel.rows.findIndex((row) => row.id === fromKey);
  let toIdx = rowModel.rows.findIndex((row) => row.id === toKey);
  if (fromIdx < 0 || toIdx < 0) {
    return [];
  }
  if (fromIdx > toIdx) {
    // Swap order to simplify things
    [fromIdx, toIdx] = [toIdx, fromIdx];
  }
  const keys = [];
  for (let i = fromIdx; i <= toIdx; i++) {
    keys.push(rowModel.rows[i].id);
  }
  return keys;
}

/**
 * Works around a problem where the ref={...} callback is called before the element to
 * be measured is attached to the DOM, which will result in the virtualizer using its
 * estimated size instead of the actual size. This hook will detect when elements that
 * are not yet attached to the DOM are measured, and will retry measuring them in the
 * useEffect.
 * @returns A callback that can be used as a ref for an element that needs to be measured.
 */
function useVirtualizerMeasureWorkaround(
  rowVirtualizer: Virtualizer<HTMLDivElement, Element>
) {
  // Tracks elements that need to be measured, but are not yet attached to the DOM
  const measureTodoQueue = useRef<HTMLElement[]>([]);

  // This is the callback that will be passed back to the caller, intended to be used as
  // a ref for each virtual item's element.
  const measureElementWithRetry = useCallback(
    (el: Element) => {
      if (!el) {
        return;
      }

      if (el.isConnected) {
        rowVirtualizer.measureElement(el);
      } else {
        measureTodoQueue.current.push(el as HTMLElement);
      }
    },
    [rowVirtualizer]
  );

  // Once the DOM is updated, try to measure any elements that were not yet attached
  useLayoutEffect(() => {
    if (measureTodoQueue.current.length > 0) {
      const todo = measureTodoQueue.current.splice(0);
      // The next line can mutate measureTodoQueue.current, hence the need to splice out
      // all the items to work on before actually calling measureElement on any of them.
      todo.forEach(rowVirtualizer.measureElement);
    }
  });

  return measureElementWithRetry;
}

class ShinyDataFrameOutputBinding extends Shiny.OutputBinding {
  find(scope: HTMLElement | JQuery<HTMLElement>): JQuery<HTMLElement> {
    return $(scope).find("shiny-data-frame");
  }

  renderValue(el: ShinyDataFrameOutput, data: unknown): void {
    el.renderValue(data);
  }

  renderError(el: ShinyDataFrameOutput, err: ErrorsMessageValue): void {
    el.classList.add("shiny-output-error");
    el.renderError(err);
  }

  clearError(el: ShinyDataFrameOutput): void {
    el.classList.remove("shiny-output-error");
    el.clearError();
  }
}
Shiny.outputBindings.register(
  new ShinyDataFrameOutputBinding(),
  "shinyDataFrame"
);

function getComputedBgColor(el: HTMLElement | null): string | null | undefined {
  if (!el) {
    // Top of document, can't recurse further
    return null;
  }

  const bgColor = getStyle(el, "background-color");

  if (!bgColor) return bgColor;
  const m = bgColor.match(
    /^rgba\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)$/
  );

  if (bgColor === "transparent" || (m && parseFloat(m[4]) === 0)) {
    // No background color on this element. See if it has a background image.
    const bgImage = getStyle(el, "background-image");

    if (bgImage && bgImage !== "none") {
      // Failed to detect background color, since it has a background image
      return null;
    } else {
      // Recurse
      return getComputedBgColor(el.parentElement);
    }
  }
  return bgColor;
}

const cssTemplate = document.createElement("template");
cssTemplate.innerHTML = `<style>${css}</style>`;

export class ShinyDataFrameOutput extends HTMLElement {
  reactRoot?: Root;
  errorRoot: HTMLSpanElement;

  connectedCallback() {
    // Currently not using shadow DOM since Bootstrap's table styling is pretty nice and
    // I don't have time to duplicate all that right now.
    // this.attachShadow({ mode: "open" });
    // const target = this.shadowRoot!;

    const [target] = [this]; // brackets are to avoid linter

    target.appendChild(cssTemplate.content.cloneNode(true));

    // Need to put error messages in an inline element (<span>) instead of in the
    // reactRoot div, because we want the error messages to appear on the same line as
    // "Error:".
    this.errorRoot = document.createElement("span");
    target.appendChild(this.errorRoot);

    const myDiv = document.createElement("div");
    myDiv.classList.add("html-fill-container", "html-fill-item");
    target.appendChild(myDiv);

    this.reactRoot = createRoot(myDiv);

    // If there is a <script class="data"> element it contains static data.
    // Render it now.
    const dataEl = this.querySelector(
      "script.data"
    ) as HTMLScriptElement | null;
    if (dataEl) {
      const data = JSON.parse(dataEl.innerText);
      this.renderValue(data);
    }
  }

  renderValue(data: unknown) {
    this.clearError();

    if (!data) {
      this.reactRoot!.render(null);
      return;
    }

    this.reactRoot!.render(
      <StrictMode>
        <ShinyDataGrid
          id={this.id}
          data={data as PandasData<unknown>}
          bgcolor={getComputedBgColor(this)}
        ></ShinyDataGrid>
      </StrictMode>
    );
  }

  renderError(err: ErrorsMessageValue) {
    this.reactRoot!.render(null);
    this.errorRoot.innerText = err.message;
  }

  clearError() {
    this.reactRoot!.render(null);
    this.errorRoot.innerText = "";
  }
}

customElements.define("shiny-data-frame", ShinyDataFrameOutput);
