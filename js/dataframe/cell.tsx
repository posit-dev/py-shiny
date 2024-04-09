import { RowModel, flexRender } from "@tanstack/react-table";
import { VirtualItem } from "@tanstack/react-virtual";
import { Cell } from "@tanstack/table-core";
import dompurify from "dompurify";
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
import type { PatchInfo } from "./types";

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
const CellStateClassEnum = {
  EditSaving: "cell-edit-saving",
  EditSuccess: "cell-edit-success",
  EditFailure: "cell-edit-failure",
  Editing: "cell-edit-editing",
  Ready: undefined,
} as const;
export type CellState = keyof typeof CellStateEnum;

const isShinyHtmlFn = (
  x: any
): x is { isShinyHtml: true; obj: { deps?: HtmlDep[]; html: string } } => {
  return (
    x !== null &&
    typeof x !== "string" &&
    Object.prototype.hasOwnProperty.call(x, "isShinyHtml") &&
    x.isShinyHtml === true
  );
};

interface TableBodyCellProps {
  key: string;
  rowId: string;
  containerRef: React.RefObject<HTMLDivElement>;
  cell: Cell<unknown[], unknown>;
  patchInfo: PatchInfo;
  columns: readonly string[];
  rowIndex: number;
  columnIndex: number;
  editCellsIsAllowed: boolean;
  getSortedRowModel: () => RowModel<unknown[]>;
  setData: (fn: (draft: unknown[][]) => void) => void;
  cellEditInfo: CellEdit | undefined;
  setCellEditMapAtLoc: SetCellEditMapAtLoc;
}

