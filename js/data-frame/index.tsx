/* eslint-disable react-hooks/rules-of-hooks */

// TODO-barret-future; Try to group all related code into a file and make index.tsx as small as possible. Try to move all logic into files and keep the main full of `useFOO` functions.

// TODO-barret-future; Instead of deconstructinng all of the use state objects, keep it as a dictionary and shorten the method names. The docs can live on the _useFoo` function return type. Ex: CellEditMapReturnObject 's setCellEditMapAtLoc should contain JSDoc on it's objects. Then we'd have a `cellEditMap.setAtLoc` method.

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
import { useImmer } from "use-immer";
import { TableBodyCell } from "./cell";
import { getCellEditMapObj, useCellEditMap } from "./cell-edit-map";
import {
  addPatchToData,
  cellPatchPyArrToCellPatchArr,
  type CellPatchPy,
} from "./data-update";
import { findFirstItemInView, getStyle } from "./dom-utils";
import { ColumnFiltersState, Filter, FilterValue, useFilters } from "./filter";
import type { CellSelection, SelectionModesProp } from "./selection";
import { SelectionModes, initSelectionModes, useSelection } from "./selection";
import { SortingState, useSort } from "./sort";
import { SortArrow } from "./sort-arrows";
import { StyleInfo, getCellStyle, useStyleInfoMap } from "./style-info";
import css from "./styles.scss";
import { useTabindexGroup } from "./tabindex-group";
import { useSummary } from "./table-summary";
import { PandasData, PatchInfo, TypeHint } from "./types";

