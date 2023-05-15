import "@glideapps/glide-data-grid/dist/index.css";

import {
  DataEditor,
  GridColumn,
  GridCell,
  GridCellKind,
  Item,
  EditableGridCell,
  DataEditorRef,
  Theme,
  Rectangle,
  getMiddleCenterBias,
} from "@glideapps/glide-data-grid";
import React, { ReactElement } from "react";
import { createRoot, Root } from "react-dom/client";
import { SpriteManager } from "@glideapps/glide-data-grid/dist/ts/data-grid/data-grid-sprites";

interface DummyItem {
  name: string;
  company: string;
  email: string;
  phone: string;
}
type CellData = ReadonlyArray<ReadonlyArray<any>>;
interface PandasData {
  columns: ReadonlyArray<string>;
  // index: ReadonlyArray<string>;
  data: CellData;
}

interface WrappedGridProps {
  id: string;
  data: PandasData;
  width?: string;
  height?: string;
}

interface SortEntry {
  columnIndex: number;
  desc: boolean;
}

const WrappedGrid: React.FC<WrappedGridProps> = (props) => {
  const data = props.data;

  const [sortList, setSortList] = React.useState<readonly SortEntry[]>([]);

  const { data: sortedData, rowNums: originalRowNums } = React.useMemo<{
    data: CellData;
    rowNums: ReadonlyArray<number>;
  }>(() => {
    return applySort(data.data, sortList, (rowA, rowB, columnIndex) => {
      const a = rowA[columnIndex];
      const b = rowB[columnIndex];
      return a < b ? -1 : a > b ? 1 : 0;
    });
  }, [data.data, sortList]);

  const getContent = React.useCallback(
    (cell: Item): GridCell => {
      const [col, row] = cell;
      let d: any = sortedData[row][col];

      let kind: GridCellKind;
      if (typeof d === "string") {
        kind = GridCellKind.Text;
        return {
          kind,
          allowOverlay: true,
          displayData: d + "",
          data: d,
          readonly: false,
        };
      } else if (typeof d === "number") {
        kind = GridCellKind.Number;
        return {
          kind,
          allowOverlay: true,
          displayData: d + "",
          data: d,
          readonly: false,
        };
      } else if (typeof d === "boolean") {
        kind = GridCellKind.Boolean;
        return {
          kind,
          allowOverlay: false,
          data: d,
          readonly: false,
        };
      } else {
        // TODO: Figure out what to do in this case
        kind = GridCellKind.Text;
        d = d + "";
      }

      return {
        kind,
        allowOverlay: false,
        displayData: d + "",
        data: d,
        readonly: false,
      };
    },
    [sortedData] // dependencies
  );

  console.log(originalRowNums);

  const onCellEdited = React.useCallback(
    (cell: Item, newValue: EditableGridCell): void => {
      Shiny.setInputValue(
        props.id + "_cell_edit",
        {
          col: cell[0],
          // Go from row number in the visible grid, to the row
          // number in the original data.
          row: originalRowNums[cell[1]],
          sorted_row: cell[1],
          new_value: newValue.data,
          cell_kind: newValue.kind,
        },
        { priority: "event" }
      );
    },
    [originalRowNums]
  );

  const columns = data.columns.map((col) => {
    return {
      title: col,
      id: col,
      hasMenu: true, // Used for sort indicator
    };
  });

  const drawHeaderCustom = React.useCallback(
    (args: {
      ctx: CanvasRenderingContext2D;
      column: GridColumn;
      columnIndex: number;
      theme: Theme;
      rect: Rectangle;
      hoverAmount: number;
      isSelected: boolean;
      isHovered: boolean;
      hasSelectedCell: boolean;
      spriteManager: SpriteManager;
      menuBounds: Rectangle;
    }): boolean => {
      const { ctx, column, columnIndex, theme, rect, isSelected } = args;

      let x = rect.x;
      let x2 = x + rect.width;
      x += theme.cellHorizontalPadding;
      x2 -= theme.cellHorizontalPadding;
      let y = rect.y + rect.height / 2;

      const sortable = true;
      const lastSortEntry =
        sortList.length === 0 ? null : sortList[sortList.length - 1];
      const sort: "asc" | "desc" | null =
        lastSortEntry?.columnIndex !== columnIndex
          ? null
          : lastSortEntry.desc
          ? "desc"
          : "asc";

      if (sortable) {
        ctx.save();
        try {
          ctx.strokeStyle = isSelected
            ? theme.textHeaderSelected
            : theme.textHeader;
          ctx.lineWidth = 2;
          const TRIANGLE_WIDTH = 8;
          const TRIANGLE_HEIGHT = 4;
          ctx.beginPath();
          if (sort === "asc") {
            // Up arrow
            ctx.moveTo(x2, y + TRIANGLE_HEIGHT / 2);
            ctx.lineTo(x2 - TRIANGLE_WIDTH / 2, y - TRIANGLE_HEIGHT / 2);
            ctx.lineTo(x2 - TRIANGLE_WIDTH, y + TRIANGLE_HEIGHT / 2);
          } else if (sort === "desc") {
            // Down arrow
            ctx.moveTo(x2, y - TRIANGLE_HEIGHT / 2);
            ctx.lineTo(x2 - TRIANGLE_WIDTH / 2, y + TRIANGLE_HEIGHT / 2);
            ctx.lineTo(x2 - TRIANGLE_WIDTH, y - TRIANGLE_HEIGHT / 2);
          } else {
            // Up/Down arrows (sortable, but not sorted)
            const Y_OFFSET = 1;
            const X_OFFSET = 1;
            ctx.lineWidth = 1.5;
            ctx.moveTo(x2 - X_OFFSET, y - Y_OFFSET);
            ctx.lineTo(x2 - TRIANGLE_WIDTH / 2, y - TRIANGLE_HEIGHT);
            ctx.lineTo(x2 - TRIANGLE_WIDTH + X_OFFSET, y - Y_OFFSET);
            ctx.moveTo(x2 - X_OFFSET, y + Y_OFFSET);
            ctx.lineTo(x2 - TRIANGLE_WIDTH / 2, y + TRIANGLE_HEIGHT);
            ctx.lineTo(x2 - TRIANGLE_WIDTH + X_OFFSET, y + Y_OFFSET);
            ctx.globalAlpha = 0.5;
          }
          ctx.stroke();
          x2 -= TRIANGLE_WIDTH;
          x2 -= theme.cellHorizontalPadding;
        } finally {
          ctx.restore();
        }
      }

      y += getMiddleCenterBias(
        ctx,
        `${theme.headerFontStyle} ${theme.fontFamily}`
      );
      ctx.fillStyle = isSelected ? theme.textHeaderSelected : theme.textHeader;
      ctx.fillText(column.title, x, y, x2 - x);
      return true;
    },
    [sortList]
  );
  const ref = React.useRef<DataEditorRef>();

  const onSortClick = React.useCallback(
    (col: number, screenPosition: Rectangle): void => {
      // We need to be careful here to not mutate any items; neither the sortList array
      // nor the SortEntry objects it contains.

      // Decide whether we should sort descending or ascending.
      let targetDesc: boolean;
      const idx = sortList.findIndex(({ columnIndex }) => columnIndex === col);
      if (idx >= 0) {
        if (idx === sortList.length - 1) {
          // 1. If the most recent sort entry is for this column, flip the direction.
          targetDesc = !sortList[idx].desc;
        } else {
          // 2. If we have an earlier sort entry for this column, use that direction.
          //    I'm hoping this is convenient when repeatedly flipping back and forth
          //    between two columns, one of which only makes sense in descending order.)
          targetDesc = sortList[idx].desc;
        }
      } else {
        // 3. In the absence of other info, use ascending.
        targetDesc = false;
      }

      // Need this just so we know to call updateCell on the previous sort item
      const lastSortCol =
        sortList.length === 0
          ? null
          : sortList[sortList.length - 1].columnIndex;

      setSortList(
        sortList
          .filter(({ columnIndex }) => columnIndex !== col)
          .concat({ columnIndex: col, desc: targetDesc })
      );

      // TODO: Ask Nick if there's a better way to do this
      setTimeout(() => {
        // If this doesn't happen in a setTimeout, the redraw occurs using the old copy
        // of the drawHeaderCustom callback
        ref.current.updateCells([{ cell: [col, -1] }]);
        if (lastSortCol !== null && lastSortCol !== col) {
          ref.current.updateCells([{ cell: [lastSortCol, -1] }]);
        }
      }, 0);
    },
    [sortList]
  );

  const darkTheme: Partial<Theme> = {
    accentColor: "#8c96ff",
    accentLight: "rgba(202, 206, 255, 0.253)",

    textDark: "#ffffff",
    textMedium: "#b8b8b8",
    textLight: "#a0a0a0",
    textBubble: "#ffffff",

    bgIconHeader: "#b8b8b8",
    fgIconHeader: "#000000",
    textHeader: "#a1a1a1",
    textHeaderSelected: "#000000",

    bgCell: "#16161b",
    bgCellMedium: "#202027",
    bgHeader: "#212121",
    bgHeaderHasFocus: "#474747",
    bgHeaderHovered: "#404040",

    bgBubble: "#212121",
    bgBubbleSelected: "#000000",

    bgSearchResult: "#423c24",

    borderColor: "rgba(225,225,225,0.2)",
    drilldownBorder: "rgba(225,225,225,0.4)",

    linkColor: "#4F5DFF",

    headerFontStyle: "bold 14px",
    baseFontStyle: "13px",
    fontFamily:
      "Inter, Roboto, -apple-system, BlinkMacSystemFont, avenir next, avenir, segoe ui, helvetica neue, helvetica, Ubuntu, noto, arial, sans-serif",

    // Should add these too:

    // accentFg: "",
    // cellHorizontalPadding: 0,
    // cellVerticalPadding: 0,
    // headerIconSize: 0,
    // editorFontSize: "",
    // lineHeight: 0
  };

  return (
    <DataEditor
      ref={ref}
      getCellContent={getContent}
      columns={columns}
      rows={data.data.length}
      onCellEdited={onCellEdited}
      drawHeader={drawHeaderCustom}
      onHeaderMenuClick={onSortClick}
      height={props.height}
      width={props.width}
      rowMarkers="clickable-number"
      // rangeSelect?: "none" | "cell" | "rect" | "multi-cell" | "multi-rect"; // default rect
      // columnSelect?: "none" | "single" | "multi"; // default multi
      // rowSelect?: "none" | "single" | "multi"; // default multi
    />
  );
};

