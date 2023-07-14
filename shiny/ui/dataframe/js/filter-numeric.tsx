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

  if (!editing) {
    return (
      <input
        className={`form-control form-control-sm`}
        readOnly={true}
        type="text"
        value={generateLabel(from, to)}
        onFocus={(e) => {
          setEditing(true);
        }}
      />
    );
  } else {
    return (
      <FilterNumericImpl
        range={[min, max]}
        value={[from, to]}
        onValueChange={(x) => onRangeChange(...x)}
        onBlur={() => setEditing(false)}
      />
    );
  }
};

function generateLabel(from?: number, to?: number) {
  if (typeof from === "undefined" && typeof to === "undefined") {
    return "";
  } else if (typeof from === "undefined") {
    return `≤ ${to}`;
  } else if (typeof to === "undefined") {
    return `≥ ${from}`;
  } else {
    return `[${from}, ${to}]`;
  }
}

interface FilterNumericImplProps {
  range: [number, number];
  value: [number | undefined, number | undefined];
  onValueChange: (range: [number | undefined, number | undefined]) => void;
  onBlur: () => void;
}

const FilterNumericImpl: React.FC<FilterNumericImplProps> = (props) => {
  const ref = useRef<HTMLInputElement>();
  useEffect(() => {
    ref.current.focus();
    ref.current.select();
  }, []);

  const [min, max] = props.value;

  return (
    <div
      onBlur={(e) => {
        if (e.currentTarget.contains(e.relatedTarget)) {
          return;
        }
        return props.onBlur();
      }}
      style={{
        display: "flex",
        gap: "0.5rem",
      }}
    >
      <input
        className={`form-control form-control-sm`}
        style={{ flex: "1 1 0", width: "0" }}
        type="number"
        placeholder={`Min (${props.range[0]})`}
        value={min}
        onChange={(e) =>
          props.onValueChange([coerceToNum(e.target.value), max])
        }
        ref={ref}
      />
      <input
        className={`form-control form-control-sm`}
        style={{ flex: "1 1 0", width: "0" }}
        type="number"
        placeholder={`Max (${props.range[1]})`}
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
