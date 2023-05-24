import React from "react";

const sortCommonProps = {
  className: "sort-arrow",
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

export const sortArrowUp = (
  <svg xmlns="http://www.w3.org/2000/svg" {...sortCommonProps}>
    <path
      d="M -1 0.5 L 0 -0.5 L 1 0.5"
      {...sortPathCommonProps}
      strokeLinecap="round"
    />
  </svg>
);

export const sortArrowDown = (
  <svg xmlns="http://www.w3.org/2000/svg" {...sortCommonProps}>
    <path
      d="M -1 -0.5 L 0 0.5 L 1 -0.5"
      {...sortPathCommonProps}
      strokeLinecap="round"
    />
  </svg>
);

//const sortArrowUp = <span className="sort-arrow sort-arrow-up"> ▲</span>;
//const sortArrowDown = <span className="sort-arrow sort-arrow-down"> ▼</span>;
