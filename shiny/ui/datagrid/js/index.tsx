import "./styles.scss";

import React, {
  FC,
  useMemo,
  useRef,
  StrictMode,
  useEffect,
  useLayoutEffect,
} from "react";
import { createRoot, Root } from "react-dom/client";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  Row,
  RowModel,
  Table,
  TableOptions,
  useReactTable,
} from "@tanstack/react-table";
import { VirtualItem, useVirtualizer } from "@tanstack/react-virtual";
import { CellData } from "./types";
import { sortArrowUp, sortArrowDown } from "./sort-arrows";

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

  const summary = useMemo(() => {
    const summaryOption = data.options.summary ?? true;
    if (!summaryOption) {
      return null;
    }

    const template =
      typeof summaryOption === "string"
        ? summaryOption
        : "Viewing rows {start} through {end} of {total}";

    if (!containerRef.current) {
      return null;
    }
    if (virtualRows.length === 0) {
      return "Viewing 0 rows";
    }

    const top = containerRef.current.scrollTop;
    const bot =
      top + containerRef.current.clientHeight - theadRef.current.clientHeight;

    let firstRow: VirtualItem | null = null;
    let lastRow: VirtualItem | null = null;
    for (let i = 0; i < virtualRows.length; i++) {
      const item = virtualRows[i];
      const middle = item.start + item.size / 2;
      if (!firstRow && middle > top) {
        firstRow = item;
        lastRow = item;
      }
      if (middle > bot) {
        break;
      }
      lastRow = item;
    }

    if (firstRow.index === 0 && lastRow.index === rowData.length - 1) {
      // Viewing all rows; no need for a summary
      return null;
    }

    return template.replace(/\{(start|end|total)\}/g, (substr, token) => {
      if (token === "start") {
        return firstRow.index + 1 + "";
      } else if (token === "end") {
        return lastRow.index + 1 + "";
      } else if (token === "total") {
        return rowData.length + "";
      } else {
        return substr;
      }
    });
  }, [
    data.options.summary,
    containerRef.current?.scrollTop,
    containerRef.current?.scrollHeight,
    virtualRows,
    rowData,
  ]);

  const tableStyle = data.options.style ?? "grid";
  const containerClass =
    tableStyle === "grid" ? "shiny-data-grid-grid" : "shiny-data-grid-table";
  const tableClass = tableStyle === "table" ? "table table-sm" : null;

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
          style={{ width: width === null || width === "auto" ? null : "100%" }}
        >
          <thead ref={theadRef} style={{ backgroundColor: bgcolor }}>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <th
                      key={header.id}
                      colSpan={header.colSpan}
                      style={{ width: header.getSize() }}
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
                  ref={rowVirtualizer.measureElement}
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
      {summary && <div>{summary}</div>}
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
