import React, { FC, useEffect, useRef, useState } from "react";

export interface FilterNumericProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  // The absolute min/max possible values
  range: () => [number | undefined, number | undefined];

  // The currently selected min/max values
  from: number | undefined;
  to: number | undefined;

  onRangeChange: (from?: number, to?: number) => void;
}

export const FilterNumeric: FC<FilterNumericProps> = (props) => {
  const [editing, setEditing] = useState(false);
  const { range, from, to, onRangeChange } = props;

  return (
    <FilterNumericImpl
      range={range}
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
  range: () => [number | undefined, number | undefined];
  value: [number | undefined, number | undefined];
  editing: boolean;
  onValueChange: (range: [number | undefined, number | undefined]) => void;
  onFocus: () => void;
  onBlur: () => void;
}

const FilterNumericImpl: React.FC<FilterNumericImplProps> = (props) => {
  const [min, max] = props.value;
  const { editing, onFocus } = props;
  const [rangeMin, rangeMax] = props.range();

  const minInputRef = useRef<HTMLInputElement>(null);
  const maxInputRef = useRef<HTMLInputElement>(null);

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
        ref={minInputRef}
        className={`form-control form-control-sm ${
          minInputRef.current?.checkValidity() ? "" : "is-invalid"
        }`}
        style={{ flex: "1 1 0", width: "0" }}
        type="number"
        placeholder={createPlaceholder(editing, "Min", rangeMin)}
        defaultValue={min}
        // min={rangeMin}
        // max={rangeMax}
        step="any"
        onChange={(e) => {
          const value = coerceToNum(e.target.value);
          if (!minInputRef.current) return;
          minInputRef.current.classList.toggle(
            "is-invalid",
            !e.target.checkValidity()
          );
          props.onValueChange([value, max]);
        }}
      />
      <input
        ref={maxInputRef}
        className={`form-control form-control-sm ${
          maxInputRef.current?.checkValidity() ? "" : "is-invalid"
        }`}
        style={{ flex: "1 1 0", width: "0" }}
        type="number"
        placeholder={createPlaceholder(editing, "Max", rangeMax)}
        defaultValue={max}
        // min={rangeMin}
        // max={rangeMax}
        step="any"
        onChange={(e) => {
          const value = coerceToNum(e.target.value);
          if (!maxInputRef.current) return;
          maxInputRef.current.classList.toggle(
            "is-invalid",
            !e.target.checkValidity()
          );
          props.onValueChange([min, value]);
        }}
      />
    </div>
  );
};

function createPlaceholder(
  editing: boolean,
  label: string,
  value: number | undefined
) {
  if (!editing) {
    return undefined;
  } else if (typeof value === "undefined") {
    return label;
  } else {
    return `${label} (${value})`;
  }
}

function coerceToNum(value: string): number | undefined {
  if (value === "") {
    return undefined;
  }
  return +value;
}
