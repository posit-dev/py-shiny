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
export const CellStateMap = {
  EditSaving: "EditSaving",
  EditSuccess: "EditSuccess",
  EditFailure: "EditFailure",
  Editing: "Editing",
  Ready: "Ready",
} as const;
const CellStateClassMap = {
  EditSaving: "edit-waiting",
  EditSuccess: "edit-success",
  EditFailure: "edit-failure",
  Editing: "editing",
  Ready: "ready",
} as const;
export type CellState = keyof typeof CellStateMap;

interface TableBodyCellProps {
  id: string | null;
  cell: Cell<unknown[], unknown>;
  columns: readonly string[];
  canEdit: boolean;
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
  canEdit,
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

  const [cellState, setCellState] = useState<CellState>(CellStateMap.Ready);

  useEffect(() => {
    const cellIsEditable =
      editRowIndex === rowIndex && editColumnIndex === columnIndex;
    if (cellIsEditable) {
      setCellState(CellStateMap.Editing);
    }
  }, [editRowIndex, editColumnIndex, rowIndex, columnIndex]);

  const hasUpdated = cellEditMap.has(`[${rowIndex}, ${columnIndex}]`);

  const tableCellClass = CellStateClassMap[cellState];

  const [errorTitle, setErrorTitle] = useState<string | undefined>(undefined);

  const resetEditInfo = React.useCallback(() => {
    setEditRowIndex(null);
    setEditColumnIndex(null);
  }, [setEditRowIndex, setEditColumnIndex]);

  const onEsc = (e: ReactKeyboardEvent<HTMLInputElement>) => {
    if (e.key !== "Escape") return;
    // Prevent default behavior
    e.preventDefault();

    // inputRef.current.blur();
    resetEditInfo();
    // TODO-barret-future; Set focus to table? (state: Editing was aborted)
  };
  const onTab = (e: ReactKeyboardEvent<HTMLInputElement>) => {
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
  const onEnter = (e: ReactKeyboardEvent<HTMLInputElement>) => {
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
    [onEsc, onEnter, onTab].forEach((fn) => fn(e));
  };

  const attemptUpdate = () => {
    // Only update if the string form of the value has changed
    if (`${initialValue}` === `${value}`) return;

    setCellState(CellStateMap.EditSaving);
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
        setCellState(CellStateMap.EditSuccess);
      },
      onError: (err) => {
        console.error("Error saving tabel cell value!", err);
        setErrorTitle(String(err));
        setCellState(CellStateMap.EditFailure);
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
    if (cellState !== CellStateMap.Editing) return;
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
    window.document
      .querySelector("body")!
      .addEventListener("click", onBodyClick);

    // Tear down global click listener when we're done
    return () => {
      window.document
        .querySelector("body")!
        .removeEventListener("click", onBodyClick);
    };
  }, [cellState, resetEditInfo]);

  // Reselect the input when it comes into view!
  // (It could be scrolled out of view and then back into view)
  function onFocus(e: ReactFocusEvent<HTMLInputElement>) {
    if (cellState !== CellStateMap.Editing) {
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

  if (cellState === CellStateMap.EditSaving) {
    content = <em>{value as string}</em>;
  } else if (cellState === CellStateMap.Editing) {
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
    if (canEdit) {
      onClick = (e: ReactMouseEvent<HTMLTableCellElement>) => {
        setEditRowIndex(rowIndex);
        setEditColumnIndex(columnIndex);
        e.preventDefault();
        e.stopPropagation();
      };
    }
    if (cellState === CellStateMap.EditFailure) {
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
