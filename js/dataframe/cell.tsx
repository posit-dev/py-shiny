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
  editColumnId: string;
  setEditRowIndex: (index: number) => void;
  setEditColumnId: (id: string) => void;
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
  editColumnId,
  setEditRowIndex,
  setEditColumnId,
  cellEditMap,
  setData,
  setCellEditMap,
  maxRowSize,
}) => {
  const rowIndex = cell.row.index;
  const columnId = cell.column.id;
  // const backgroundColor = cellEditMap.has(`[${rowIndex}, ${columnId}]`)
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
  //   columnId: string;
  //   getValue: () => unknown;
  //   editRowIndex: number;
  //   editColumnId: string;
  //   cellEditMap: Map<string, { value: string; state: CellState }>;
  // }
  // return (
  //   <EditableCell
  //     rowIndex={rowIndex}
  //     columnId={columnId}
  //     getValue={getValue}
  //     editRowIndex={editRowIndex}
  //     editColumnId={editColumnId}
  //     cellEditMap={cellEditMap}
  //   ></EditableCell>
  // );

  // const EditableCell: FC<EditableCellProps> = (props) => {
  // const {
  //   rowIndex,
  //   columnId,
  //   getValue,
  //   editRowIndex,
  //   editColumnId,
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

  const editable = editRowIndex === rowIndex && editColumnId === columnId;
  if (editable) {
    setCellState(CellState.Editing);
  }
  const hasUpdated = cellEditMap.has(`[${rowIndex}, ${columnId}]`);
  if (editable) {
    if (hasUpdated) {
      console.log("Has updated!", rowIndex, columnId, cellEditMap);
    }
  }

  // useEffect(() => {
  //   if (editable) {
  //     console.log(
  //       "cell background color: ",
  //       cellBackground,
  //       rowIndex,
  //       columnId
  //     );
  //   }
  // }, [cellBackground, editable, rowIndex, columnId]);

  // useEffect(() => {

  //   setCellState(CellState.Ready);
  // }, [cellEditMap, rowIndex, columnId]);
  useEffect(() => {
    if (!editable) return;
    console.log(
      "Cell map:",
      rowIndex,
      columnId,
      cellEditMap,
      cellEditMap.has(`[${rowIndex}, ${columnId}]`)
    );
  }, [cellEditMap, rowIndex, editable, columnId]);

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

  useEffect(() => {
    console.log("Cell background:", tableCellClass, rowIndex, columnId);
  }, [tableCellClass, rowIndex, columnId]);
  useEffect(() => {
    console.log("Cell state:", cellState, hasUpdated);
  }, [hasUpdated, cellState]);

  function resetEditInfo() {
    setEditRowIndex(null);
    setEditColumnId(null);
  }

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

    const newColumnIndex = columns.indexOf(editColumnId) + (hasShift ? -1 : 1);
    if (newColumnIndex < 0 || newColumnIndex >= columns.length) {
      // If the new column index is out of bounds, quit
      return;
    }
    const newColumnId = columns[newColumnIndex];

    setEditColumnId(newColumnId);
  };
  const onEnter = (e: ReactKeyboardEvent<HTMLInputElement>) => {
    if (e.key !== "Enter") return;
    // Prevent default behavior
    e.preventDefault();

    const hasShift = e.shiftKey;

    const newRowIndex = editRowIndex + (hasShift ? -1 : 1);
    if (newRowIndex < 0 || newRowIndex >= maxRowSize) {
      // If the new row index is out of bounds, quit
      return;
    }

    setEditRowIndex(newRowIndex);
  };

  const onInputKeyDown = (e: ReactKeyboardEvent<HTMLInputElement>) => {
    [onEsc, onEnter, onTab].forEach((fn) => fn(e));
  };

  // When the input is blurred, we'll call our table meta's updateData function
  // console.log("rendering cell", rowIndex, id, initialValue, value);
  const onBlur = () => {
    // console.log("on blur!", initialValue, value, e);
    // Only update if the string form of the value has changed
    if (`${initialValue}` !== `${value}`) {
      setCellState(CellState.EditSaving);
      // console.log("Setting update count");
      // setUpdateCount(updateCount + 1);
      updateCellsData({
        id,
        cellInfos: [
          {
            rowIndex,
            columnId,
            value,
            prev: initialValue,
          },
        ],
        onSuccess: (values) => {
          console.log("success!", values);
          setCellState(CellState.EditSuccess);
        },
        onError: (err) => {
          console.log("error!", err);
          setCellState(CellState.EditFailure);
        },
        columns,
        setData,
        setCellEditMap,
      });
    }
  };

  // If the initialValue is changed external, sync it up with our state
  useEffect(() => {
    setValue(initialValue);
  }, [initialValue, setValue]);

  // Select the input when it becomes editable
  useEffect(() => {
    if (editable) {
      inputRef.current.focus();
      inputRef.current.select();

      // Setup global click listener to reset edit info
      window.document
        .querySelector("body")
        .addEventListener("click", (e: MouseEvent) => {
          // console.log("body click!", e.target, inputRef.current);
          // TODO-barret; Do not reset if target is another table cell!
          // Or skip the reset?
          resetEditInfo();
        });

      // Tear down global click listener when we're done
      return () => {
        window.document
          .querySelector("body")
          .removeEventListener("click", resetEditInfo);
      };
    }
  }, [editable]);

  // Reselect the input when it comes into view!
  // (It could be scrolled out of view and then back into view)
  function onFocus(e: ReactFocusEvent<HTMLInputElement>) {
    if (editable) {
      e.target.select();
    }
  }

  function onChange(e: ReactChangeEvent<HTMLInputElement>) {
    console.log("on change!");
    setValue(e.target.value);
  }

  let onClick = undefined;
  let content = undefined;

  if (cellState === CellState.EditSaving) {
    content = <em>Saving...</em>;
  } else if (editable) {
    content = (
      <input
        value={value as string}
        onChange={onChange}
        onBlur={onBlur}
        onFocus={onFocus}
        onKeyDown={onInputKeyDown}
        ref={inputRef}
      />
    );
  } else {
    onClick = (e: ReactMouseEvent<HTMLTableCellElement>) => {
      console.log("on ready click!", e.target);
      setEditRowIndex(rowIndex);
      setEditColumnId(columnId);
    };
    if (cellState === CellState.EditFailure) {
      console.log("Render edit failure");
    }
    content = flexRender(cell.column.columnDef.cell, cell.getContext());
  }

  return (
    <td key={cell.id} onClick={onClick} className={tableCellClass}>
      {content}
    </td>
  );
};
