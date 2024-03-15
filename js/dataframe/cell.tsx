import { flexRender } from "@tanstack/react-table";
import { Cell } from "@tanstack/table-core";
import React, {
  FC,
  ChangeEvent as ReactChangeEvent,
  FocusEvent as ReactFocusEvent,
  KeyboardEvent as ReactKeyboardEvent,
  MouseEvent as ReactMouseEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import { useImmer } from "use-immer";
import { updateCellsData } from "./data-update";

export enum CellState {
  EditSaving = "edit-waiting",
  EditSuccess = "edit-success",
  EditFailure = "edit-failure",
  Editing = "editing",
  Ready = "ready",
}

interface TableBodyCellProps {
  id: string;
  cell: Cell<unknown[], unknown>;
  columns: readonly string[];
  canEdit: boolean;
  editRowIndex: number;
  editColumnIndex: number;
  setEditRowIndex: (index: number) => void;
  setEditColumnIndex: (index: number) => void;
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
  const columnIndex = cell.column.columnDef.meta.colIndex;
  // const backgroundColor = cellEditMap.has(`[${rowIndex}, ${columnIndex}]`)
  //   ? "red"
  //   : null;

  // return (
  //   <td key={cell.id} style={{ backgroundColor }}>
  //     {flexRender(cell.column.columnDef.cell, cell.getContext())}
  //   </td>
  // );
  // };

  // interface EditableCellProps {
  //   rowIndex: number;
  //   columnIndex: string;
  //   getValue: () => unknown;
  //   editRowIndex: number;
  //   editColumnIndex: string;
  //   cellEditMap: Map<string, { value: string; state: CellState }>;
  // }
  // return (
  //   <EditableCell
  //     rowIndex={rowIndex}
  //     columnIndex={columnIndex}
  //     getValue={getValue}
  //     editRowIndex={editRowIndex}
  //     editColumnIndex={editColumnIndex}
  //     cellEditMap={cellEditMap}
  //   ></EditableCell>
  // );

  // const EditableCell: FC<EditableCellProps> = (props) => {
  // const {
  //   rowIndex,
  //   columnIndex,
  //   getValue,
  //   editRowIndex,
  //   editColumnIndex,
  //   cellEditMap,
  // } = props;

  // States
  // # Ready
  // # Editing
  // # Saving / Disabled
  // # Error
  // # Saved
  // # Cancelled (is Ready state?)
  // # New
  // # Added
  // # Removed
  const initialValue = cell.getValue();
  // We need to keep and update the state of the cell normally
  const [value, setValue] = useImmer(initialValue);
  const inputRef = useRef(null);

  const [cellState, setCellState] = useState<CellState>(CellState.Ready);

  const [editable, setEditable] = useState(false);
  useEffect(() => {
    const cellIsEditable =
      editRowIndex === rowIndex && editColumnIndex === columnIndex;
    setEditable(cellIsEditable);
  }, [editRowIndex, editColumnIndex, rowIndex, columnIndex]);

  // const editable = editRowIndex === rowIndex && editColumnIndex === columnIndex;
  if (editable) {
    setCellState(CellState.Editing);
  }
  const hasUpdated = cellEditMap.has(`[${rowIndex}, ${columnIndex}]`);
  // if (editable) {
  //   if (hasUpdated) {
  //     console.log("Has updated!", rowIndex, columnIndex, cellEditMap);
  //   }
  // }

  // useEffect(() => {
  //   if (editable) {
  //     console.log(
  //       "cell background color: ",
  //       cellBackground,
  //       rowIndex,
  //       columnIndex
  //     );
  //   }
  // }, [cellBackground, editable, rowIndex, columnIndex]);

  // useEffect(() => {

  //   setCellState(CellState.Ready);
  // }, [cellEditMap, rowIndex, columnIndex]);
  // useEffect(() => {
  //   if (!editable) return;
  //   console.log(
  //     "Cell map:",
  //     rowIndex,
  //     columnIndex,
  //     cellEditMap,
  //     cellEditMap.has(`[${rowIndex}, ${columnIndex}]`)
  //   );
  // }, [cellEditMap, rowIndex, editable, columnIndex]);

  // useEffect(() => {
  //   if (editable) {
  //     setCellBackground("red");
  //     return;
  //   }
  //   // if (!hasUpdated) {
  //   //   setCellBackground("transparent");
  //   //   return;
  //   // }
  //   switch (cellState) {
  //     case CellState.EditSaving:
  //       setCellBackground("lightgrey");
  //       break;
  //     case CellState.EditSuccess:
  //       setCellBackground("#ddffdd");
  //       break;
  //     case CellState.EditFailure:
  //       setCellBackground("lightcoral");
  //       break;
  //     case CellState.Editing:
  //       setCellBackground("lightblue");
  //       break;
  //     default:
  //       setCellBackground("transparent");
  //   }
  // }, [cellState, editable, hasUpdated]);

  type TableCellClassMap = {
    [key in CellState]: string;
  };
  const tableCellClassMap_: Record<string, string | null> = {};
  tableCellClassMap_[CellState.Ready] = null;
  tableCellClassMap_[CellState.Editing] = "cell-edit-editing";
  tableCellClassMap_[CellState.EditSaving] = "cell-edit-saving";
  tableCellClassMap_[CellState.EditSuccess] = "cell-edit-success";
  tableCellClassMap_[CellState.EditFailure] = "cell-edit-failure";
  const tableCellMap: TableCellClassMap =
    tableCellClassMap_ as TableCellClassMap;

  const tableCellClass = tableCellMap[cellState];

  const [errorTitle, setErrorTitle] = useState<string | null>(undefined);

  // useEffect(() => {
  //   console.log("Cell background:", tableCellClass, rowIndex, columnIndex);
  // }, [tableCellClass, rowIndex, columnIndex]);
  // useEffect(() => {
  //   console.log("Cell state:", cellState, hasUpdated);
  // }, [hasUpdated, cellState]);

  // function resetEditInfo() {
  //   console.log("Resetting edit info!", rowIndex, columnIndex);
  //   setEditRowIndex(null);
  //   setEditColumnIndex(null);
  // }
  const resetEditInfo = React.useCallback(() => {
    setEditRowIndex(null);
    setEditColumnIndex(null);
  }, [editRowIndex, editColumnIndex]);

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

    const newColumnIndex = editColumnIndex + (hasShift ? -1 : 1);
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

    const newRowIndex = editRowIndex + (hasShift ? -1 : 1);
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

    setCellState(CellState.EditSaving);
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
        setCellState(CellState.EditSuccess);
      },
      onError: (err) => {
        console.error("Error saving tabel cell value!", err);
        setErrorTitle(String(err));
        setCellState(CellState.EditFailure);
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
    if (!editable) return;

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
      .querySelector("body")
      .addEventListener("click", onBodyClick);

    // Tear down global click listener when we're done
    return () => {
      window.document
        .querySelector("body")
        .removeEventListener("click", onBodyClick);
    };
  }, [editable]);

  // Reselect the input when it comes into view!
  // (It could be scrolled out of view and then back into view)
  function onFocus(e: ReactFocusEvent<HTMLInputElement>) {
    if (editable) {
      e.target.select();
    }
  }

  function onChange(e: ReactChangeEvent<HTMLInputElement>) {
    // console.log("on change!");
    setValue(e.target.value);
  }

  let onClick = undefined;
  let content = undefined;
  let cellTitle = errorTitle;

  if (cellState === CellState.EditSaving) {
    content = <em>{value as string}</em>;
  } else if (editable) {
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
    if (cellState === CellState.EditFailure) {
      // TODO-barret; Handle edit failure?
      // console.log("Render edit failure");
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
