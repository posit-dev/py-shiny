import { LitElement, css, html } from "lit";
import { property } from "lit/decorators.js";
import { makeOutputBinding } from "./make-output-binding";

export class ShinyClassificationLabel extends LitElement {
  static styles = css`
    :host {
      display: block;
      padding-bottom: 2rem;
    }

    .wrapper {
      border: 1px solid #ccc;
      padding: 12px;
      border-radius: 5px;
    }

    .item {
      margin-top: 15px;
    }

    .bar {
      height: 5px;
      margin-top: 5px;
      margin-bottom: 5px;
      background-color: #4890e3;
      border-radius: 2px;
    }

    .label {
      display: flex;
      flex-direction: row;
      align-items: baseline;
    }

    .dashed-line {
      flex: 1 1 0%;
      border-bottom: 1px dashed #888;
      margin-left: 0.5rem;
      margin-right: 0.5rem;
    }
  `;

  @property({ type: Object }) value: Record<string, number> = {};
  @property({ type: Number }) sort: number = 1;

  render() {
    const entries = Object.entries(this.value);

    if (this.sort) {
      entries.sort((a, b) => b[1] - a[1]);
    }

    const valuesHtml = entries.map(([k, v]) => {
      return html`<div class="item">
        <div class="bar" style="width: ${v}%;"></div>
        <div class="label">
          <div>${k}</div>
          <div class="dashed-line"></div>
          <div>${v}%</div>
        </div>
      </div>`;
    });

    return html` <div class="wrapper">${valuesHtml}</div> `;
  }
}

// Register the custom element with the browser.
customElements.define("shiny-classification-label", ShinyClassificationLabel);

makeOutputBinding("shiny-classification-label");
