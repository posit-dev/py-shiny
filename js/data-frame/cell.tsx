import { ColumnDef, RowModel, flexRender } from "@tanstack/react-table";
import { Cell } from "@tanstack/table-core";
import React, {
  FC,
  ChangeEvent as ReactChangeEvent,
  ReactElement,
  FocusEvent as ReactFocusEvent,
  KeyboardEvent as ReactKeyboardEvent,
  MouseEvent as ReactMouseEvent,
  useCallback,
  useEffect,
  useRef,
} from "react";
import { CellEdit, SetCellEditMapAtLoc } from "./cell-edit-map";
import { updateCellsData } from "./data-update";
import { SelectionSet } from "./selection";
import { CellStyle } from "./style-info";
import type { PatchInfo } from "./types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type HtmlDep = any;

// States
// # √ Ready
// # √ Editing
// # √ Saving / Disabled
// # √ Error
// # √ Saved
// # Cancelled (is Ready state?)
// # New
// # Added
// # Removed
export const CellStateEnum = {
  EditSaving: "EditSaving",
  EditSuccess: "EditSuccess",
  EditFailure: "EditFailure",
  Editing: "Editing",
  Ready: "Ready",
} as const;
export const CellStateClassEnum = {
  EditSaving: "cell-edit-saving",
  EditSuccess: "cell-edit-success",
  EditFailure: "cell-edit-failure",
  Editing: "cell-edit-editing",
  Ready: undefined,
} as const;
export type CellState = keyof typeof CellStateEnum;

