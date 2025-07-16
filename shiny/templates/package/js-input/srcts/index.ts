import { LitElement, html, css } from "lit";
import { property } from "lit/decorators.js";
import type { CustomElementInput } from "@posit-dev/shiny-bindings-core";
import { makeInputBinding } from "@posit-dev/shiny-bindings-core";

/**
 * An example element.
 *
 * @csspart button - The button that increments the value
 * @csspart display - The span containing the value
 */
export class CustomComponentEl
  extends LitElement
  implements CustomElementInput<number>
{
  static override styles = css`
    :host {
      display: block;
      border: solid 1px gray;
      padding: 16px;
      max-width: 800px;
      width: fit-content;
    }
  `;

  @property({ type: Number })
  value = 0;

  /*
   * The callback function that is called when the value of the input changes.
   * This alerts Shiny that the value has changed and it should check for the
   * latest value. This is set by the input binding.
   */
  notifyBindingOfChange: (x?: boolean) => void = () => {};

  /**
   * Function to run when the increment button is clicked.
   */
  onIncrement() {
    this.value++;
    this.notifyBindingOfChange(true);
  }

  override render() {
    return html`
      <button @click=${this.onIncrement} part="button">increment</button>
      <span part="display"> Value: ${this.value} </span>
      <slot></slot>
    `;
  }
}

// Setup the input binding
makeInputBinding("custom-component", CustomComponentEl, {
  registerElement: true,
});
