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
  GridSelection,
  CompactSelection,
} from "@glideapps/glide-data-grid";
import React, { ReactElement } from "react";
import { createRoot, Root } from "react-dom/client";
import { SpriteManager } from "@glideapps/glide-data-grid/dist/ts/data-grid/data-grid-sprites";

import { CellData, SortEntry } from "./types";
import { useSortColumns } from "./grid-sort";

interface PandasData {
  columns: ReadonlyArray<string>;
  index: ReadonlyArray<string>;
  data: CellData;
  options: DataGridOptions;
  width?: string;
  height?: string;
}

interface DataGridOptions {
  row_selection: boolean;
  column_selection: boolean;
  range_selection: boolean;
  cell_selection: boolean;
}

interface WrappedGridProps {
  id: string;
  columns: ReadonlyArray<string>;
  index: ReadonlyArray<string>;
  rows: CellData;
  options: DataGridOptions;
  width?: string;
  height?: string;
}

const WrappedGrid: React.FC<WrappedGridProps> = (props) => {
  const { id, columns, index, rows, options, height, width } = props;

  const { currentSort, sortedData, onSortClick, mapSortedRowToUnsorted } =
    useSortColumns({
      rows,
    });

  let editable = true; // TODO: Make configurable

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
          readonly: !editable,
        };
      } else if (typeof d === "number") {
        kind = GridCellKind.Number;
        return {
          kind,
          allowOverlay: true,
          displayData: d + "",
          data: d,
          readonly: !editable,
        };
      } else if (typeof d === "boolean") {
        kind = GridCellKind.Boolean;
        return {
          kind,
          allowOverlay: false,
          data: d,
          readonly: !editable,
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
        readonly: !editable,
      };
    },
    [sortedData] // dependencies
  );

  const onCellEdited = React.useCallback(
    (cell: Item, newValue: EditableGridCell): void => {
      Shiny.setInputValue(
        props.id + "_cell_edit",
        {
          col: cell[0],
          // Go from row number in the visible grid, to the row
          // number in the original data.
          row: mapSortedRowToUnsorted(cell[1]),
          sorted_row: cell[1],
          new_value: newValue.data,
          cell_kind: newValue.kind,
        },
        { priority: "event" }
      );
    },
    [mapSortedRowToUnsorted]
  );

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

      if (columnIndex < 0) {
        return false;
      }

      let x = rect.x;
      let x2 = x + rect.width;
      x += theme.cellHorizontalPadding;
      x2 -= theme.cellHorizontalPadding;
      let y = rect.y + rect.height / 2;

      const sortable = true;
      const sort: "asc" | "desc" | null =
        currentSort?.columnIndex !== columnIndex
          ? null
          : currentSort.desc
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
    [currentSort]
  );
  const ref = React.useRef<DataEditorRef>();

  // Update header cells affected by changes to the sort
  React.useEffect(() => {
    const col = currentSort?.columnIndex;
    if (col !== null) {
      ref.current.updateCells([{ cell: [col, -1] }]);
    }
    return () => {
      if (col !== null) {
        // When currentSort changes next time, re-update the same header because it's
        // probably lost its sort arrow now.
        ref.current.updateCells([{ cell: [col, -1] }]);
      }
    };
  }, [currentSort]);

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

  const colDefs = columns.map((col) => {
    return {
      title: col,
      id: col,
      hasMenu: true, // Used for sort indicator
    };
  });

  const [gridSelection, setGridSelection] =
    React.useState<GridSelection>(undefined);

  const onGridSelectionChange = (newSelection: GridSelection) => {
    // if (!options.cell_selection && !options.range_selection && newSelection.current?.cell) {
    //   // Convert cell selection to row selection
    //   newSelection = {
    //     rows: CompactSelection.fromSingleSelection(
    //       newSelection.current.cell[1]
    //     ),
    //     columns: CompactSelection.empty(),
    //   };
    // }
    setGridSelection(newSelection);

    Shiny.setInputValue(
      props.id + "_column_selection",
      newSelection.columns.toArray() // TODO: Pass column names
    );
    Shiny.setInputValue(
      props.id + "_row_selection",
      newSelection.rows.toArray().map(mapSortedRowToUnsorted)
    );
    if (newSelection.current?.cell) {
      let [col, row] = newSelection.current!.cell;
      row = mapSortedRowToUnsorted(row);
      Shiny.setInputValue(props.id + "_cell_selection", { col, row });
    } else {
      Shiny.setInputValue(props.id + "_cell_selection", null);
    }
    if (newSelection.current?.range) {
      const { x, y, width, height } = newSelection.current?.range;
      const cols = [];
      for (let i = x; i < x + width; i++) {
        cols.push(i);
      }
      const rows = [];
      for (let i = y; i < y + height; i++) {
        rows.push(i);
      }
      Shiny.setInputValue(props.id + "_range_selection", {
        cols,
        rows: rows.map(mapSortedRowToUnsorted),
      });
    } else {
      Shiny.setInputValue(props.id + "_range_selection", null);
    }
  };

  return (
    <DataEditor
      ref={ref}
      getCellContent={getContent}
      // getCellsForSelection={true}
      columns={colDefs}
      rows={rows.length}
      onCellEdited={onCellEdited}
      drawHeader={drawHeaderCustom}
      onHeaderMenuClick={onSortClick}
      gridSelection={gridSelection}
      onGridSelectionChange={onGridSelectionChange}
      height={props.height}
      width={props.width}
      rowMarkers="clickable-number"
      rowSelect={options.row_selection ? "multi" : "none"}
      columnSelect={options.column_selection ? "multi" : "none"}
      rangeSelect={
        options.range_selection
          ? "rect"
          : options.cell_selection
          ? "cell"
          : "none"
      }
    />
  );
};

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
        <WrappedGrid
          id={id}
          columns={columns}
          index={index}
          rows={rows}
          options={options}
          width={width}
          height={height}
        />
      )
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
