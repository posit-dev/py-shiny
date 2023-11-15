import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * An example element.
 *
 * @csspart display - The span containing the value
 */
@customElement("shiny-custom-output")
export class ShinyCustomOutput extends LitElement {
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

  override render() {
    return html`
      <span part="display"> Value: ${this.count} </span>
      <slot></slot>
    `;
  }
}

class CustomOutputBinding extends Shiny.OutputBinding {
  /**
   * Find the element that will be rendered by this output binding.
   * @param scope The scope in which to search for the element.
   * @returns The element that will be rendered by this output
   * binding.
   */
  override find(scope: JQuery<HTMLElement>) {
    return scope.find("shiny-custom-output");
  }

  /**
   * Function to run when rendering the output. This function will be passed the
   * element that was found by `find()` and the payload that was sent by the
   * server when there's new data to render. Note that the element passed may
   * already be populated with content from a previous render and it is up to
   * the function to clear the element and re-render the content.
   * @param el The element that was found by `find()`
   * @param payload An object as provided from server with the
   * `render_custom_output` function
   */
  override renderValue(el: HTMLElement, payload: { value: number }) {
    // Return early if el is not an instance of the custom element
    if (!(el instanceof ShinyCustomOutput)) {
      return;
    }

    el.count = payload.value;
  }
}
Shiny.outputBindings.register(new CustomOutputBinding(), "shiny-custom-output");
