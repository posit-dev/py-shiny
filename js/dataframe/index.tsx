/* eslint-disable react-hooks/rules-of-hooks */
import { useState } from "react";
import { useImmer } from "use-immer";
import { ImmutableSet } from "./immutable-set";
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

import { ResponseValue, makeRequest } from "./request";
// setTimeout(() => {
//   console.log("Making request!");
//   makeRequest(
//     "dataframeUpdateCell",
//     [1, 2, 3],
//     (value: ResponseValue) => {
//       console.log("success!", value);
//     },
//     (err: string) => {
//       console.error("error!", err);
//     },
//     undefined
//   );
// }, 2000);

// TODO-barret;

// export interface PandasData<TIndex> {
//   columns: ReadonlyArray<string>;
//   // index: ReadonlyArray<TIndex>;
//   data: unknown[][];
//   type_hints?: ReadonlyArray<TypeHint>;
//   options: DataGridOptions;
// }

type UpdateCellData = {
  rowIndex: number;
  columnId: string;
  value: unknown;
  prev: unknown;
};
type UpdateCellDataRequest = {
  row_index: number;
  column_id: string;
  value: unknown;
  prev: unknown;
};

declare module "@tanstack/table-core" {
  interface ColumnMeta<TData extends RowData, TValue> {
    typeHint: TypeHint;
  }
  interface TableMeta<TData extends RowData> {
    updateCellsData: (cellInfos: UpdateCellData[]) => void;
  }
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

interface ShinyDataGridProps<TIndex> {
  id: string | null;
  data: PandasData<TIndex>;
  bgcolor?: string;
}

const ShinyDataGrid: FC<ShinyDataGridProps<unknown>> = (props) => {
  const { id, data, bgcolor } = props;
  const { columns, type_hints, data: rowData } = data;
  const { width, height, fill, filters: withFilters } = data.options;

  const containerRef = useRef<HTMLDivElement>(null);
  const theadRef = useRef<HTMLTableSectionElement>(null);
  const tbodyRef = useRef<HTMLTableSectionElement>(null);

  // const [target, setTarget] = useState(null);

  // const [editingInfo, setEdtingInfo] = useImmer({
  //   rowIndex: null,
  //   columnId: null,
  // });
  const [editRowIndex, setEditRowIndex] = useState<number>(null);
  const [editColumnId, setEditColumnId] = useState<string>(null);

  useEffect(() => {
    console.trace("editing info!", editRowIndex, editColumnId);
  }, [editColumnId, editRowIndex]);

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
          cell: ({
            getValue,
            row: { index: rowIndex },
            column: { id: columnId },
            table,
          }) => {
            // return <EditableCell {onclick}{}{}{}{}>  </EditableCell>

            const initialValue = getValue();
            // We need to keep and update the state of the cell normally
            const [value, setValue] = useImmer(initialValue);
            const inputRef = useRef(null);
            const editable =
              editRowIndex === rowIndex && editColumnId === columnId;

            const onEsc = (e: React.KeyboardEvent<HTMLInputElement>) => {
              if (e.key !== "Escape") return;
              // Prevent default behavior
              e.preventDefault();

              // inputRef.current.blur();
              setEditRowIndex(null);
              setEditColumnId(null);
              // TODO-barret-future; Set focus to table? (state: Editing was aborted)
            };
            const onTab = (e: React.KeyboardEvent<HTMLInputElement>) => {
              if (e.key !== "Tab") return;
              // Prevent default behavior
              e.preventDefault();

              const hasShift = e.shiftKey;

              const newColumnIndex =
                columns.indexOf(editColumnId) + (hasShift ? -1 : 1);
              if (newColumnIndex < 0 || newColumnIndex >= columns.length) {
                // If the new column index is out of bounds, quit
                return;
              }
              const newColumnId = columns[newColumnIndex];

              setEditColumnId(newColumnId);
            };
            const onEnter = (e: React.KeyboardEvent<HTMLInputElement>) => {
              if (e.key !== "Enter") return;
              // Prevent default behavior
              e.preventDefault();

              const hasShift = e.shiftKey;

              const newRowIndex = editRowIndex + (hasShift ? -1 : 1);
              if (
                newRowIndex < 0 ||
                newRowIndex >= table.getSortedRowModel().rows.length
              ) {
                // If the new row index is out of bounds, quit
                return;
              }

              setEditRowIndex(newRowIndex);
            };

            const onInputKeyDown = (
              e: React.KeyboardEvent<HTMLInputElement>
            ) => {
              [onEsc, onEnter, onTab].forEach((fn) => fn(e));
            };

            // When the input is blurred, we'll call our table meta's updateData function
            // console.log("rendering cell", rowIndex, id, initialValue, value);
            const onBlur = () => {
              // console.log("on blur!", initialValue, value);
              // Only update if the value has changed
              if (initialValue !== value) {
                table.options.meta?.updateCellsData([
                  {
                    rowIndex,
                    columnId,
                    value,
                    prev: initialValue,
                  },
                ]);
              }
            };

            // If the initialValue is changed external, sync it up with our state
            React.useEffect(() => {
              setValue(initialValue);
            }, [initialValue, setValue]);

            // Select the input when it becomes editable
            React.useEffect(() => {
              if (editable) {
                inputRef.current.focus();
                inputRef.current.select();
              }
            }, [editable]);

            // Reselect the input when it comes into view!
            // (It could be scrolled out of view and then back into view)
            function onFocus(e: React.FocusEvent<HTMLInputElement>) {
              if (editable) {
                e.target.select();
              }
            }

            function onChange(e: React.ChangeEvent<HTMLInputElement>) {
              console.log("on change!");
              setValue(e.target.value);
            }

            if (editable) {
              return (
                <input
                  value={value as string}
                  onChange={onChange}
                  onBlur={onBlur}
                  onFocus={onFocus}
                  onKeyDown={onInputKeyDown}
                  ref={inputRef}
                />
              );
            } else {
              const onReadyClick = (e: React.MouseEvent<HTMLInputElement>) => {
                console.trace("on ready click!", e.target);
                setEditRowIndex(rowIndex);
                setEditColumnId(columnId);
              };
              return <div onClick={onReadyClick}>{value as string}</div>;
            }
          },
        };
      }),
    [columns, editColumnId, editRowIndex, type_hints]
  );

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

  const filterOpts = useFilter<unknown[]>(withFilters);

  const options: TableOptions<unknown[]> = {
    data: dataState,
    columns: coldefs,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    ...filterOpts,
    debugAll: true,
    // Provide our updateCellsData function to our table meta
    // autoResetPageIndex,
    meta: {
      updateCellsData: (cellInfos: UpdateCellData[]) => {
        // // Skip page index reset until after next rerender
        // skipAutoResetPageIndex();

        const updateInfos: UpdateCellDataRequest[] = cellInfos.map(
          (cellInfo) => {
            return {
              row_index: cellInfo.rowIndex,
              column_id: cellInfo.columnId,
              value: cellInfo.value,
              prev: cellInfo.prev,
            };
          }
        );

        console.log("Set data here! (Send info back to shiny)", cellInfos);
        makeRequest(
          "outputRPC",
          [
            // id: string
            id,
            // handler: string
            "cells_update",
            // list[OnCellUpdateParams]
            updateInfos,
          ],
          (values: ResponseValue[]) => {
            console.log("cellsUpdate - success!", values);
            setData((draft) => {
              values.forEach((value: string, i: number) => {
                const { rowIndex, columnId } = cellInfos[i];
                const colIndex = columns.indexOf(columnId);
                const row = draft[rowIndex];
                console.log(
                  "Setting new value!",
                  value,
                  columnId,
                  draft[rowIndex]
                );

                draft[rowIndex][colIndex] = value;
              });
            });
          },
          (err: string) => {
            console.error("error!", err);
          },
          undefined
        );
      },
    },
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

  // ### Row selection ###############################################################
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
    const handleMessage = (event: CustomEvent<{ keys: number[] }>) => {
      // We convert "None" to an empty tuple on the python side
      // so an empty array indicates that selection should be cleared.
      if (!event.detail.keys.length) {
        rowSelection.clear();
      } else {
        rowSelection.setMultiple(event.detail.keys.map(String));
      }
    };

    const element = document.getElementById(id);
    element.addEventListener(
      "updateRowSelection",
      handleMessage as EventListener
    );

    return () => {
      element.removeEventListener(
        "updateRowSelection",
        handleMessage as EventListener
      );
    };
  }, [rowSelection]);

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
            .map((key) => parseInt(key))
            .sort()
        );
      }
    }
  }, [[...rowSelection.keys()]]);

  // ### End row selection ############################################################

  // ### Editable cells ###############################################################
  // type TKey = DOMStringMap[string]: string
  type TKey = typeof HTMLTableRowElement.prototype.dataset.key;
  type TElement = HTMLTableRowElement;

  const editable = data.options["editable"] ?? false;
  if (editable && canSelect) {
    // TODO-barret; maybe listen for a double click?
    // Is is possible to rerender on double click independent of the row selection?
    console.error(
      "Should not have editable and row selection at the same time"
    );
  }

  // const [selectedKeys, setSelectedKeys] = useImmer<ImmutableSet<TKey>>(
  //   ImmutableSet.empty()
  // );

  // // The anchor is the item that was most recently selected with a click or ctrl-click,
  // // and is used to determine the "other end" of a shift-click selection operation.
  // const [anchor, setAnchor] = useImmer<TKey | null>(null);

  // const onMouseDown = (event: React.MouseEvent<TElement, MouseEvent>): void => {
  //   if (mode === SelectionMode.None) {
  //     return;
  //   }

  //   const el = event.currentTarget as TElement;
  //   const key = keyAccessor(el);

  //   const result = performMouseDownAction<TKey, TElement>(
  //     mode,
  //     between,
  //     selectedKeys,
  //     event,
  //     key,
  //     anchor
  //   );
  //   if (result) {
  //     setSelectedKeys(result.selection);
  //     if (result.anchor) {
  //       setAnchor(key);
  //       el.focus();
  //     }
  //     event.preventDefault();
  //   }
  // };

  // const onKeyDown = (event: React.KeyboardEvent<TElement>): void => {
  //   if (mode === SelectionMode.None) {
  //     return;
  //   }

  //   const el = event.currentTarget as TElement;
  //   const key = keyAccessor(el);
  //   const selected = selectedKeys.has(key);

  //   if (mode === SelectionMode.Single) {
  //     if (event.key === " " || event.key === "Enter") {
  //       if (selectedKeys.has(key)) {
  //         setSelectedKeys(ImmutableSet.empty());
  //       } else {
  //         setSelectedKeys(ImmutableSet.just(key));
  //       }
  //       event.preventDefault();
  //     } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
  //       const targetKey = focusOffset(key, event.key === "ArrowUp" ? -1 : 1);
  //       if (targetKey) {
  //         event.preventDefault();
  //         if (selected) {
  //           setSelectedKeys(ImmutableSet.just(targetKey));
  //         }
  //       }
  //     }
  //   } else if (mode === SelectionMode.Multiple) {
  //     if (event.key === " " || event.key === "Enter") {
  //       setSelectedKeys(selectedKeys.toggle(key));
  //       event.preventDefault();
  //     } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
  //       if (focusOffset(key, event.key === "ArrowUp" ? -1 : 1)) {
  //         event.preventDefault();
  //       }
  //     }
  //   }
  // };

  // const barret2 = () => {
  //   return {
  //     has(key: TKey): boolean {
  //       return selectedKeys.has(key);
  //     },

  //     set(key: TKey, selected: boolean) {
  //       if (selected) {
  //         setSelectedKeys(selectedKeys.add(key));
  //       } else {
  //         setSelectedKeys(selectedKeys.delete(key));
  //       }
  //     },

  //     setMultiple(key_arr: TKey[]) {
  //       setSelectedKeys(ImmutableSet.just(...key_arr));
  //     },

  //     clear() {
  //       setSelectedKeys(selectedKeys.clear());
  //     },

  //     keys() {
  //       return selectedKeys;
  //     },

  //     itemHandlers() {
  //       return { onMouseDown, onKeyDown };
  //     },
  //   };
  // };

  const EditableCell = function () {
    // States
    // # Ready
    // # Editing
    // # Saving / Disabled
    // # Error
    // # Saved
    // # Cancelled
    // # New
    // # Added
    // # Removed

    return <input />;
  };

  // ### End editable cells ###########################################################

  //

  //

  //
  const tbodyTabItems = React.useCallback(
    () => tbodyRef.current.querySelectorAll("[tabindex='-1']"),
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
  }, [data]);

  const headerRowCount = table.getHeaderGroups().length;

  // Assume we're scrolling until proven otherwise
  let scrollingClass = "scrolling";
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

// This is the shim between Shiny's messaging passing behaviour and React.
// The python code sends a custom message which includes an id, handler
// and obbject and we use that information to dispatch it to the
// react listener.
// It would be better to have something similar to session.send_input_message
// for updating outputs, but that requires changes to ShinyJS.
$(function () {
  Shiny.addCustomMessageHandler("receiveMessage", function (message) {
    const evt = new CustomEvent(message.handler, {
      detail: message.obj,
    });
    const el = document.getElementById(message.id);
    el.dispatchEvent(evt);
  });
});