/**
 * Sorts items by the comparator, but instead of returning a sorted array, returns the
 * indices of the items in sorted order.
 */
function sortOrder<T>(
  items: ReadonlyArray<T>,
  comparator: (a: T, b: T) => number
): Array<number> {
  const indices = items.map((_, index) => index);
  indices.sort((indexA, indexB) => comparator(items[indexA], items[indexB]));
  return indices;
}

/**
 * Retrieve items[indices]
 */
function mget<T>(
  items: ReadonlyArray<T>,
  indices: ReadonlyArray<number>
): ReadonlyArray<T> {
  return indices.map((i) => items[i]);
}

function applySort<T>(
  data: readonly T[],
  sortList: readonly SortEntry[],
  comparator: (a: T, b: T, columnIndex: number) => number
): { data: readonly T[]; rowNums: readonly number[] } {
  if (sortList.length === 0) {
    return { data, rowNums: data.map((_, i) => i) };
  }
  let newRows = [...data] as readonly T[];
  let originalRowNums = newRows.map((_, i) => i) as readonly number[];
  sortList.forEach(({ columnIndex, desc }) => {
    const descFactor = desc ? -1 : 1;
    const sortIndices = sortOrder(
      newRows,
      (a, b) => descFactor * comparator(a, b, columnIndex)
    );
    newRows = mget(newRows, sortIndices);
    originalRowNums = mget(originalRowNums, sortIndices);
  });
  return { data: newRows, rowNums: originalRowNums };
}

const roots = new WeakMap<HTMLElement, Root>();

class GlideDataGridBinding extends Shiny.OutputBinding {
  find(scope: HTMLElement | JQuery<HTMLElement>): JQuery<HTMLElement> {
    return $(scope).find(".shiny-glide-data-grid-output");
  }

  renderValue(el: HTMLElement, data: unknown): void {
    if (!document.querySelector("#portal")) {
      const portalDiv = document.createElement("div");
      portalDiv.id = "portal";
      portalDiv.style.position = "fixed";
      portalDiv.style.left = "0";
      portalDiv.style.top = "0";
      portalDiv.style.zIndex = "9999";
      document.body.appendChild(portalDiv);
    }

    let root = roots.get(el);
    if (!root) {
      root = createRoot(el);
      roots.set(el, root);
    }

    const id = this.getId(el);

    root.render(
      data && <WrappedGrid id={id} data={data as PandasData} height="500px" />
    );
  }
}
Shiny.outputBindings.register(new GlideDataGridBinding(), "shinyGlideDataGrid");

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
