import { flexRender } from "@tanstack/react-table";
import { VirtualItem } from "@tanstack/react-virtual";
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
  useState,
} from "react";
import { useImmer } from "use-immer";
import {
  CellEditMap,
  SetCellEditMap,
  getCellEditMapValue,
} from "./cell-edit-map";
import { updateCellsData } from "./data-update";

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

interface TableBodyCellProps {
  id: string | null;
  cell: Cell<unknown[], unknown>;
  columns: readonly string[];
  editCellsIsAllowed: boolean;
  editRowIndex: number | null;
  editColumnIndex: number | null;
  virtualRows: VirtualItem[];
  setEditRowIndex: (index: number | null) => void;
  setEditColumnIndex: (index: number | null) => void;
  setData: (fn: (draft: unknown[][]) => void) => void;
  cellEditMap: CellEditMap;
  setCellEditMap: SetCellEditMap;
  maxRowSize: number;
}

export const TableBodyCell: FC<TableBodyCellProps> = ({
  id,
  cell,
  columns,
  editCellsIsAllowed,
  editRowIndex,
  editColumnIndex,
  virtualRows,
  setEditRowIndex,
  setEditColumnIndex,
  cellEditMap,
  setData,
  setCellEditMap,
  maxRowSize,
}) => {
  const rowIndex = cell.row.index;
  const columnIndex = cell.column.columnDef.meta!.colIndex;

  const initialValue = cell.getValue();
  // We need to keep and update the state of the cell normally
  const [value, setValue] = useImmer(initialValue);
  // If the initialValue (defined by `cell.getValue()`) is changed externally
  // (e.g. copy/**paste**), sync it up with our state
  // (This method only runs if `initialValue` has changed)
  useEffect(() => setValue(initialValue), [initialValue, setValue]);

  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const [cellState, setCellState] = useState<CellState>(
    getCellEditMapValue(cellEditMap, rowIndex, columnIndex)?.state ||
      CellStateEnum.Ready
  );

  const [errorTitle, setErrorTitle] = useState<string | undefined>(undefined);

  const setValueStateError = useCallback(
    ({
      newValue,
      newCellState,
      newErrorTitle,
    }: {
      newValue: typeof value;
      newCellState: typeof cellState;
      newErrorTitle: typeof errorTitle;
    }) => {
      setValue(newValue);
      setCellState(newCellState);
      setErrorTitle(newErrorTitle);
    },
    [setValue, setCellState, setErrorTitle]
  );

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
  // * In row / column selection mode, allow for arrowoutput_binding_request_handler key navigation by focusing on a single cell, not a TR
  // * If a cell is focused,
  //   * `enter key` allows you to go into edit mode; If editing is turned off, the selection is toggled
  //   * `space key` allows you toggle the selection of the cell
  // * Arrow key navigation is required

  useEffect(() => {
    const cellIsEditable =
      editRowIndex === rowIndex && editColumnIndex === columnIndex;
    // If the cell is editable, set the cell state to editing
    if (cellIsEditable) {
      setCellState(CellStateEnum.Editing);
    } else {
      // Update cell state when a cell edit has been created
      const editInfo = getCellEditMapValue(cellEditMap, rowIndex, columnIndex);
      if (editInfo) {
        setValueStateError({
          newValue: editInfo.value,
          newCellState: editInfo.state,
          newErrorTitle: editInfo.save_error,
        });
      }
    }
  }, [
    editRowIndex,
    editColumnIndex,
    rowIndex,
    columnIndex,
    cellEditMap,
    setValueStateError,
  ]);

  const resetEditInfo = useCallback(() => {
    setEditRowIndex(null);
    setEditColumnIndex(null);
  }, [setEditColumnIndex, setEditRowIndex]);

  const handleEsc = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== "Escape") return;
    // Prevent default behavior
    e.preventDefault();

    // Try to restore the previous value, state, and error
    // If there is no previous state info, reset the cell to the inital value
    const stateInfo = getCellEditMapValue(cellEditMap, rowIndex, columnIndex);

    if (stateInfo) {
      // Restore the previous value, state, and error
      setValueStateError({
        newValue: stateInfo.value,
        newCellState: stateInfo.state,
        newErrorTitle: stateInfo.save_error,
      });
    } else {
      // Reset to the initial value
      setValueStateError({
        newValue: initialValue,
        newCellState: CellStateEnum.Ready,
        newErrorTitle: undefined,
      });
    }
    // Remove editing info
    resetEditInfo();
  };
  const handleTab = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== "Tab") return;
    // Prevent default behavior
    e.preventDefault();

    const hasShift = e.shiftKey;

    const newColumnIndex = editColumnIndex! + (hasShift ? -1 : 1);
    if (newColumnIndex < 0 || newColumnIndex >= columns.length) {
      // If the new column index is out of bounds, quit
      return;
    }

    attemptUpdate();
    setEditColumnIndex(newColumnIndex);
  };
  // TODO future: Make Cmd-Enter add a newline in a cell.
  const handleEnter = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== "Enter") return;
    // Prevent default behavior
    e.preventDefault();

    const hasShift = e.shiftKey;

    const newRowIndex = editRowIndex! + (hasShift ? -1 : 1);
    if (newRowIndex < 0 || newRowIndex >= maxRowSize) {
      // If the new row index is out of bounds, quit
      return;
    }

    attemptUpdate();
    setEditRowIndex(newRowIndex);
  };

  const onInputKeyDown = (e: ReactKeyboardEvent<HTMLTextAreaElement>) => {
    [handleEsc, handleEnter, handleTab].forEach((fn) => fn(e));
  };

  const attemptUpdate = useCallback(() => {
    setErrorTitle(undefined);

    // Only update if the string form of the value has changed
    if (`${initialValue}` === `${value}`) {
      setCellState(CellStateEnum.Ready);
      return;
    }

    setCellState(CellStateEnum.EditSaving);
    // Update the data!
    // updateCellsData updates the underlying data via `setData` and `setCellEditMap`
    updateCellsData({
      id,
      patches: [
        {
          rowIndex,
          columnIndex,
          value,
          // prev: initialValue,
        },
      ],
      onSuccess: (_patches) => {
        // console.log("Success!!");
      },
      onError: (err) => {
        // console.log("Error!!", err);
      },
      columns,
      setData,
      setCellEditMap,
    });
  }, [
    id,
    rowIndex,
    columnIndex,
    value,
    initialValue,
    columns,
    setData,
    setCellEditMap,
  ]);

  // Select the input when it becomes editable
  useEffect(() => {
    if (cellState !== CellStateEnum.Editing) return;
    if (!inputRef.current) return;

    inputRef.current.focus();
    inputRef.current.select();
  }, [cellState]);

  // When editing a cell, set up a global click listener to reset edit info when
  // clicking outside of the cell
  useEffect(() => {
    if (cellState !== CellStateEnum.Editing) return;
    if (!inputRef.current) return;

    // TODO-barret; Restore cursor position and text selection here

    // Set up global click listener to reset edit info
    const onBodyClick = (e: MouseEvent) => {
      if (e.target === inputRef.current) return;

      attemptUpdate();
      resetEditInfo();
    };
    document.body.addEventListener("click", onBodyClick);

    // Tear down global click listener when we're done
    return () => {
      document.body.removeEventListener("click", onBodyClick);
    };
  }, [cellState, attemptUpdate, resetEditInfo, value]);

  // Reselect the input when it comes into view!
  // (It could be scrolled out of view and then back into view)
  function onFocus(e: ReactFocusEvent<HTMLTextAreaElement>) {
    if (cellState === CellStateEnum.Editing) {
      e.target.select();
    }
  }

  function onChange(e: ReactChangeEvent<HTMLTextAreaElement>) {
    // Upddate value temporarily (do not save to cell edit map)
    setValue(e.target.value);
  }

  // https://medium.com/@oherterich/creating-a-textarea-with-dynamic-height-using-react-and-typescript-5ed2d78d9848
  // Updates the height of a <textarea> when the value changes.
  const useAutosizeTextArea = (
    textAreaRef: HTMLTextAreaElement | null,
    value: string
  ) => {
    useEffect(() => {
      if (textAreaRef) {
        // We need to reset the height momentarily to get the correct scrollHeight for the textarea
        textAreaRef.style.height = "0px";
        const scrollHeight = textAreaRef.scrollHeight;

        // We then set the height directly, outside of the render loop
        // Trying to set this with state or a ref will product an incorrect value.
        textAreaRef.style.height = scrollHeight + "px";
      }
    }, [textAreaRef, value]);
  };
  useAutosizeTextArea(inputRef.current, value as string);

  let onClick:
    | ((e: ReactMouseEvent<HTMLTableCellElement>) => void)
    | undefined = undefined;
  let content: ReactElement | ReturnType<typeof flexRender> | undefined =
    undefined;
  let cellTitle = errorTitle;
  const tableCellClass = CellStateClassEnum[cellState];
  // let cellContentEditable: boolean = false;

  if (cellState === CellStateEnum.EditSaving) {
    content = <em>{value as string}</em>;
  } else if (cellState === CellStateEnum.Editing) {
    content = (
      <textarea
        value={value as string}
        onChange={onChange}
        // onBlur={onBlur}
        onFocus={onFocus}
        onKeyDown={onInputKeyDown}
        ref={inputRef}
        style={{ width: "100%", height: "100%" }}
      />
    );
  } else {
    // Only allow transition to edit mode if the cell can be edited
    if (editCellsIsAllowed) {
      onClick = (e: ReactMouseEvent<HTMLTableCellElement>) => {
        setEditRowIndex(rowIndex);
        setEditColumnIndex(columnIndex);
        // Do not prevent default or stop propagation here!
        // Other methods need to be able to handle the event as well. e.g. `onBodyClick` above.
        // e.preventDefault();
        // e.stopPropagation();
      };
    }
    if (cellState === CellStateEnum.EditFailure) {
      cellTitle = errorTitle;
    }
    content = flexRender(cell.column.columnDef.cell, cell.getContext());
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
  }

  return (
    <td
      key={cell.id}
      onClick={onClick}
      title={cellTitle}
      className={tableCellClass}
    >
      {content}
    </td>
  );
};
