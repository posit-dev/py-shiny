import "./styles.css";

import React, { FC, useMemo, useRef, StrictMode } from "react";
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
import { useVirtual } from "@tanstack/react-virtual";
import { CellData } from "./types";

interface DataGridOptions {}

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
}

const sortCommonProps = {
  viewBox: [-1, -1, 2, 2].map((x) => x * 1.4).join(" "),
  width: "13",
  height: "13",
  style: { paddingLeft: "3px" },
};
const sortPathCommonProps = {
  stroke: "#333333",
  strokeWidth: "0.6",
  fill: "transparent",
};
const sortArrowUp = (
  <svg xmlns="http://www.w3.org/2000/svg" {...sortCommonProps}>
    <path
      d="M -1 0.5 L 0 -0.5 L 1 0.5"
      {...sortPathCommonProps}
      strokeLinecap="round"
    />
  </svg>
);
const sortArrowDown = (
  <svg xmlns="http://www.w3.org/2000/svg" {...sortCommonProps}>
    <path
      d="M -1 -0.5 L 0 0.5 L 1 -0.5"
      {...sortPathCommonProps}
      strokeLinecap="round"
    />
  </svg>
);

//const sortArrowUp = <span className="sort-arrow sort-arrow-up"> ▲</span>;
//const sortArrowDown = <span className="sort-arrow sort-arrow-down"> ▼</span>;

const ShinyDataGrid: FC<ShinyDataGridProps> = (props) => {
  const { data, bgcolor } = props;
  const { columns, data: rowData } = data;

  const containerRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtual({
    parentRef: containerRef,
    size: rowData.length,
    overscan: 100,
  });
  const { virtualItems: virtualRows, totalSize } = rowVirtualizer;

  const coldefs = useMemo<ColumnDef<unknown>[]>(
    () =>
      columns.map((colname, i) => {
        return {
          accessorFn: (row, index) => {
            return (row as any)[i];
          },
          header: colname,
        };
      }),
    [columns]
  );

  // Not sure if it's even necessary to clone
  const dataClone = useMemo(() => [...rowData], [rowData]);

  const options: TableOptions<unknown> = {
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

  return (
    <div
      className="shiny-data-grid"
      ref={containerRef}
      style={{ height: "400px", overflow: "auto" }}
    >
      <table className="table table-sm">
        <thead style={{ backgroundColor: bgcolor }}>
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
                          cursor: header.column.getCanSort() ? "pointer" : null,
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
        <tbody>
          {paddingTop > 0 && (
            <tr>
              <td style={{ height: `${paddingTop}px` }} />
            </tr>
          )}
          {virtualRows.map((virtualRow) => {
            console.log(virtualRow.index);
            const row = table.getRowModel().rows[virtualRow.index] as Row<any>;
            return (
              <tr key={row.id}>
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
            <tr>
              <td style={{ height: `${paddingBottom}px` }} />
            </tr>
          )}
        </tbody>
      </table>
    </div>
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
