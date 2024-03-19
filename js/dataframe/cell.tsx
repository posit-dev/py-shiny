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
import { CellEditMap, SetCellEditMap } from "./cell-edit-map";
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
  Editing: "cell-editing",
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

  const inputRef = useRef<HTMLInputElement | null>(null);
  const [cellState, setCellState] = useState<CellState>(CellStateEnum.Ready);

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

  const handleEsc = (e: ReactKeyboardEvent<HTMLInputElement>) => {
    if (e.key !== "Escape") return;
    // Prevent default behavior
    e.preventDefault();

    // inputRef.current.blur();
    attemptUpdate();
    resetEditInfo();
    // TODO-barret-future; Set focus to table? (state: Editing was aborted)
  };
  const handleTab = (e: ReactKeyboardEvent<HTMLInputElement>) => {
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
  const handleEnter = (e: ReactKeyboardEvent<HTMLInputElement>) => {
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

  const onInputKeyDown = (e: ReactKeyboardEvent<HTMLInputElement>) => {
    [handleEsc, handleEnter, handleTab].forEach((fn) => fn(e));
  };

  const attemptUpdate = useCallback(() => {
    console.log("attemptUpdate", rowIndex, columnIndex, value, initialValue);

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

    // Setup global click listener to reset edit info
    const onBodyClick = (e: MouseEvent) => {
      if (e.target === inputRef.current) {
        return;
      }
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
  function onFocus(e: ReactFocusEvent<HTMLInputElement>) {
    console.log("focus cellState: ", cellState, rowIndex, columnIndex);
    if (cellState === CellStateEnum.Editing) {
      // TODO-barret; Restore cursor position and selection
      e.target.select();
    }
  }

  function onChange(e: ReactChangeEvent<HTMLInputElement>) {
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
      <input
        className="cell-edit-input"
        value={value as string}
        onChange={onChange}
        // onBlur={onBlur}
        onFocus={onFocus}
        onKeyDown={onInputKeyDown}
        ref={inputRef}
      />
    );
  } else {
    // Only allow transition to edit mode if the cell can be edited
    if (editCellsIsAllowed) {
      onClick = (e: ReactMouseEvent<HTMLTableCellElement>) => {
        setEditRowIndex(rowIndex);
        setEditColumnIndex(columnIndex);
        e.preventDefault();
        e.stopPropagation();
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
    >
      {content}
    </td>
  );
};
