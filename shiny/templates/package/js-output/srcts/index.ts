import { LitElement, html, css } from "lit";
import { property } from "lit/decorators.js";

import { makeOutputBindingWebComponent } from "@posit-dev/shiny-bindings-core";

// What the server-side output binding will send to the client. It's important
// to make sure this matches what the python code is sending.
type Payload = { value: number };

/**
 * An example element.
 *
 * @csspart display - The span containing the value
 */
export class CustomComponentEl extends LitElement {
  static override styles = css`
    :host {
      display: block;
      border: solid 1px gray;
      padding: 16px;
      max-width: 800px;
    }
  `;

  /**
   * The number of times the button has been clicked.
   */
  @property({ type: Number })
  count = 0;

  onNewValue(payload: Payload) {
    this.count = payload.value;
  }

  override render() {
    return html`
      <span part="display"> Value: ${this.count} </span>
      <slot></slot>
    `;
  }
}

// Setup output binding. This also registers the custom element.

makeOutputBindingWebComponent<Payload>("custom-component", CustomComponentEl);
