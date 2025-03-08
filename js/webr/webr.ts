import { html } from "lit";

import { RObject, WebR } from "https://webr.r-wasm.org/latest/webr.mjs";
import { Message } from "webr/dist/webR/chan/message";
import { LightElement } from "../utils/_utils";

type CaptureRResult = {
  result: unknown; // Should be JSONifiable
  output: {
    type: string;
    data: any;
  }[];
  images: ImageBitmap[];
};

const WEBR_COMPONENT_TAG = "shiny-webr-component";

class WebRComponent extends LightElement {
  // webRConsole: Console;
  webR: WebR;

  private output!: HTMLElement;
  private input!: HTMLInputElement;

  private outputId: string;
  private inputId: string;
  private runId: string;

  constructor() {
    super();
    this.outputId = this.id + "_output";
    this.inputId = this.id + "_input";
    this.runId = this.id + "_run";

    this.webR = new WebR();
  }

  render() {
    return html`<div>
      <pre><code id="${this.outputId}">Loading webR, please wait...</code></pre>
      <input
        spellcheck="false"
        autocomplete="off"
        id="${this.inputId}"
        type="text"
        style="width: 100%;"
      />
      <button id="${this.runId}">Run</button>
    </div>`;
  }

  firstUpdated() {
    this.output = document.getElementById(this.outputId) as HTMLElement;
    this.input = document.getElementById(this.inputId) as HTMLInputElement;
    this.webR.init().then(() => {
      this.output.textContent = `webR ${this.webR.version}\n`;
      this.prompt();
    });

    const sendInput = async () => {
      this.evalInConsole(this.input.value);
      this.input.value = "";
    };

    /* Send input on Enter key */
    this.input.addEventListener("keydown", (e) => {
      if (e.code === "Enter") sendInput();
    });

    const runButton = document.getElementById(this.runId) as HTMLButtonElement;
    runButton.addEventListener("click", sendInput);
  }

  handleOutput(msg: Message) {
    switch (msg.type) {
      case "stdout":
        this.appendToOutEl((msg.data as string) + "\n");
        break;
      case "stderr":
        this.appendToOutEl((msg.data as string) + "\n");
        break;
      case "prompt":
        console.log("prompt");
        this.appendToOutEl(msg.data as string);
        break;
      case "canvas":
        console.log("canvas");
        break;
      case "closed":
        return;
      default:
        console.warn(`Unhandled output type for webR: ${msg.type}.`);
    }
  }

  async evalInConsole(code: string): Promise<CaptureRResult> {
    this.appendToOutEl(code + "\n");

    const shelter = await new this.webR.Shelter();
    const result = await shelter.captureR(code, {
      withAutoprint: true,
    });
    result.output.forEach((msg) => this.handleOutput(msg));

    shelter.purge();
    this.prompt();

    const newResult = {
      ...result,
      result: await result.result.toJs(),
    };

    return newResult;
  }

  prompt() {
    this.appendToOutEl("> ");
  }

  private appendToOutEl(line: string) {
    this.output.append(line);
  }
}

customElements.define(WEBR_COMPONENT_TAG, WebRComponent);

window.Shiny.addCustomMessageHandler("eval_r", async function (message) {
  const el = document.getElementById(message.id) as WebRComponent;
  const result = await el.evalInConsole(message.code);
  window.Shiny.setInputValue!(message.id + "_result", result);
});
