/* eslint-disable react-hooks/rules-of-hooks */
import {
  Column,
  ColumnDef,
  RowData,
  RowModel,
  SortingState,
  TableOptions,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { Virtualizer, useVirtualizer } from "@tanstack/react-virtual";
import React, {
  FC,
  ReactElement,
  StrictMode,
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Root, createRoot } from "react-dom/client";
import { ErrorsMessageValue } from "rstudio-shiny/srcts/types/src/shiny/shinyapp";
import { useImmer } from "use-immer";
import { TableBodyCell } from "./cell";
import { getCellEditMapObj, useCellEditMap } from "./cell-edit-map";
import { findFirstItemInView, getStyle } from "./dom-utils";
import { Filter, useFilters } from "./filter";
import type { BrowserCellSelection, SelectionModesProp } from "./selection";
import {
  SelectionModes,
  initRowSelectionModes,
  useSelection,
} from "./selection";
import { useSort } from "./sort";
import { SortArrow } from "./sort-arrows";
import css from "./styles.scss";
import { useTabindexGroup } from "./tabindex-group";
import { useSummary } from "./table-summary";
import { EditModeEnum, PandasData, PatchInfo, TypeHint } from "./types";

// TODO-barret set selected cell as input! (Might be a followup?)

// TODO-barret; Type support
// export interface PandasData<TIndex> {
//   columns: ReadonlyArray<string>;
//   // index: ReadonlyArray<TIndex>;
//   data: unknown[][];
//   typeHints?: ReadonlyArray<TypeHint>;
//   options: DataGridOptions;
// }

declare module "@tanstack/table-core" {
  interface ColumnMeta<TData extends RowData, TValue> {
    colIndex: number;
    typeHint: TypeHint | undefined;
    isHtmlColumn: boolean;
  }
  // interface TableMeta<TData extends RowData> {
  //   updateCellsData: (cellInfos: UpdateCellData[]) => void;
  // }
}

// // TODO-barret-future; Use window.setSelectionRange() and this method to reselect text when scrolling out of view
// const useSelectedText = () => {
//   const [text, setText] = useState("");
//   const select = () => {
//     const selected = window.getSelection() as Selection;
//     setText(selected.toString());
//   };
//   return [select, text] as const;
// };

//

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

type ShinyDataGridServerInfo<TIndex> = {
  payload: PandasData<TIndex>;
  patchInfo: PatchInfo;
  selectionModes: SelectionModesProp;
};

interface ShinyDataGridProps<TIndex> {
  id: string | null;
  gridInfo: ShinyDataGridServerInfo<TIndex>;
  bgcolor?: string;
}

const ShinyDataGrid: FC<ShinyDataGridProps<unknown>> = ({
  id,
  gridInfo: { payload, patchInfo, selectionModes: selectionModesProp },
  bgcolor,
}) => {
  const {
    columns,
    typeHints,
    data: rowData,
    options: payloadOptions,
  } = payload;
  const { width, height, fill, filters: withFilters } = payloadOptions;

  const containerRef = useRef<HTMLDivElement>(null);
  const theadRef = useRef<HTMLTableSectionElement>(null);
  const tbodyRef = useRef<HTMLTableSectionElement>(null);

  const { cellEditMap, setCellEditMapAtLoc } = useCellEditMap();

  const editCellsIsAllowed = payloadOptions["editable"] === true;

  const coldefs = useMemo<ColumnDef<unknown[], unknown>[]>(
    () =>
      columns.map((colname, colIndex) => {
        const typeHint = typeHints?.[colIndex];

        const isHtmlColumn = typeHint?.type === "html";
        const enableSorting = isHtmlColumn ? false : undefined;

        return {
          accessorFn: (row, index) => {
            return row[colIndex];
          },
          // TODO: delegate this decision to something in filter.tsx
          filterFn:
            typeHint?.type === "numeric" ? "inNumberRange" : "includesString",
          header: colname,
          meta: {
            colIndex,
            isHtmlColumn,
            typeHint,
          },
          cell: ({ getValue }) => {
            return getValue() as string;
          },
          enableSorting,
        };
      }),
    [columns, typeHints]
  );

  // TODO-barret-future; Possible pagination helper
  // function useSkipper() {
  //   const shouldSkipRef = React.useRef(true);
  //   const shouldSkip = shouldSkipRef.current;

  //   // Wrap a function with this to skip a pagination reset temporarily
  //   const skip = React.useCallback(() => {
  //     shouldSkipRef.current = false;
  //   }, []);

  //   React.useEffect(() => {
  //     shouldSkipRef.current = true;
  //   });

  //   return [shouldSkip, skip] as const;
  // }
  // const [autoResetPageIndex, skipAutoResetPageIndex] = useSkipper();

  const dataOriginal = useMemo(() => rowData, [rowData]);
  const [dataState, setData] = useImmer(rowData);

  const { sorting, sortState, sortingTableOptions } = useSort();

  const { columnFilters, columnFiltersState, filtersTableOptions } =
    useFilters<unknown[]>(withFilters);

  const options: TableOptions<unknown[]> = {
    data: dataState,
    columns: coldefs,
    state: {
      ...sortState,
      ...columnFiltersState,
    },
    getCoreRowModel: getCoreRowModel(),
    ...sortingTableOptions,
    ...filtersTableOptions,
    // debugAll: true,
    // Provide our updateCellsData function to our table meta
    // autoResetPageIndex,
    // meta: {
    //   updateCellsData: (cellInfos: UpdateCellData[]) => {},
    // },
  };
  const table = useReactTable(options);

  const rowVirtualizer = useVirtualizer({
    count: table.getFilteredRowModel().rows.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 31,
    paddingStart: theadRef.current?.clientHeight ?? 0,
    // In response to https://github.com/posit-dev/py-shiny/pull/538/files#r1228352446
    // (the default scrollingDelay is 150)
    scrollingDelay: 10,
  });

  // Reset scroll when dataset changes
  useLayoutEffect(() => {
    rowVirtualizer.scrollToOffset(0);
  }, [payload, rowVirtualizer]);

  const totalSize = rowVirtualizer.getTotalSize();
  const virtualRows = rowVirtualizer.getVirtualItems();

  // paddingTop and paddingBottom are to force the <tbody> to add up to the correct
  // virtual height.
  // paddingTop must subtract out the thead height, since thead is inside the scroll
  // container but not virtualized.
  const paddingTop =
    (virtualRows.length > 0 ? virtualRows?.[0]?.start || 0 : 0) -
      (theadRef.current?.clientHeight ?? 0) ?? 0;
  const paddingBottom =
    virtualRows.length > 0
      ? totalSize - (virtualRows?.[virtualRows.length - 1]?.end || 0)
      : 0;

  const summary = useSummary(
    payloadOptions["summary"],
    containerRef?.current,
    virtualRows,
    theadRef.current,
    rowVirtualizer.options.count
  );

  const tableStyle = payloadOptions["style"] ?? "grid";
  const containerClass =
    tableStyle === "grid" ? "shiny-data-grid-grid" : "shiny-data-grid-table";
  const tableClass = tableStyle === "table" ? "table table-sm" : null;

  // ### Row selection ###############################################################

  const rowSelectionModes = initRowSelectionModes(selectionModesProp);

  const canSelect = !rowSelectionModes.is_none();
  const canMultiRowSelect =
    rowSelectionModes.row !== SelectionModes._rowEnum.NONE;

  const rowSelection = useSelection<string, HTMLTableRowElement>(
    rowSelectionModes,
    (el) => el.dataset.key!,
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
    const handleMessage = (
      event: CustomEvent<{ cellSelection: BrowserCellSelection }>
    ) => {
      // We convert "None" to an empty tuple on the python side
      // so an empty array indicates that selection should be cleared.

      const cellSelection = event.detail.cellSelection;

      if (cellSelection.type === "none") {
        rowSelection.clear();
        return;
        // } else if (cellSelection.type === "all") {
        //   rowSelection.setMultiple(rowData.map((_, i) => String(i)));
        //   return;
      } else if (cellSelection.type === "row") {
        rowSelection.setMultiple(cellSelection.rows.map(String));
        return;
      } else {
        console.error("Unhandled cell selection update:", cellSelection);
      }
    };

    if (!id) return;

    const element = document.getElementById(id);
    if (!element) return;

    element.addEventListener(
      "updateCellSelection",
      handleMessage as EventListener
    );

    return () => {
      element.removeEventListener(
        "updateCellSelection",
        handleMessage as EventListener
      );
    };
  }, [id, rowSelection, rowData]);

  useEffect(() => {
    if (!id) return;
    const shinyId = `${id}_cell_selection`;
    let shinyValue: BrowserCellSelection | null = null;
    if (rowSelectionModes.is_none()) {
      shinyValue = null;
    } else if (rowSelectionModes.row !== SelectionModes._rowEnum.NONE) {
      const rowSelectionKeys = rowSelection.keys().toList();
      const rowsById = table.getSortedRowModel().rowsById;
      shinyValue = {
        type: "row",
        rows: rowSelectionKeys.map((key) => rowsById[key].index).sort(),
      };
    } else {
      console.error("Unhandled row selection mode:", rowSelectionModes);
    }
    Shiny.setInputValue!(shinyId, shinyValue);
  }, [id, rowSelection, rowSelectionModes, table, table.getSortedRowModel]);

  useEffect(() => {
    if (!id) return;
    const shinyId = `${id}_column_sort`;
    Shiny.setInputValue!(shinyId, sorting);
  }, [id, sorting]);
  useEffect(() => {
    if (!id) return;
    const shinyId = `${id}_column_filter`;
    Shiny.setInputValue!(shinyId, columnFilters);
  }, [id, columnFilters]);
  useEffect(() => {
    if (!id) return;
    const shinyId = `${id}_data_view_indicies`;

    // Already prefiltered rows!
    const shinyValue: RowModel<unknown[]> = table.getSortedRowModel();
    console.log("sortedRowModel", shinyValue);

    const rowIndices = table.getSortedRowModel().rows.map((row) => row.index);
    Shiny.setInputValue!(shinyId, rowIndices);
  }, [
    id,
    table,
    // Update with either sorting or columnFilters update!
    sorting,
    columnFilters,
  ]);

  // ### End row selection ############################################################

  // ### Editable cells ###############################################################
  // type TKey = DOMStringMap[string]: string
  type TKey = typeof HTMLTableRowElement.prototype.dataset.key;
  type TElement = HTMLTableRowElement;

  if (editCellsIsAllowed && canSelect) {
    // TODO-barret; maybe listen for a double click?
    // Is is possible to rerender on double click independent of the row selection?
    console.error(
      "Should not have editable and row selection at the same time"
    );
  }

  // ### End editable cells ###########################################################

  //

  //

  //
  const tbodyTabItems = React.useCallback(
    () => tbodyRef.current!.querySelectorAll("[tabindex='-1']"),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [tbodyRef.current]
  );
  const tbodyTabGroup = useTabindexGroup(containerRef.current, tbodyTabItems, {
    top: theadRef.current?.clientHeight ?? 0,
  });

  // Reset sorting and selection whenever dataset changes. (Should we do this?)
  // NOTE-2024-02-21-barret; Maybe only reset sorting if the column information changes?
  useEffect(() => {
    return () => {
      table.resetSorting();
      rowSelection.clear();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [payload]);

  const headerRowCount = table.getHeaderGroups().length;

  // Assume we're scrolling until proven otherwise
  let scrollingClass = rowData.length > 0 ? "scrolling" : "";
  const scrollHeight = containerRef.current?.scrollHeight;
  const clientHeight = containerRef.current?.clientHeight;
  if (scrollHeight && clientHeight && scrollHeight <= clientHeight) {
    scrollingClass = "";
  }

  const makeHeaderKeyDown =
    (column: Column<unknown[], unknown>) => (event: React.KeyboardEvent) => {
      if (event.key === " " || event.key === "Enter") {
        column.toggleSorting(undefined, event.shiftKey);
      }
    };

  const measureEl = useVirtualizerMeasureWorkaround(rowVirtualizer);

  let className = `shiny-data-grid ${containerClass} ${scrollingClass}`;
  if (fill) {
    className += " html-fill-item";
  }

  return (
    <>
      <div
        className={className}
        ref={containerRef}
        style={{ width, height, overflow: "auto" }}
      >
        <table
          className={tableClass + (withFilters ? " filtering" : "")}
          aria-rowcount={dataState.length}
          aria-multiselectable={canMultiRowSelect}
          style={{
            width: width === null || width === "auto" ? undefined : "100%",
          }}
        >
          <thead ref={theadRef} style={{ backgroundColor: bgcolor }}>
            {table.getHeaderGroups().map((headerGroup, i) => (
              <tr key={headerGroup.id} aria-rowindex={i + 1}>
                {headerGroup.headers.map((header) => {
                  const headerContent = header.isPlaceholder ? undefined : (
                    <div
                      style={{
                        cursor: header.column.getCanSort()
                          ? "pointer"
                          : undefined,
                        userSelect: header.column.getCanSort()
                          ? "none"
                          : undefined,
                      }}
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                      <SortArrow direction={header.column.getIsSorted()} />
                    </div>
                  );

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
                      {headerContent}
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
                      // TODO-barret; Only send in the cell data that is needed;
                      const rowIndex = cell.row.index;
                      const columnIndex = cell.column.columnDef.meta!.colIndex;
                      const [cellEditInfo, _key] = getCellEditMapObj(
                        cellEditMap,
                        rowIndex,
                        columnIndex
                      );

                      return (
                        <TableBodyCell
                          key={cell.id}
                          rowId={cell.row.id}
                          containerRef={containerRef}
                          cell={cell}
                          patchInfo={patchInfo}
                          editCellsIsAllowed={editCellsIsAllowed}
                          columns={columns}
                          coldefs={coldefs}
                          rowIndex={rowIndex}
                          columnIndex={columnIndex}
                          getSortedRowModel={table.getSortedRowModel}
                          cellEditInfo={cellEditInfo}
                          setData={setData}
                          setCellEditMapAtLoc={setCellEditMapAtLoc}
                        ></TableBodyCell>
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
    (el: Element | null) => {
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

function getComputedBgColor(el: HTMLElement | null): string | undefined {
  if (!el) {
    // Top of document, can't recurse further
    return undefined;
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
      return undefined;
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

  renderValue(value: ShinyDataGridServerInfo<unknown> | null) {
    this.clearError();

    if (!value) {
      this.reactRoot!.render(null);
      return;
    }

    this.reactRoot!.render(
      <StrictMode>
        <ShinyDataGrid
          id={this.id}
          gridInfo={value}
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

// This is the shim between Shiny's messaging passing behaviour and React.
// The python code sends a custom message which includes an id, handler
// and obbject and we use that information to dispatch it to the
// react listener.
// It would be better to have something similar to session.send_input_message
// for updating outputs, but that requires changes to ShinyJS.
$(function () {
  Shiny.addCustomMessageHandler("shinyDataFrameMessage", function (message) {
    const evt = new CustomEvent(message.handler, {
      detail: message.obj,
    });
    const el = document.getElementById(message.id);
    el?.dispatchEvent(evt);
  });
});
