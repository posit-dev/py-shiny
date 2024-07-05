import { SortDirection } from "@tanstack/react-table";
import React, { FC } from "react";

const sortClassName = "sort-arrow";
const sortCommonProps = {
  viewBox: [-1, -1, 2, 2].map((x) => x * 1.4).join(" "),
  width: "100%",
  height: "100%",
  style: { paddingLeft: "3px" },
};

const sortPathCommonProps = {
  stroke: "#333333",
  strokeWidth: "0.6",
  fill: "transparent",
};

const sortArrowUp = (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    {...{ ...sortCommonProps, className: `${sortClassName} sort-arrow-up` }}
  >
    <path
      d="M -1 0.5 L 0 -0.5 L 1 0.5"
      {...sortPathCommonProps}
      strokeLinecap="round"
    />
  </svg>
);

const sortArrowDown = (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    {...{ ...sortCommonProps, className: `${sortClassName} sort-arrow-down` }}
  >
    <path
      d="M -1 -0.5 L 0 0.5 L 1 -0.5"
      {...sortPathCommonProps}
      strokeLinecap="round"
    />
  </svg>
);

interface SortArrowProps {
  direction: SortDirection | false;
}

export const SortArrow: FC<SortArrowProps> = ({ direction }) => {
  if (!direction) {
    return null;
  }
  if (direction === "asc") {
    return sortArrowUp;
  }
  if (direction === "desc") {
    return sortArrowDown;
  }
  throw new Error(`Unexpected sort direction: '${direction}'`);
};

//const sortArrowUp = <span className="sort-arrow sort-arrow-up"> ▲</span>;
//const sortArrowDown = <span className="sort-arrow sort-arrow-down"> ▼</span>;
