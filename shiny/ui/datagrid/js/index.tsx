import "./styles.scss";

import {
  ColumnDef,
  Row,
  RowModel,
  Table,
  TableOptions,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { VirtualItem, useVirtualizer } from "@tanstack/react-virtual";
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
import { SelectionMode, useSelection } from "./selection";
import { sortArrowDown, sortArrowUp } from "./sort-arrows";
import { useSummary } from "./table-summary";
import { CellData } from "./types";

// TODO: Right-align numeric columns, maybe change font
// TODO: Row selection
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

interface DataGridOptions {
  style?: "table" | "grid";
  summary?: boolean | string;
}

interface PandasData {
  columns: ReadonlyArray<string>;
  index: ReadonlyArray<string>;
  data: CellData;
  options: DataGridOptions;
  width?: string;
  height?: string;
}

interface ShinyDataGridProps {
  data: PandasData;
  bgcolor?: string;
  width?: string;
  height?: string;
}

const ShinyDataGrid: FC<ShinyDataGridProps> = (props) => {
  const { data, bgcolor, width, height } = props;
  const { columns, data: rowData } = data;

  const containerRef = useRef<HTMLDivElement>(null);
  const theadRef = useRef<HTMLTableSectionElement>(null);
  const tbodyRef = useRef<HTMLTableSectionElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: rowData.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 50,
  });

  // Reset scroll when dataset changes
  useLayoutEffect(() => {
    rowVirtualizer.scrollToOffset(0);
  }, [data]);

  const totalSize = rowVirtualizer.getTotalSize();
  const virtualRows = rowVirtualizer.getVirtualItems();

  const coldefs = useMemo<ColumnDef<unknown[], unknown>[]>(
    () =>
      columns.map((colname, i) => {
        return {
          accessorFn: (row, index) => {
            return row[i];
          },
          header: colname,
        };
      }),
    [columns]
  );

  // Not sure if it's even necessary to clone
  const dataClone = useMemo(() => [...rowData], [rowData]);

  const options: TableOptions<unknown[]> = {
    data: dataClone,
    columns: coldefs,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    //debugAll: true,
  };
  const table = useReactTable(options);

  // paddingTop and paddingBottom are to force the <tbody> to add up to the correct
  // virtual height
  const paddingTop = virtualRows.length > 0 ? virtualRows?.[0]?.start || 0 : 0;
  const paddingBottom =
    virtualRows.length > 0
      ? totalSize - (virtualRows?.[virtualRows.length - 1]?.end || 0)
      : 0;

  const summary = useSummary(
    data.options.summary,
    containerRef?.current,
    virtualRows,
    theadRef.current,
    rowData.length
  );

  const tableStyle = data.options.style ?? "grid";
  const containerClass =
    tableStyle === "grid" ? "shiny-data-grid-grid" : "shiny-data-grid-table";
  const tableClass = tableStyle === "table" ? "table table-sm" : null;

  const rowSelection = useSelection<string, HTMLTableRowElement>(
    SelectionMode.Multi,
    (el) => el.dataset.key,
    (fromKey, toKey) => {
      // TODO: Refactor into separate/pure function
      const rowModel = table.getSortedRowModel();
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
    },
    "selected"
  );

  // Reset sorting whenever dataset changes
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
  return (
    <>
      <div
        className={`shiny-data-grid ${containerClass} ${scrollingClass}`}
        ref={containerRef}
        style={{ width, maxHeight: height, overflow: "auto" }}
      >
        <table
          className={tableClass}
          aria-rowcount={rowData.length}
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
                          onClick={header.column.getToggleSortingHandler()}
                        >
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                          {{
                            asc: sortArrowUp,
                            desc: sortArrowDown,
                          }[header.column.getIsSorted() as string] ?? null}
                        </div>
                      )}
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>
          <tbody ref={tbodyRef}>
            {paddingTop > 0 && <tr style={{ height: `${paddingTop}px` }}></tr>}
            {virtualRows.map((virtualRow) => {
              const row = table.getRowModel().rows[virtualRow.index];
              return (
                <tr
                  key={virtualRow.key}
                  data-index={virtualRow.index}
                  aria-rowindex={virtualRow.index + headerRowCount}
                  data-key={row.id}
                  ref={rowVirtualizer.measureElement}
                  className={rowSelection.has(row.id) ? "selected" : undefined}
                  {...rowSelection.handlers()}
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

const roots = new WeakMap<HTMLElement, Root>();

class ShinyDataGridBinding extends Shiny.OutputBinding {
  find(scope: HTMLElement | JQuery<HTMLElement>): JQuery<HTMLElement> {
    return $(scope).find(".shiny-glide-data-grid-output");
  }

  renderValue(el: HTMLElement, data: unknown): void {
    let root = roots.get(el);
    if (!root) {
      root = createRoot(el);
      roots.set(el, root);
    }

    const id = this.getId(el);

    const {
      columns,
      index,
      data: rows,
      options,
      width,
      height,
    } = data as PandasData;

    root.render(
      data && (
        <StrictMode>
          <ShinyDataGrid
            data={data as PandasData}
            bgcolor={getComputedBgColor(el)}
            width={width ?? "100%"}
            height={height ?? "500px"}
          ></ShinyDataGrid>
        </StrictMode>
      )
    );
  }
}
Shiny.outputBindings.register(new ShinyDataGridBinding(), "shinyDataGrid");

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

function getStyle(el: Element, styleProp: string): string | undefined {
  // getComputedStyle can return null when we're inside a hidden iframe on
  // Firefox; don't attempt to retrieve style props in this case.
  // https://bugzilla.mozilla.org/show_bug.cgi?id=548397
  return document?.defaultView
    ?.getComputedStyle(el, null)
    ?.getPropertyValue(styleProp);
}

// class MyReactShinyBinding extends Shiny.ReactOutputBinding {
//   createComponent(): ReactElement {
//     function(props) {
//       const data = useShinyValue();
//     }
//   }
// }

// function MyReactDataGrid(props) {
//   const { data, error } = useShinyValue<PandasData>();
//   if (error) {
//     return <div>Bad</div>
//   }
//   // ...
// }
// Shiny.outputBindings.registerReact(MyReactDataGrid, ".shiny-glide-data-grid-output");
