import { SketchPicker } from "react-color";
import React from "react";

import { makeReactInput, makeReactOutput } from "@shiny-helpers/react";

// Generates a new input binding that renders the supplied react component
// into the root of the webcomponent.
makeReactInput({
  tagName: "custom-component-input",
  initialValue: "#fff",
  renderComp: ({ initialValue, onNewValue }) => (
    <ColorPickerReact
      initialValue={initialValue}
      onNewValue={(color) => onNewValue(color)}
    />
  ),
});

// Color Picker React component
function ColorPickerReact({
  initialValue,
  onNewValue,
}: {
  initialValue: string;
  onNewValue: (x: string) => void;
}) {
  const [currentColor, setCurrentColor] = React.useState(initialValue);

  return (
    <SketchPicker
      color={currentColor}
      onChange={(color) => {
        setCurrentColor(color.hex);
        onNewValue(color.hex);
      }}
    />
  );
}

makeReactOutput<{ value: string }>({
  tagName: "custom-component-output",
  renderComp: ({ value }) => (
    <div
      style={{
        backgroundColor: value,
        border: "1px solid black",
        height: "100px",
        width: "100px",
      }}
    />
  ),
});
