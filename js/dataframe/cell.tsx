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
  const [cellState, setCellState] = useState<CellState>(CellStateEnum.Ready);

  // Keyboard navigation:
  // * When editing a cell:
  //   * On esc key:
  //     * √ Restore prior value / state / error
  //     * Move focus from input to td
  //   * On enter key:
  //     * √ Save value
  //     * √ Move to the cell below (or above w/ shift) and edit the new cell
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

  useEffect(() => {
    const cellIsEditable =
      editRowIndex === rowIndex && editColumnIndex === columnIndex;
    if (cellIsEditable) {
      setCellState(CellStateEnum.Editing);
    }
  }, [editRowIndex, editColumnIndex, rowIndex, columnIndex]);

  const [errorTitle, setErrorTitle] = useState<string | undefined>(undefined);

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
      setValue(initialValue);
      setCellState(stateInfo.state);
      setErrorTitle(stateInfo.save_error);
    } else {
      setValue(initialValue);
      setCellState(CellStateEnum.Ready);
      setErrorTitle(undefined);
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
      cellInfos: [
        {
          rowIndex,
          columnIndex,
          value,
          prev: initialValue,
        },
      ],
      onSuccess: (_values) => {
        // Update cell state
        setCellState(CellStateEnum.EditSuccess);
      },
      onError: (err) => {
        // Update error info
        setErrorTitle(String(err));
        setCellState(CellStateEnum.EditFailure);
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

  // // When the input is blurred, we'll call our table meta's updateData function
  // // console.log("rendering cell", rowIndex, id, initialValue, value);
  // const onBlur = () => {
  //   // console.log("on blur!", initialValue, value, e);
  //   attemptUpdate();
  // };

  // Select the input when it becomes editable
  useEffect(() => {
    if (cellState !== CellStateEnum.Editing) return;
    if (!inputRef.current) return;

    inputRef.current.focus();
    inputRef.current.select();
  }, [cellState]);

  useEffect(() => {
    if (cellState !== CellStateEnum.Editing) return;
    if (!inputRef.current) return;

    // TODO-barret; Restore cursor position and text selection here

    // Setup global click listener to reset edit info
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
    console.log("focus cellState: ", cellState, rowIndex, columnIndex);
    if (cellState === CellStateEnum.Editing) {
      e.target.select();
    }
  }

  function onChange(e: ReactChangeEvent<HTMLTextAreaElement>) {
    // console.log("on change!");
    setValue(e.target.value);
  }

  let onClick:
    | ((e: ReactMouseEvent<HTMLTableCellElement>) => void)
    | undefined = undefined;
  let content: ReactElement | ReturnType<typeof flexRender> | undefined =
    undefined;
  let cellTitle = errorTitle;
  const tableCellClass = CellStateClassEnum[cellState];

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
  }

  return (
    <td
      key={cell.id}
      onClick={onClick}
      title={cellTitle}
      className={tableCellClass}
      // contentEditable={cellContentEditable}
    >
      {content}
    </td>
  );
};
