import { createRoot } from "react-dom/client";
import { SketchPicker } from "react-color";
import type { ColorResult } from "react-color";
import React from "react";

const customInputTag = "custom-react-input";

const styleTag = `${customInputTag} {
  display: block;
  border: solid 1px gray;
  padding: 16px;
  width: fit-content;
}`;

/**
 * A webcomponent that wraps a react component. This is the component that
 * Shiny will interact with. By using a webcomponent here we can encapsulate
 * all the dependencies and logic for the react component and only expose a
 * simple HTML tag interface to Shiny.
 */
export class ShinyReactComponent extends HTMLElement {
  /**
   * The current value of the input.
   */
  value: string = "#fff";

  onChangeCallback: () => void = () => null;

  constructor() {
    super();
    // Add styles to the dom for this component
    addStylesForTag(customInputTag, styleTag);
  }

  /**
   * Function to run when the a new color is shown. First updates the value and
   * then tells Shiny that there is an updated value
   */
  onNewColor(color: string) {
    this.value = color;
    this.onChangeCallback();
  }

  connectedCallback() {
    // Render the react component into the root
    // Note the use of arrow functions. This makes sure the `this` stays the
    // webcomponent and doesn't get bound away by react.
    createRoot(this).render(
      <ColorPickerReact
        initialColor={this.value}
        currentColorCallback={(color) => this.onNewColor(color)}
      />
    );
  }
}

// Color Picker React component
function ColorPickerReact({
  initialColor,
  currentColorCallback,
}: {
  initialColor: string;
  currentColorCallback: (x: string) => void;
}) {
  const [currentColor, setCurrentColor] = React.useState<string>(initialColor);

  function handleChange(color: ColorResult) {
    setCurrentColor(color.hex);
    currentColorCallback(color.hex);
  }

  return <SketchPicker color={currentColor} onChange={handleChange} />;
}

customElements.define(customInputTag, ShinyReactComponent);

// Setup the input binding for the custom input
class ReactWithLitBinding extends Shiny.InputBinding {
  override find(scope: HTMLElement): JQuery<HTMLElement> {
    return $(scope).find(customInputTag);
  }

  override getValue(el: ShinyReactComponent) {
    // Our component stores the value in the `value` property. In this case it's
    // a string with the current color.
    return el.value;
  }

  override subscribe(
    el: ShinyReactComponent,
    callback: (x: boolean) => void
  ): void {
    // Hook up callback used to tell Shiny that the value has changed
    // to the onChangeCallback of the webcomponent we created
    el.onChangeCallback = () => callback(true);
  }

  override unsubscribe(el: ShinyReactComponent): void {
    // Remove the value-has-updated callback so that it doesn't get called
    // after Shiny is no longer bound to the element
    el.onChangeCallback = () => null;
  }
}

Shiny.inputBindings.register(new ReactWithLitBinding(), customInputTag);
/**
 * Add styles to the dom for a given tag but only once.
 * @param tag Name of the tag to add styles for
 * @param styles Styles to add
 */
export function addStylesForTag(tag: string, styles: string) {
  // If the styles are already in the dom, don't add them again
  if (document.querySelector(`style[data-wcstyles="${tag}"]`)) {
    return;
  }
  const styleEl = document.createElement("style");
  styleEl.dataset[`wcstyles`] = tag;
  styleEl.innerHTML = styles;
  document.head.appendChild(styleEl);
}
