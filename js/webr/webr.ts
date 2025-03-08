import { html } from "lit";

import { Console } from "https://webr.r-wasm.org/latest/webr.mjs";
import { ShinyClass } from "rstudio-shiny/srcts/types/src/shiny";
import { LightElement } from "../utils/_utils";

const WEBR_COMPONENT_TAG = "shiny-webr-component";
const OUTPUT_ID = "webr-output";
const INPUT_ID = "webr-input";
const RUN_ID = "webr-run";

class WebRComponent extends LightElement {
  webRConsole: Console;

  private resolveEvalCode: ((value: string) => void) | null = null;

  private enableCaptureOutput = false;
  private capturedOutput: string[] = [];
  private captureOutput(s: string) {
    if (this.enableCaptureOutput) {
      this.capturedOutput.push(s);
    }
  }

  constructor() {
    super();

    this.webRConsole = new Console({
      stdout: (line) => this.appendToOutEl(line + "\n"),
      stderr: (line) => this.appendToOutEl(line + "\n"),
      prompt: (p) => {
        if (this.resolveEvalCode) {
          this.resolveEvalCode(this.capturedOutput.join("\n"));
          this.enableCaptureOutput = false;

          // Reset the captured output
          this.capturedOutput.length = 0;
          this.resolveEvalCode = null;
        }
        this.appendToOutEl(p);
      },
    });
    this.webRConsole.run();
  }

  render() {
    return html`<div>
      <pre><code id="${OUTPUT_ID}">Loading webR, please wait...</code></pre>
      <input
        spellcheck="false"
        autocomplete="off"
        id="${INPUT_ID}"
        type="text"
        style="width: 100%;"
      />
      <button id="${RUN_ID}">Run</button>
    </div>`;
  }

  firstUpdated() {
    const input = document.getElementById(INPUT_ID) as HTMLInputElement;

    const sendInput = () => {
      this.webRConsole.stdin(input.value);
      this.appendToOutEl(input.value + "\n");
      input.value = "";
    };

    /* Send input on Enter key */
    input.addEventListener("keydown", (e) => {
      if (e.code === "Enter") sendInput();
    });

    const runButton = document.getElementById(RUN_ID) as HTMLButtonElement;
    runButton.addEventListener("click", sendInput);
  }

  evalR(code: string): Promise<string> {
    this.webRConsole.stdin(code);
    this.appendToOutEl(code + "\n");

    this.enableCaptureOutput = true;
    return new Promise((resolve) => {
      this.resolveEvalCode = resolve;
    });
  }

  private appendToOutEl(line: string) {
    const outEl = document.getElementById(OUTPUT_ID) as HTMLElement;
    outEl.append(line);
    this.captureOutput(line);
  }
}

customElements.define(WEBR_COMPONENT_TAG, WebRComponent);

Shiny.initializedPromise.then(() => {
  Shiny.addCustomMessageHandler("eval_r", async function (message) {
    const el = document.getElementById(message.id) as WebRComponent;
    const result = await el.evalR(message.code);
    Shiny.setInputValue!(message.id + "_result", result);
  });
});

// This is a workaround to let TypeScript know that Shiny is a global.
// See https://github.com/rstudio/shiny/issues/4197
declare global {
  const Shiny: ShinyClass;
  interface Window {
    Shiny: ShinyClass;
  }
}