type CellHtmlValue = {
  isShinyHtml: true;
  obj: { deps?: HtmlDep[]; html: string };
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const isShinyHtml = (x: any): x is CellHtmlValue => {
  return (
    x !== null && // Note: x === null has `typeof x === "object"`
    typeof x === "object" &&
    Object.prototype.hasOwnProperty.call(x, "isShinyHtml") &&
    x.isShinyHtml === true
  );
};
type CellValue = string | CellHtmlValue | null;
const getCellValueText = (cellValue: CellValue) => {
  if (cellValue === null) return "";
  if (isShinyHtml(cellValue)) return cellValue.obj.html;
  return cellValue;
};

interface TableBodyCellProps {
  key: string;
  rowId: string;
  containerRef: React.RefObject<HTMLDivElement>;
  cell: Cell<unknown[], unknown>;
  patchInfo: PatchInfo;
  columns: readonly string[];
  coldefs: readonly ColumnDef<unknown[], unknown>[];
  rowIndex: number;
  columnIndex: number;
  editCellsIsAllowed: boolean;
  getSortedRowModel: () => RowModel<unknown[]>;
  setData: (fn: (draft: unknown[][]) => void) => void;
  cellEditInfo: CellEdit | undefined;
  cellStyle: CellStyle | undefined;
  cellClassName: string | undefined;
  setCellEditMapAtLoc: SetCellEditMapAtLoc;
  selection: SelectionSet<string, HTMLTableRowElement>;
}

export const TableBodyCell: FC<TableBodyCellProps> = ({
  containerRef,
  rowId,
  cell,
  patchInfo,
  columns,
  coldefs,
  rowIndex,
  columnIndex,
  editCellsIsAllowed,
  getSortedRowModel,
  cellEditInfo,
  cellStyle,
  cellClassName,
  setData,
  setCellEditMapAtLoc,
  selection,
}) => {
  const initialValue = cell.getValue() as
    | string
    | { isShinyHtml: true; obj: { deps?: HtmlDep[]; html: string } }
    | null;

  const isHtmlColumn = cell.column.columnDef.meta!.isHtmlColumn;

  const cellValue = cellEditInfo?.value ?? initialValue;

  const cellState = cellEditInfo?.state ?? CellStateEnum.Ready;
  const errorTitle = cellEditInfo?.errorTitle;
  // Listen to boolean value of cellEditInfo. This allows for the cell state to be restored if esc is hit
  const isEditing = cellEditInfo?.isEditing ?? false;
  const editValue = cellEditInfo?.editValue ?? getCellValueText(cellValue);

  const tdRef = useRef<HTMLTableCellElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  // Keyboard navigation:
  // * When editing a cell:
  //   * On esc key:
  //     * √ Restore prior value / state / error
  //     * √ Move focus from input to td
  //   * On enter key:
  //     * √ Save value
  //     * √ Move to the cell below (or above w/ shift) and edit the new cell
  //     * X Should shift+enter add a newline in a cell?
  //   * On tab key:
  //     * √ Save value
  //     * √ Move to the cell to the right (or left w/ shift) and edit the new cell
  //   * Scrolls out of view:
  //     * Intercept keyboard events and execute the above actions
  //     * (Currently, there literally is no input DOM element to accept keyboard events)
  // TODO-barret-future; More keyboard navigation!
  //   * https://www.npmjs.com/package/@table-nav/react ?
  // * When focused on a td:
  //   * Allow for arrow key navigation
  //   * Have enter key enter edit mode for a cell
  //   * √ When a td is focused, Have esc key move focus to the table
  //   * X When table is focused, Have esc key blur the focus
  // TODO-barret-future; Combat edit mode being independent of selection mode
  // * In row / column selection mode, allow for arrow key navigation by focusing on a single cell, not a TR
  // * If a cell is focused,
  //   * `enter key` allows you to go into edit mode; If editing is turned off, the selection is toggled
  //   * `space key` allows you toggle the selection of the cell
  // * Arrow key navigation is required

  const resetEditing = useCallback(
    (
      {
        resetIsEditing = false,
        resetEditValue = false,
      }: { resetIsEditing?: boolean; resetEditValue?: boolean } = {
        resetIsEditing: true,
        resetEditValue: true,
      }
    ) => {
      setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
        if (resetIsEditing) obj_draft.isEditing = false;
        if (resetEditValue) obj_draft.editValue = undefined;
      });
    },
    [rowIndex, columnIndex, setCellEditMapAtLoc]
  );

  const handleEsc = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== "Escape") return;
    // Prevent default behavior
    e.preventDefault();
    e.stopPropagation();

    // Turn off editing and the _temp_ edit value
    resetEditing();
    selection.focusOffset(rowId, 0);
  };
  const handleTab = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== "Tab") return;
    // Prevent default behavior
    e.preventDefault();
    e.stopPropagation();

    const hasShift = e.shiftKey;

    let nextColumnIndex = columnIndex;
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const newColumnIndex = nextColumnIndex + (hasShift ? -1 : 1);

      if (newColumnIndex < 0 || newColumnIndex >= coldefs.length) {
        // If the new column index is out of bounds, quit
        return;
      }

      nextColumnIndex = newColumnIndex;
      // Repeat until the loop if the next column is not an HTML column
      if (coldefs[newColumnIndex]!.meta!.isHtmlColumn !== true) {
        break;
      }
    }

    // Submit changes to the current cell
    attemptUpdate();

    // Turn on editing in next cell!
    setCellEditMapAtLoc(rowIndex, nextColumnIndex, (obj_draft) => {
      obj_draft.isEditing = true;
    });
  };
  // TODO future: Make Cmd-Enter add a newline in a cell.
  const handleEnter = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== "Enter") return;
    // Prevent default behavior
    e.preventDefault();
    e.stopPropagation();

    const hasShift = e.shiftKey;

    const rowModel = getSortedRowModel();
    const sortedRowIndex = rowModel.rows.findIndex((row) => row.id === rowId);
    // Couldn't find row... silently quit
    if (sortedRowIndex < 0) {
      return;
    }
    const nextSortedRowIndex = sortedRowIndex! + (hasShift ? -1 : 1);

    if (nextSortedRowIndex < 0 || nextSortedRowIndex >= rowModel.rows.length) {
      // If the new row index is out of bounds, quit
      return;
    }

    // Submit changes to the current cell
    attemptUpdate();

    // Turn on editing in the next cell!
    // Get the original row index
    const targetRowIndex = rowModel.rows[nextSortedRowIndex]!.index;
    setCellEditMapAtLoc(targetRowIndex, columnIndex, (obj_draft) => {
      obj_draft.isEditing = true;
    });
  };

  const onInputKeyDown = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    [handleEsc, handleEnter, handleTab].forEach((fn) => fn(e));
  };

  const attemptUpdate = useCallback(() => {
    // Reset error title
    setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
      obj_draft.errorTitle = undefined;
    });

    // Only update if the string form of the value has changed
    if (`${getCellValueText(cellValue)}` === `${editValue}`) {
      // Reset all edit info
      resetEditing();
      // Set state to prior cell state
      setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
        obj_draft.state = cellState;
      });
      return;
    }

    // Only turn off editing for cell; Maintain all other edit info
    resetEditing({ resetIsEditing: true });

    // Set state to saving
    setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
      obj_draft.state = CellStateEnum.EditSaving;
    });

    // Update the data!
    // updateCellsData updates the underlying data via `setData` and `setCellEditMapAtLoc`
    updateCellsData({
      patchInfo: patchInfo,
      patches: [{ rowIndex, columnIndex, value: editValue }],
      onSuccess: (_patches) => {
        // Reset `editValue`
        resetEditing({ resetEditValue: true });

        // console.log("Success!!");
      },
      onError: (_err) => {
        // console.log("Error!!", _err);
        // // Do not reset edit value here so that users can "restore" their prior edit value
        // resetEditing({ resetEditValue: true });
      },
      columns,
      setData,
      setCellEditMapAtLoc,
    });
  }, [
    setCellEditMapAtLoc,
    rowIndex,
    columnIndex,
    cellValue,
    editValue,
    resetEditing,
    patchInfo,
    columns,
    setData,
    cellState,
  ]);

  // Select the input when it becomes editable
  useEffect(() => {
    if (!isEditing) return;
    if (!inputRef.current) return;

    inputRef.current.focus();
    inputRef.current.select();
  }, [isEditing]);

  // When editing a cell, set up a global click listener to reset edit info when
  // clicking outside of the cell
  // Use MouseDown event to match how selection is performed to prevent the click from bubbling up
  useEffect(() => {
    if (!isEditing) return;
    if (!tdRef.current) return;
    if (!inputRef.current) return;

    // TODO-barret; Restore cursor position and text selection here

    const onEdtingCellMouseDown = (e: MouseEvent) => {
      if (!tdRef.current?.contains(e.target as Node)) return;
      // Prevent the click from bubbling up to the body click listener
      e.stopPropagation();

      // Do not stop the event from preventing default as we need the click to work for the text area!
      // e.preventDefault();
    };
    const curRef = tdRef.current; // Capture the current ref
    curRef.addEventListener("mousedown", onEdtingCellMouseDown);

    // Set up global click listener to reset edit info
    const onBodyMouseDown = (e: MouseEvent) => {
      if (e.target === inputRef.current) return;

      attemptUpdate();
      // Turn off editing for this cell
      resetEditing();
    };
    document.body.addEventListener("mousedown", onBodyMouseDown);

    // Tear down global click listener when we're done
    return () => {
      curRef.removeEventListener("mousedown", onEdtingCellMouseDown);
      document.body.removeEventListener("mousedown", onBodyMouseDown);
    };
  }, [
    cellState,
    attemptUpdate,
    rowIndex,
    columnIndex,
    isEditing,
    resetEditing,
  ]);

  // Reselect the input when it comes into view!
  // (It could be scrolled out of view and then back into view)
  function onFocus(e: ReactFocusEvent<HTMLTextAreaElement>) {
    if (isEditing) {
      e.target.select();
    }
  }

  function onChange(e: ReactChangeEvent<HTMLTextAreaElement>) {
    // Update edit value to cell map
    setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
      obj_draft.editValue = e.target.value;
    });
  }

  // // https://medium.com/@oherterich/creating-a-textarea-with-dynamic-height-using-react-and-typescript-5ed2d78d9848
  // // Updates the height of a <textarea> when the value changes.
  // const useAutosizeTextArea = (
  //   textAreaRef: HTMLTextAreaElement | null,
  //   value: string
  // ) => {
  //   useEffect(() => {
  //     if (textAreaRef) {
  //       // We need to reset the height momentarily to get the correct scrollHeight for the textarea
  //       textAreaRef.style.height = "0px";
  //       const scrollHeight = textAreaRef.scrollHeight;

  //       // We then set the height directly, outside of the render loop
  //       // Trying to set this with state or a ref will product an incorrect value.
  //       textAreaRef.style.height = scrollHeight + "px";
  //     }
  //   }, [textAreaRef, value]);
  // };
  // useAutosizeTextArea(inputRef.current, value as string);

  let onCellDoubleClick:
    | ((e: ReactMouseEvent<HTMLTableCellElement>) => void)
    | undefined = undefined;
  let content: ReactElement | ReturnType<typeof flexRender> | undefined =
    undefined;
  const cellTitle = errorTitle;
  let tableCellClass: string | undefined = cellClassName;
  const addToTableCellClass = (x: string | undefined) => {
    if (!x) return;
    if (tableCellClass) {
      tableCellClass += " ";
      tableCellClass += x;
    } else {
      tableCellClass = x;
    }
  };
  addToTableCellClass(
    CellStateClassEnum[isEditing ? CellStateEnum.Editing : cellState]
  );
  let attemptRenderAsync = false;

  let editContent: ReactElement | null = null;
  if (cellState === CellStateEnum.EditSaving) {
    // If saving, do not allow any clicks or edits
    content = editValue as string;
  } else {
    if (isEditing) {
      editContent = (
        <textarea
          value={String(editValue)}
          onChange={onChange}
          // onBlur={onBlur}
          onFocus={onFocus}
          onKeyDown={onInputKeyDown}
          ref={inputRef}
          // style={{ width: "100%", height: "100%" }}
        />
      );
    } else if (isHtmlColumn) {
      addToTableCellClass("cell-html");
    } else {
      // `isEditing` is `false` and not an HTML column, so we can allow for double clicks to go into edit mode

      // Only allow transition to edit mode if the cell can be edited
      if (editCellsIsAllowed) {
        addToTableCellClass("cell-editable");
        onCellDoubleClick = (e: ReactMouseEvent<HTMLTableCellElement>) => {
          // Do not prevent default or stop propagation here!
          // Other methods need to be able to handle the event as well. e.g. `onBodyClick` above.
          // e.preventDefault();
          // e.stopPropagation();

          // Set this cell to editing mode
          setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
            obj_draft.isEditing = true;
            obj_draft.editValue = getCellValueText(cellValue) as string;
          });
        };
      }
    }
    if (isShinyHtml(cellValue)) {
      attemptRenderAsync = true;
    } else {
      // Render cell contents like normal
      content = flexRender(cell.column.columnDef.cell, cell.getContext());
    }
  }

  useEffect(() => {
    if (!tdRef.current) return;
    if (!attemptRenderAsync) return;
    if (!isShinyHtml(cellValue)) return;

    // TODO-future; Use faster way to make a deep copy
    const cellValueObjDeepCopy = JSON.parse(JSON.stringify(cellValue.obj));
    // Render the Shiny content asynchronously to the table's cell
    window.Shiny.renderContentAsync(tdRef.current, cellValueObjDeepCopy);

    const curTdRef = tdRef.current;

    return () => {
      // Unbind all Shiny inputs and outputs within the cell
      window.Shiny.unbindAll!(curTdRef);
      // Remove DOM elements from cell inserted by `window.Shiny.renderContentAsync`
      curTdRef.replaceChildren("");
    };
  }, [tdRef, cellValue, rowIndex, columnIndex, attemptRenderAsync]);

  return (
    <td
      ref={tdRef}
      onDoubleClick={onCellDoubleClick}
      title={cellTitle}
      className={tableCellClass}
      style={{ ...cellStyle }}
    >
      {editContent}
      {content}
    </td>
  );
};

// // TODO-barret; Consider using https://www.npmjs.com/package/react-contenteditable !
// const cellValue = cell.getValue();
// const cellValueType = typeof cellValue;
// const cellContentIsEditable =
//   cellValueType === "string" ||
//   cellValueType === "number" ||
//   cellValueType === "boolean" ||
//   cellValueType === "undefined" ||
//   cellValue === null;
// if (cellContentIsEditable) {
//   // cellContentEditable = ""plaintext-only";
//   cellContentEditable = true;
// }
// const onInput = (e: ReactChangeEvent<HTMLTableCellElement>) => {
//   console.log("on input!", e, rowIndex, columnIndex, e.target.textContent);
// };
// td attrs for below
// contentEditable={cellContentEditable}
// onInput={onInput}
