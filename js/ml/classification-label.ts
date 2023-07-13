import { LitElement, css, html } from "lit";
import { property } from "lit/decorators.js";

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
      margin-top: 20px;
      margin-bottom: 20px;
    }

    .winner {
      display: flex;
      justify-content: center;
      font-weight: bold;
      font-size: 1.75em;
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
      margin-left: 0.5em;
      margin-right: 0.5em;
    }
  `;

  @property({ type: Object }) value: Record<string, number> = {};
  @property({ type: Number }) sort: number = 1;
  @property({ type: Number, attribute: "display-winner" })
  displayWinner: number = 0;
  @property({ type: Number, attribute: "max-items" })
  maxItems: number | null = null;

  render() {
    let entries = Object.entries(this.value);

    if (this.maxItems !== null) {
      entries = truncateEntries(entries, this.maxItems);
    }

    if (this.sort) {
      entries.sort((a, b) => b[1] - a[1]);
    }

    let winnerHTML = null;
    if (this.displayWinner) {
      // Entries might not be sorted, so we need to loop through again.
      const currentWinner = { name: "", value: -Infinity };
      entries.forEach(([k, v]) => {
        if (v > currentWinner.value) {
          currentWinner.name = k;
          currentWinner.value = v;
        }
      });
      winnerHTML = html`<div class="winner">${currentWinner.name}</div>`;
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

    return html`<div class="wrapper">${winnerHTML} ${valuesHtml}</div> `;
  }
}

customElements.define("shiny-classification-label", ShinyClassificationLabel);

function truncateEntries(entries: [string, number][], maxItems: number | null) {
  // Just the numeric values
  const values = entries.map(([_, v]) => v);
  values.sort().reverse();

  const cutoffValue = values[maxItems - 1];

  const newEntries = [];
  for (const entry of entries) {
    if (entry[1] >= cutoffValue) {
      newEntries.push(entry);
      // In case there are multiple items that match cutoffValue, we need to make sure
      // we don't add more entries than were asked for.
      if (newEntries.length === maxItems) {
        break;
      }
    }
  }

  return newEntries;
}