export const TableBodyCell: FC<TableBodyCellProps> = ({
  containerRef,
  rowId,
  cell,
  patchInfo,
  columns,
  rowIndex,
  columnIndex,
  editCellsIsAllowed,
  getSortedRowModel,
  cellEditInfo,
  setData,
  setCellEditMapAtLoc,
}) => {
  const initialValue = cell.getValue() as
    | string
    | { isShinyHtml: true; obj: { deps?: HtmlDep[]; html: string } }
    | null;

  const isHtmlColumn = cell.column.columnDef.meta!.isHtmlColumn;

  // const isShinyHtml: boolean =
  //   initialValue !== null &&
  //   typeof initialValue !== "string" &&
  //   Object.prototype.hasOwnProperty.call(initialValue, "isShinyHtml") &&
  //   initialValue.isShinyHtml === true;
  // const valueHasHtmlKey =
  //   isHtmlColumn &&
  //   typeof initialValue !== "string" &&
  //   Object.prototype.hasOwnProperty.call(initialValue, "html");

  const cellValue = cellEditInfo?.value ?? initialValue;
  const getCellValueText = useCallback(() => {
    if (isShinyHtmlFn(cellValue)) {
      return cellValue.obj.html;
    }
    return cellValue as string;
  }, [cellValue]);

  const cellState = cellEditInfo?.state ?? CellStateEnum.Ready;
  const errorTitle = cellEditInfo?.errorTitle;
  // Listen to boolean value of cellEditInfo. This allows for the cell state to be restored if esc is hit
  const isEditing = cellEditInfo?.isEditing ?? false;
  const editValue = cellEditInfo?.editValue ?? getCellValueText();

  // if (isEditing) console.log("editValue", editValue, rowIndex, columnIndex);

  const tdRef = useRef<HTMLTableCellElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  // editCellsIsAllowed = editCellsIsAllowed && !isHtmlColumn;

  // Keyboard navigation:
  // * When editing a cell:
  //   * On esc key:
  //     * √ Restore prior value / state / error
  //     * Move focus from input to td
  //   * On enter key:
  //     * √ Save value
  //     * √ Move to the cell below (or above w/ shift) and edit the new cell
  //     * Should shift+enter add a newline in a cell?
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
  //   * When a td is focused, Have esc key move focus to the table
  //   * When table is focused, Have esc key blur the focus
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

    // Turn off editing and the _temp_ edit value
    resetEditing();
  };
  const handleTab = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== "Tab") return;
    // Prevent default behavior
    e.preventDefault();

    const hasShift = e.shiftKey;

    const newColumnIndex = columnIndex! + (hasShift ? -1 : 1);

    // Submit changes to the current cell
    attemptUpdate();

    if (newColumnIndex < 0 || newColumnIndex >= columns.length) {
      // If the new column index is out of bounds, quit
      return;
    }

    // Turn on editing in next cell!
    setCellEditMapAtLoc(rowIndex, newColumnIndex, (obj_draft) => {
      obj_draft.isEditing = true;
    });
  };
  // TODO future: Make Cmd-Enter add a newline in a cell.
  const handleEnter = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== "Enter") return;
    // Prevent default behavior
    e.preventDefault();

    const hasShift = e.shiftKey;

    const rowModel = getSortedRowModel();
    const sortedRowIndex = rowModel.rows.findIndex((row) => row.id === rowId);
    // Couldn't find row... silently quit
    if (sortedRowIndex < 0) {
      return;
    }
    const nextSortedRowIndex = sortedRowIndex! + (hasShift ? -1 : 1);

    // Submit changes to the current cell
    attemptUpdate();

    if (nextSortedRowIndex < 0 || nextSortedRowIndex >= rowModel.rows.length) {
      // If the new row index is out of bounds, quit
      return;
    }

    // Turn on editing in the next cell!
    // Get the original row index
    const targetRowIndex = rowModel.rows[nextSortedRowIndex].index;
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
    if (`${getCellValueText()}` === `${editValue}`) {
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
    // Replace cell content to remove any HTML based cell values
    // Can not use window.Shiny.renderContentAsync(tdRef.current, null) as the method is async;
    // tdRef.current?.replaceChildren("");
    // // Reset any shiny bindings that have occurred in cell
    // window.Shiny.bindAll();

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
    getCellValueText,
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
  useEffect(() => {
    if (!isEditing) return;
    if (!inputRef.current) return;

    // TODO-barret; Restore cursor position and text selection here

    // Set up global click listener to reset edit info
    const onBodyClick = (e: MouseEvent) => {
      if (e.target === inputRef.current) return;

      attemptUpdate();
      // Turn off editing for this cell
      resetEditing();
    };
    document.body.addEventListener("click", onBodyClick);

    // Tear down global click listener when we're done
    return () => {
      document.body.removeEventListener("click", onBodyClick);
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

  let onClick:
    | ((e: ReactMouseEvent<HTMLTableCellElement>) => void)
    | undefined = undefined;
  // let dangerousContent: { __html: string } | undefined = undefined;
  let content: ReactElement | ReturnType<typeof flexRender> | undefined =
    undefined;
  const cellTitle = errorTitle;
  const tableCellClass =
    CellStateClassEnum[isEditing ? CellStateEnum.Editing : cellState];
  let attemptRenderAsync = false;

  let editContent: ReactElement | null = null;
  if (cellState === CellStateEnum.EditSaving) {
    // If saving, do not allow any clicks or edits
    content = <em>{editValue as string}</em>;
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
    } else {
      // `isEditing` is `false`

      // Only allow transition to edit mode if the cell can be edited
      if (editCellsIsAllowed) {
        onClick = (e: ReactMouseEvent<HTMLTableCellElement>) => {
          // Do not prevent default or stop propagation here!
          // Other methods need to be able to handle the event as well. e.g. `onBodyClick` above.
          // e.preventDefault();
          // e.stopPropagation();

          // Set this cell to editing mode
          setCellEditMapAtLoc(rowIndex, columnIndex, (obj_draft) => {
            obj_draft.isEditing = true;
            obj_draft.editValue = getCellValueText() as string;
          });
        };
      }
      if (isHtmlColumn) {
        // // console.log(rowIndex, columnIndex, isEditing, editValue);
        // // window.Shiny.renderContentAsync();
        // const dangerousScript = `<script>console.log(1, this, this.parent)</script>`;
        // // dangerousContent = { __html: dompurify.sanitize(cellValue as string) };
        // dangerousContent = { __html: dangerousScript };
        // attemptRenderAsync = true
      }
    }
    if (!isShinyHtmlFn(cellValue)) {
      content = flexRender(cell.column.columnDef.cell, cell.getContext());
    } else {
      attemptRenderAsync = true;
    }
  }

  // TODO-barret; when the tdRef is visible when we should display dangerous content, run html script to display the UI!
  useEffect(() => {
    // console.log("useEffect", rowIndex, columnIndex, isShinyHtml, content);
    if (!tdRef.current) return;
    if (!attemptRenderAsync) return;
    if (!isShinyHtmlFn(cellValue)) return;
    // if (isEditing) return;

    // if (!isHtmlColumn) return;
    // if (!isShinyHtmlFn(initialValue)) return;
    // // Safety hatch; Do not render if content is already set
    // if (content) return;

    // console.log(initialValue, rowIndex, columnIndex);
    // console.log("renderContentAsync", rowIndex, columnIndex, cellValue.obj);

    const cellValueObjDeepCopy = JSON.parse(JSON.stringify(cellValue.obj));

    window.Shiny.renderContentAsync(tdRef.current, cellValueObjDeepCopy);

    const curTdRef = tdRef.current;

    return () => {
      // console.log("renderContentAsync removed!", rowIndex, columnIndex);
      curTdRef.replaceChildren("");
    };
  }, [tdRef, cellValue, rowIndex, columnIndex, attemptRenderAsync]);

  // if (rowIndex === 1 && columnIndex === 1) {
  //   console.log("TableBodyCell", rowIndex, columnIndex, editContent, content);
  // }

  const ret = (
    <td
      // key={cell.id}
      ref={tdRef}
      onClick={onClick}
      title={cellTitle}
      className={tableCellClass}
      // dangerouslySetInnerHTML={dangerousContent}
    >
      {editContent}
      {content}
    </td>
  );

  return ret;
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

// const DangerouseContent: FC<{ fn: () => void }> = ({ fn }) => {
//   const dangerousRef = useRef<HTMLDivElement | null>(null);

//   useEffect(() => {
//     if (!dangerousRef.current) return;
//     fn(dangerousRef);

//     return () => {
//       console.log("Dangerous content removed!", dangerousRef.current);
//     };
//   }, [fn, dangerousRef]);

//   const ret = (
//     <div ref={dangerousRef}>
//       <p>Dangerous content!</p>
//     </div>
//   );

//   return ret;
// };
