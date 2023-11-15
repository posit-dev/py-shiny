import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

const customInputTag = "shiny-custom-input";
/**
 * An example element.
 *
 * @csspart button - The button that increments the value
 * @csspart display - The span containing the value
 */
@customElement(customInputTag)
export class ShinyCustomInput extends LitElement {
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
  onChangeCallback: null | ((x: boolean) => void) = null;

  /**
   * Function to run when the increment button is clicked.
   */
  onIncrement() {
    this.value++;
    this.onChangeCallback?.(true);
  }

  override render() {
    return html`
      <button @click=${this.onIncrement} part="button">increment</button>
      <span part="display"> Value: ${this.value} </span>
      <slot></slot>
    `;
  }
}

// Setup the input binding for the custom input
class CustomInputBinding extends Shiny.InputBinding {
  constructor() {
    super();
  }

  override find(scope: HTMLElement): JQuery<HTMLElement> {
    return $(scope).find(customInputTag);
  }

  override getValue(el: ShinyCustomInput) {
    return el.value;
  }

  override subscribe(
    el: ShinyCustomInput,
    callback: (x: boolean) => void
  ): void {
    // Our custom input has a callback that it calls when its value has changed.
    // By setting this here we can alert Shiny that the value has changed and it
    // should check for the latest value.
    el.onChangeCallback = callback;
  }
}

Shiny.inputBindings.register(new CustomInputBinding(), customInputTag);
