import { SketchPicker } from "react-color";
import type { ColorResult } from "react-color";
import React from "react";

import { makeReactInput } from "@shiny-helpers/react";

// Generates a new input binding that renders the supplied react component
// into the root of the webcomponent.
makeReactInput({
  tagName: "custom-component",
  initialValue: "#fff",
  renderComp: ({ onNewValue }) => (
    <ColorPickerReact
      initialValue="#fff"
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
  const [currentColor, setCurrentColor] = React.useState<string>(initialValue);

  return (
    <SketchPicker
      color={currentColor}
      onChange={(color: ColorResult) => {
        setCurrentColor(color.hex);
        onNewValue(color.hex);
      }}
    />
  );
}
