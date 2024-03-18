import { flexRender } from "@tanstack/react-table";
import { Cell } from "@tanstack/table-core";
import React, {
  FC,
  ChangeEvent as ReactChangeEvent,
  ReactElement,
  FocusEvent as ReactFocusEvent,
  KeyboardEvent as ReactKeyboardEvent,
  MouseEvent as ReactMouseEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import { useImmer } from "use-immer";
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
  setEditRowIndex: (index: number | null) => void;
  setEditColumnIndex: (index: number | null) => void;
  cellEditMap: Map<string, { value: string; state: CellState }>;
  setData: (fn: (draft: unknown[][]) => void) => void;
  setCellEditMap: (
    fn: (draft: Map<string, { value: string; state: CellState }>) => void
  ) => void;
  maxRowSize: number;
}

export const TableBodyCell: FC<TableBodyCellProps> = ({
  id,
  cell,
  columns,
  editCellsIsAllowed,
  editRowIndex,
  editColumnIndex,
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
  const inputRef = useRef<HTMLInputElement | null>(null);

  const [cellState, setCellState] = useState<CellState>(CellStateEnum.Ready);

  useEffect(() => {
    const cellIsEditable =
      editRowIndex === rowIndex && editColumnIndex === columnIndex;
    if (cellIsEditable) {
      setCellState(CellStateEnum.Editing);
    }
  }, [editRowIndex, editColumnIndex, rowIndex, columnIndex]);

  const hasUpdated = cellEditMap.has(`[${rowIndex}, ${columnIndex}]`);

  const tableCellClass = CellStateClassEnum[cellState];

  const [errorTitle, setErrorTitle] = useState<string | undefined>(undefined);

  const resetEditInfo = () => {
    setEditRowIndex(null);
    setEditColumnIndex(null);
  };

  const handleEsc = (e: ReactKeyboardEvent<HTMLInputElement>) => {
    if (e.key !== "Escape") return;
    // Prevent default behavior
    e.preventDefault();

    // inputRef.current.blur();
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
      // attemptUpdate();
      return;
    }

    setEditRowIndex(newRowIndex);
  };

  const onInputKeyDown = (e: ReactKeyboardEvent<HTMLInputElement>) => {
    [handleEsc, handleEnter, handleTab].forEach((fn) => fn(e));
  };

  const attemptUpdate = () => {
    // Only update if the string form of the value has changed
    if (`${initialValue}` === `${value}`) return;

    setCellState(CellStateEnum.EditSaving);
    // console.log("Setting update count");
    // setUpdateCount(updateCount + 1);
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
      onSuccess: (values) => {
        // console.log("success!", values);
        setCellState(CellStateEnum.EditSuccess);
      },
      onError: (err) => {
        console.error("Error saving tabel cell value!", err);
        setErrorTitle(String(err));
        setCellState(CellStateEnum.EditFailure);
      },
      columns,
      setData,
      setCellEditMap,
    });
  };

  // When the input is blurred, we'll call our table meta's updateData function
  // console.log("rendering cell", rowIndex, id, initialValue, value);
  const onBlur = () => {
    // console.log("on blur!", initialValue, value, e);
    attemptUpdate();
  };

  // If the initialValue is changed external, sync it up with our state
  useEffect(() => {
    setValue(initialValue);
  }, [initialValue, setValue]);

  // Select the input when it becomes editable
  useEffect(() => {
    if (cellState !== CellStateEnum.Editing) return;
    if (!inputRef.current) return;

    inputRef.current.focus();
    inputRef.current.select();

    // Setup global click listener to reset edit info
    const onBodyClick = (e: MouseEvent) => {
      if (e.target === inputRef.current) {
        return;
      }
      resetEditInfo();
    };
    document.body.addEventListener("click", onBodyClick);

    // Tear down global click listener when we're done
    return () => {
      document.body.removeEventListener("click", onBodyClick);
    };
  }, [cellState, resetEditInfo]);

  // Reselect the input when it comes into view!
  // (It could be scrolled out of view and then back into view)
  function onFocus(e: ReactFocusEvent<HTMLInputElement>) {
    if (cellState !== CellStateEnum.Editing) {
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

  if (cellState === CellStateEnum.EditSaving) {
    content = <em>{value as string}</em>;
  } else if (cellState === CellStateEnum.Editing) {
    content = (
      <input
        className="cell-edit-input"
        value={value as string}
        onChange={onChange}
        onBlur={onBlur}
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
