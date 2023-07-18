import React, { FC, useEffect, useRef, useState } from "react";

export interface FilterNumericProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  // The absolute min/max possible values
  min: number;
  max: number;

  // The currently selected min/max values
  from: number | undefined;
  to: number | undefined;

  onRangeChange: (from?: number, to?: number) => void;
}

export const FilterNumeric: FC<FilterNumericProps> = (props) => {
  const [editing, setEditing] = useState(false);
  const { min, max, from, to, onRangeChange } = props;

  return (
    <FilterNumericImpl
      range={[min, max]}
      value={[from, to]}
      editing={editing}
      onValueChange={(x) => onRangeChange(...x)}
      onFocus={() => setEditing(true)}
      onBlur={() => setEditing(false)}
    />
  );
};

function generateLabel(from?: number, to?: number) {
  if (typeof from === "undefined" && typeof to === "undefined") {
    return "";
  } else if (typeof from === "undefined") {
    return `≤ ${to}`;
  } else if (typeof to === "undefined") {
    return `≥ ${from}`;
  } else {
    return `≥${from}, ≤${to}`;
  }
}

interface FilterNumericImplProps {
  range: [number, number];
  value: [number | undefined, number | undefined];
  editing: boolean;
  onValueChange: (range: [number | undefined, number | undefined]) => void;
  onFocus: () => void;
  onBlur: () => void;
}

const FilterNumericImpl: React.FC<FilterNumericImplProps> = (props) => {
  const [min, max] = props.value;
  const { editing, onFocus } = props;

  return (
    <div
      onBlur={(e) => {
        if (e.currentTarget.contains(e.relatedTarget)) {
          return;
        }
        return props.onBlur();
      }}
      onFocus={() => onFocus()}
      style={{
        display: "flex",
        gap: "0.5rem",
      }}
    >
      <input
        className="form-control form-control-sm"
        style={{ flex: "1 1 0", width: "0" }}
        type="number"
        placeholder={editing ? `Min (${props.range[0]})` : null}
        value={min}
        onChange={(e) =>
          props.onValueChange([coerceToNum(e.target.value), max])
        }
      />
      <input
        className="form-control form-control-sm"
        style={{ flex: "1 1 0", width: "0" }}
        type="number"
        placeholder={editing ? `Max (${props.range[1]})` : null}
        value={max}
        onChange={(e) =>
          props.onValueChange([min, coerceToNum(e.target.value)])
        }
      />
    </div>
  );
};

function coerceToNum(value: string): number | undefined {
  if (value === "") {
    return undefined;
  }
  return +value;
}
