import { SketchPicker } from "react-color";
import React from "react";

import { makeReactInput } from "@posit-dev/shiny-bindings-react";

// Generates a new input binding that renders the supplied react component
// into the root of the webcomponent.
makeReactInput({
  tagName: "custom-component",
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