// TODO-barret-future set selected cell as input! (Might be a followup?)

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
    columns: columnsProp,
    typeHints: typeHintsProp,
    data: tableDataProp,
    options: payloadOptions = {
      width: undefined,
      height: undefined,
      fill: false,
      styles: [],
    },
    htmlDeps,
  } = payload;
  const {
    width,
    height,
    fill,
    filters: withFilters,
    styles: initStyleInfos,
  } = payloadOptions;

  const containerRef = useRef<HTMLDivElement>(null);
  const theadRef = useRef<HTMLTableSectionElement>(null);
  const tbodyRef = useRef<HTMLTableSectionElement>(null);

  const [columns, setColumns] = useImmer(columnsProp);
  const [typeHints, setTypeHints] = useImmer(typeHintsProp);

  const _useStyleInfo = useStyleInfoMap({
    initStyleInfos: initStyleInfos ?? [],
    nrow: tableDataProp.length,
    ncol: columns.length,
  });
  /**
   * Contains all style information for the full table.
   *
   * Currently only the "data" location is supported.
   */
  const styleInfoMap = _useStyleInfo.styleInfoMap;
  const { setStyleInfos } = _useStyleInfo;

  const _cellEditMap = useCellEditMap();
  /**
   * Contains all cell state and edit information
   *
   * If a cell's state is not in this map, it is assumed to be in the default display state.
   */
  const cellEditMap = _cellEditMap.cellEditMap;
  /**
   * Set a cell's state or edit value in the `cellEditMap`
   */
  const setCellEditMapAtLoc = _cellEditMap.setCellEditMapAtLoc;
  /**
   * Reset the `cellEditMap` to an empty state
   */
  const resetCellEditMap = _cellEditMap.resetCellEditMap;

  /**
   * Determines if the user is allowed to edit cells in the table.
   */
  const editCellsIsAllowed = payloadOptions["editable"] === true;

  /**
   * Determines if any cell is currently being edited
   *
   * This is currently being used to prevent row selection when a cell is being edited.
   */
  const isEditingCell = useMemo<boolean>(() => {
    for (const cellEdit of cellEditMap.values()) {
      if (cellEdit.isEditing) {
        return true;
      }
    }
    return false;
  }, [cellEditMap]);

  /**
   * Column definitions for the table
   */
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
            const ret = getValue();

            // Regardless of type, if the value is null or undefined,
            // return an empty string
            if (ret === null || ret === undefined) {
              return "";
            }
            switch (typeHint?.type) {
              // Return the value as is
              case "numeric":
              case "date":
              case "datetime":
              case "duration":
              case "categorical":
              case "html":
                return ret;
              // Convert the value to a string
              case "string":
              case "boolean":
                return String(ret);
              // Convert the value to a JSON string if it isn't a string already
              case "unknown":
              case "object":
                if (typeof ret === "string") {
                  return ret;
                }
                return JSON.stringify(ret);
              default:
                return ret;
            }
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

  /**
   * Copy of the original data
   */
  const dataOriginal = useMemo(() => tableDataProp, [tableDataProp]);

  const _tableData = useImmer(tableDataProp);
  /** Up-to-date data for the table */
  const tableData = _tableData[0];
  /** Function to update the data in the table */
  const setTableData = _tableData[1];

  const getColDefs = (): ColumnDef<unknown[], unknown>[] => {
    return coldefs;
  };

  const _sort = useSort({ getColDefs });
  /** Sorting state of the table */
  const sorting = _sort.sorting;
  /** Table options specific for sorting */
  const sortTableStateOptions = _sort.sortTableStateOptions;
  /** Sorting state of the table */
  const sortTableOptions = _sort.sortTableOptions;
  /** Set the sorting state of the table */
  const setSorting = _sort.setSorting;

  const {
    columnFilters,
    columnFiltersState,
    filtersTableOptions,
    setColumnFilters,
  } = useFilters<unknown[]>(withFilters);

  const updateData = useCallback(
    ({
      data,
      columns,
      typeHints,
    }: {
      data: PandasData<unknown>["data"];
      columns: readonly string[];
      typeHints: readonly TypeHint[] | undefined;
    }) => {
      setColumns(columns);
      setTableData(data);
      setTypeHints(typeHints);
      resetCellEditMap();

      // Make map for quick lookup of type hints
      const newTypeHintMap = new Map<string, TypeHint>();
      typeHints?.forEach((hint, i) => {
        newTypeHintMap.set(columns[i]!, hint);
      });
      // Filter out sorting and column filters that are no longer valid
      const newSort = sorting.filter((sort) => newTypeHintMap.has(sort.id));
      const newColumnFilter = columnFilters.filter((filter) => {
        const typeHint = newTypeHintMap.get(filter.id);
        if (!typeHint) return false;
        // Maintain the filter if it's a numeric filter
        // Drop if it's a string filter
        if (typeHint.type === "numeric") {
          return (
            filter.value === null ||
            (Array.isArray(filter.value) &&
              filter.value.every((v) => v !== null))
          );
        }
        // Maintain string filters
        return typeof filter.value === "string";
      });

      setColumnFilters(newColumnFilter);
      setSorting(newSort);
    },
    [
      columnFilters,
      resetCellEditMap,
      setColumnFilters,
      setColumns,
      setSorting,
      setTableData,
      setTypeHints,
      sorting,
    ]
  );

  const options: TableOptions<unknown[]> = {
    data: tableData,
    columns: coldefs,
    state: {
      ...sortTableStateOptions,
      ...columnFiltersState,
    },
    getCoreRowModel: getCoreRowModel(),
    ...sortTableOptions,
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
    overscan: 15,
    paddingStart: theadRef.current?.clientHeight ?? 0,
    // In response to https://github.com/posit-dev/py-shiny/pull/538/files#r1228352446
    // (the default scrollingDelay is 150)
    isScrollingResetDelay: 10,
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

  const selectionModes = initSelectionModes(selectionModesProp);

  const canSelect = !selectionModes.isNone();
  const canMultiRowSelect = selectionModes.row !== SelectionModes._rowEnum.NONE;

  const selection = useSelection<string, HTMLTableRowElement>({
    isEditingCell,
    editCellsIsAllowed,
    selectionModes,
    keyAccessor: (el) => {
      return el.dataset.key!;
    },
    focusEscape: (el) => {
      setTimeout(() => {
        el?.blur();
        containerRef.current?.focus();
      }, 0);
    },
    focusOffset: (key, offset = 0) => {
      const rowModel = table.getSortedRowModel();
      let index = rowModel.rows.findIndex((row) => row.id === key);
      if (index < 0) {
        return null;
      }
      index += offset;
      if (index < 0 || index >= rowModel.rows.length) {
        return null;
      }
      const targetKey = rowModel.rows[index]!.id;
      rowVirtualizer.scrollToIndex(index);
      setTimeout(() => {
        const targetEl = containerRef.current?.querySelector(
          `[data-key='${targetKey}']`
        ) as HTMLElement | null;
        targetEl?.focus();
      }, 0);
      return targetKey;
    },
    between: (fromKey, toKey) =>
      findKeysBetween(table.getSortedRowModel(), fromKey, toKey),
    onKeyDownEnter: (el) => {
      // Retrieve all editable cells in the row
      const childrenNodes = Array(...el.childNodes.values()).filter((node) => {
        return (
          node instanceof HTMLElement &&
          node.classList.contains("cell-editable")
        );
      });
      if (childrenNodes.length === 0) return; // Quit early

      // Find the first editable cell in the row
      const firstItem = findFirstItemInView(
        containerRef.current!,
        childrenNodes
      );
      if (!firstItem) return; // Quit early

      // Submit the double click event to the cell to trigger edit mode for the cell
      const doubleClickEvent = new MouseEvent("dblclick", {
        bubbles: true,
        cancelable: true,
      });
      firstItem.dispatchEvent(doubleClickEvent);
    },
  });

  useEffect(() => {
    const handleCellSelection = (
      event: CustomEvent<{ cellSelection: CellSelection }>
    ) => {
      // We convert "None" to an empty tuple on the python side
      // so an empty array indicates that selection should be cleared.

      const cellSelection = event.detail.cellSelection;

      if (cellSelection.type === "none") {
        selection.clear();
        return;
        // } else if (cellSelection.type === "all") {
        //   rowSelection.setMultiple(rowData.map((_, i) => String(i)));
        //   return;
      } else if (cellSelection.type === "row") {
        selection.setMultiple(cellSelection.rows.map(String));
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
      handleCellSelection as EventListener
    );

    return () => {
      element.removeEventListener(
        "updateCellSelection",
        handleCellSelection as EventListener
      );
    };
  }, [id, selection, tableData]);

  useEffect(() => {
    if (!htmlDeps) return;
    // Register the Shiny HtmlDependencies
    Shiny.renderDependenciesAsync([...htmlDeps]);
  }, [htmlDeps]);

  useEffect(() => {
    const handleAddPatches = (
      event: CustomEvent<{
        patches: CellPatchPy[];
      }>
    ) => {
      const evtPatches = event.detail.patches;
      const newPatches = cellPatchPyArrToCellPatchArr(evtPatches);

      // Update data with extra patches
      addPatchToData({
        setData: setTableData,
        newPatches,
        setCellEditMapAtLoc,
      });
    };

    if (!id) return;

    const element = document.getElementById(id);
    if (!element) return;

    element.addEventListener("addPatches", handleAddPatches as EventListener);

    return () => {
      element.removeEventListener(
        "addPatches",
        handleAddPatches as EventListener
      );
    };
  }, [columns, id, setCellEditMapAtLoc, setSorting, setTableData]);

  useEffect(() => {
    const handleUpdateData = (
      event: CustomEvent<{
        data: PandasData<unknown>["data"];
        columns: PandasData<unknown>["columns"];
        typeHints: PandasData<unknown>["typeHints"];
      }>
    ) => {
      const evtData = event.detail;

      updateData(evtData);
    };

    if (!id) return;

    const element = document.getElementById(id);
    if (!element) return;

    element.addEventListener("updateData", handleUpdateData as EventListener);

    return () => {
      element.removeEventListener(
        "updateData",
        handleUpdateData as EventListener
      );
    };
  }, [columns, id, resetCellEditMap, setTableData, updateData]);

  useEffect(() => {
    const handleColumnSort = (
      event: CustomEvent<{ sort: { col: number; desc: boolean }[] }>
    ) => {
      const shinySorting = event.detail.sort;
      const columnSorting: SortingState = [];

      shinySorting.map((sort) => {
        columnSorting.push({
          id: columns[sort.col]!,
          desc: sort.desc,
        });
      });
      setSorting(columnSorting);
    };

    if (!id) return;

    const element = document.getElementById(id);
    if (!element) return;

    element.addEventListener(
      "updateColumnSort",
      handleColumnSort as EventListener
    );

    return () => {
      element.removeEventListener(
        "updateColumnSort",
        handleColumnSort as EventListener
      );
    };
  }, [columns, id, setSorting]);

  useEffect(() => {
    const handleColumnFilter = (
      event: CustomEvent<{ filter: { col: number; value: FilterValue }[] }>
    ) => {
      const shinyFilters = event.detail.filter;

      const columnFilters: ColumnFiltersState = [];
      shinyFilters.map((filter) => {
        columnFilters.push({
          id: columns[filter.col]!,
          value: filter.value,
        });
      });
      setColumnFilters(columnFilters);
    };

    if (!id) return;

    const element = document.getElementById(id);
    if (!element) return;

    element.addEventListener(
      "updateColumnFilter",
      handleColumnFilter as EventListener
    );

    return () => {
      element.removeEventListener(
        "updateColumnFilter",
        handleColumnFilter as EventListener
      );
    };
  }, [columns, id, setColumnFilters]);

  useEffect(() => {
    const handleStyles = (event: CustomEvent<{ styles: StyleInfo[] }>) => {
      const styles = event.detail.styles;
      setStyleInfos(styles);
    };

    if (!id) return;

    const element = document.getElementById(id);
    if (!element) return;

    element.addEventListener("updateStyles", handleStyles as EventListener);

    return () => {
      element.removeEventListener(
        "updateStyles",
        handleStyles as EventListener
      );
    };
  }, [id, setStyleInfos]);

  useEffect(() => {
    if (!id) return;
    let shinyValue: CellSelection | null = null;
    if (selectionModes.isNone()) {
      shinyValue = null;
    } else if (selectionModes.row !== SelectionModes._rowEnum.NONE) {
      const rowSelectionKeys = selection.keys().toList();
      const rowsById = table.getSortedRowModel().rowsById;
      shinyValue = {
        type: "row",
        rows: rowSelectionKeys
          .map((key) => {
            if (!(key in rowsById)) {
              return null;
            }
            return rowsById[key]!.index;
          })
          .filter((x): x is number => x !== null),
      };
    } else {
      console.error("Unhandled row selection mode:", selectionModes);
    }
    Shiny.setInputValue!(`${id}_cell_selection`, shinyValue);
  }, [id, selection, selectionModes, table, table.getSortedRowModel]);

  useEffect(() => {
    if (!id) return;
    const shinySort: { col: number; desc: boolean }[] = [];
    sorting.map((sortObj) => {
      const columnNum = columns.indexOf(sortObj.id);
      shinySort.push({
        col: columnNum,
        desc: sortObj.desc,
      });
    });
    Shiny.setInputValue!(`${id}_sort`, shinySort);

    // Deprecated as of 2024-05-21
    Shiny.setInputValue!(`${id}_column_sort`, shinySort);
  }, [columns, id, sorting]);
  useEffect(() => {
    if (!id) return;
    const shinyFilter: {
      col: number;
      value: FilterValue;
    }[] = [];
    columnFilters.map((filterObj) => {
      const columnNum = columns.indexOf(filterObj.id);
      shinyFilter.push({
        col: columnNum,
        value: filterObj.value as FilterValue,
      });
    });
    Shiny.setInputValue!(`${id}_filter`, shinyFilter);

    // Deprecated as of 2024-05-21
    Shiny.setInputValue!(`${id}_column_filter`, shinyFilter);
  }, [id, columnFilters, columns]);
  useEffect(() => {
    if (!id) return;

    const shinyRows: number[] = table
      // Already prefiltered rows!
      .getSortedRowModel()
      .rows.map((row) => row.index);
    Shiny.setInputValue!(`${id}_data_view_rows`, shinyRows);

    // Legacy value as of 2024-05-13
    Shiny.setInputValue!(`${id}_data_view_indices`, shinyRows);
  }, [
    id,
    table,
    // Update with either sorting or columnFilters update!
    sorting,
    columnFilters,
  ]);

  // Restored for legacy purposes. Only send selected rows to Shiny when row selection is performed.
  useEffect(() => {
    if (!id) return;
    let shinyValue: number[] | null = null;
    if (selectionModes.row !== SelectionModes._rowEnum.NONE) {
      const rowSelectionKeys = selection.keys().toList();
      const rowsById = table.getSortedRowModel().rowsById;
      shinyValue = rowSelectionKeys
        .map((key) => {
          if (!(key in rowsById)) {
            return null;
          }
          return rowsById[key]!.index;
        })
        .filter((x): x is number => x !== null)
        .sort();
    }
    Shiny.setInputValue!(`${id}_selected_rows`, shinyValue);
  }, [id, selection, selectionModes, table]);

  // ### End row selection ############################################################

  // ### Editable cells ###############################################################
  // type TKey = DOMStringMap[string]: string
  type TKey = typeof HTMLTableRowElement.prototype.dataset.key;
  type TElement = HTMLTableRowElement;

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
      selection.clear();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [payload]);

  const headerRowCount = table.getHeaderGroups().length;

  // Maintain the .scrolling class: present if the amount of data in the table causes
  // vertical overflow, absent if not.
  useLayoutEffect(() => {
    // If no data, we're definitely not scrolling. Otherwise, we need to test.
    let scrolling = tableData.length > 0;
    if (scrolling) {
      // We need to add .scrolling before comparing scrollHeight/clientHeight. If not,
      // then if there's already a scrollworthy amount of data, we might get stuck in
      // non-scrolling state because the clientHeight is expanding within a fixed
      // container. (See https://github.com/posit-dev/py-shiny/issues/1549)
      containerRef.current?.classList.add("scrolling");
      const scrollHeight = containerRef.current?.scrollHeight;
      const clientHeight = containerRef.current?.clientHeight;
      if (scrollHeight && clientHeight && scrollHeight <= clientHeight) {
        scrolling = false;
      }
    }
    containerRef.current?.classList.toggle("scrolling", scrolling);
  }, [
    tableData.length,
    containerRef.current?.scrollHeight,
    containerRef.current?.clientHeight,
  ]);

  const makeHeaderKeyDown =
    (column: Column<unknown[], unknown>) => (event: React.KeyboardEvent) => {
      if (event.key === " " || event.key === "Enter") {
        column.toggleSorting(undefined, event.shiftKey);
      }
    };

  const measureEl = useVirtualizerMeasureWorkaround(rowVirtualizer);

  let className = `shiny-data-grid ${containerClass}`;
  if (fill) {
    className += " html-fill-item";
  }

  const includeRowNumbers =
    false && selectionModes.row !== SelectionModes._rowEnum.NONE;

  return (
    <>
      <div
        className={className}
        ref={containerRef}
        style={{ width, height, overflow: "auto" }}
      >
        <table
          className={tableClass + (withFilters ? " filtering" : "")}
          aria-rowcount={table.getRowCount()}
          aria-multiselectable={canMultiRowSelect}
          style={{
            width: width === null || width === "auto" ? undefined : "100%",
          }}
        >
          <thead ref={theadRef} style={{ backgroundColor: bgcolor }}>
            {table.getHeaderGroups().map((headerGroup, i) => (
              <tr
                // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                // @ts-ignore:next-line
                key={headerGroup.id}
                aria-rowindex={i + 1}
              >
                {includeRowNumbers && <th className="table-corner"></th>}

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
                      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                      // @ts-ignore:next-line
                      key={header.id}
                      colSpan={header.colSpan}
                      style={{
                        width: header.getSize(),
                        // When row numbers are displayed, this value is helpful instead of `width`
                        // minWidth: header.getSize()
                      }}
                      scope="col"
                      tabIndex={0}
                      onClick={header.column.getToggleSortingHandler()}
                      onKeyDown={makeHeaderKeyDown(header.column)}
                      className={
                        header.column.getCanSort() ? undefined : "header-html"
                      }
                    >
                      {headerContent}
                    </th>
                  );
                })}
              </tr>
            ))}
            {withFilters && (
              <tr className="filters">
                {includeRowNumbers && <th className="table-corner"></th>}
                {table.getFlatHeaders().map((header) => {
                  const thKey = `filter-${header.id}`;
                  return (
                    <th
                      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                      // @ts-ignore:next-line
                      key={thKey}
                    >
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
                    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                    // @ts-ignore:next-line
                    key={virtualRow.key}
                    data-index={virtualRow.index}
                    aria-rowindex={virtualRow.index + headerRowCount}
                    data-key={row.id}
                    ref={measureEl}
                    aria-selected={selection.has(row.id)}
                    tabIndex={-1}
                    {...selection.itemHandlers()}
                  >
                    {includeRowNumbers && (
                      <td className="row-number">{row.index + 1}</td>
                    )}
                    {row.getVisibleCells().map((cell) => {
                      // TODO-barret; Only send in the cell data that is needed;
                      const rowIndex = cell.row.index;
                      const columnIndex = cell.column.columnDef.meta!.colIndex;
                      const [cellEditInfo, _key] = getCellEditMapObj(
                        cellEditMap,
                        rowIndex,
                        columnIndex
                      );
                      const { cellStyle, cellClassName } = getCellStyle(
                        styleInfoMap,
                        "body",
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
                          cellStyle={cellStyle}
                          cellClassName={cellClassName}
                          setData={setTableData}
                          setCellEditMapAtLoc={setCellEditMapAtLoc}
                          selection={selection}
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
    keys.push(rowModel.rows[i]!.id);
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

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  renderValue(el: ShinyDataFrameOutput, data: any): void {
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

  if (bgColor === "transparent" || (m && parseFloat(m[4]!) === 0)) {
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
  errorRoot!: HTMLSpanElement;

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
