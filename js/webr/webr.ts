import { html } from "lit";

import { WebR } from "https://webr.r-wasm.org/latest/webr.mjs";
import { Message } from "webr/dist/webR/chan/message";
import { WebRDataJs } from "webr/dist/webR/robj";
import { LightElement } from "../utils/_utils";

type CaptureRResult = {
  result: unknown; // Should be JSONifiable
  output: {
    type: string;
    data: any;
  }[];
  images: string[];
};

const WEBR_COMPONENT_TAG = "shiny-webr-component";
const PLOT_WIDTH = 400;
const PLOT_HEIGHT = 300;

class WebRComponent extends LightElement {
  webR: WebR;

  private output!: HTMLElement;
  private input!: HTMLInputElement;
  private plot!: HTMLCanvasElement;

  private outputId: string;
  private inputId: string;
  private runId: string;
  private plotId: string;

  constructor() {
    super();
    this.outputId = this.id + "_output";
    this.inputId = this.id + "_input";
    this.runId = this.id + "_run";
    this.plotId = this.id + "_plot";

    this.webR = new WebR();
  }

  render() {
    return html`<div>
      <pre style="max-height: 500px"><code id="${this
        .outputId}">Loading webR, please wait...</code></pre>
      <div>
        <input
          spellcheck="false"
          autocomplete="off"
          id="${this.inputId}"
          type="text"
          style="width: 100%;"
        />
        <button id="${this.runId}">Run</button>
      </div>
      <div id="${this.plotId}"></div>
    </div>`;
  }

  firstUpdated() {
    this.output = document.getElementById(this.outputId) as HTMLElement;
    this.input = document.getElementById(this.inputId) as HTMLInputElement;
    this.plot = document.getElementById(this.plotId) as HTMLCanvasElement;

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    (async () => {
      await this.webR.init();
      this.output.textContent = `webR ${this.webR.version}\n`;
      const result = await this.webR.flush();
      result.forEach((msg) => this.handleOutput(msg));

      // await this.webR.evalR(
      //   `options(device=webr::canvas(${PLOT_WIDTH * 2}, ${PLOT_HEIGHT * 2}))`
      // );
    })();

    const sendInput = async () => {
      await this.evalInConsole(this.input.value);
      this.input.value = "";
    };

    /* Send input on Enter key */
    this.input.addEventListener("keydown", (e) => {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
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
        this.handleImage(msg.data.image);
        break;
      case "closed":
        return;
      default:
        console.warn(`Unhandled output type for webR: ${msg.type}.`);
    }
  }

  handleImage(img: ImageBitmap) {
    const canvas = document.createElement("canvas");
    canvas.style.width = `${img.width / 2}px`;
    canvas.style.height = `${img.height / 2}px`;
    canvas.style.margin = "2px";
    canvas.style.border = "1px solid black";
    canvas.style.borderRadius = "3";
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext("2d")!;
    ctx.drawImage(img, 0, 0, img.width, img.height);
    this.plot.insertBefore(canvas, this.plot.firstChild);
  }

  async evalInConsole(code: string): Promise<CaptureRResult> {
    this.appendToOutEl(code + "\n");

    const shelter = await new this.webR.Shelter();
    const res = await shelter.captureR(code, {
      withAutoprint: true,
      captureGraphics: {
        width: PLOT_WIDTH,
        height: PLOT_HEIGHT,
      },
    });
    const moreResults = await this.webR.flush();
    res.output.forEach((msg) => this.handleOutput(msg));
    res.images.forEach((img) => this.handleImage(img));
    console.log(res);
    console.log(moreResults);

    let resultJson: WebRDataJs = {
      type: "null",
    };
    let imagesJson: string[] = [];
    try {
      resultJson = await res.result.toJs();
      imagesJson = await Promise.all(
        res.images.map(async (img) => {
          return await imageBitmapToPngBase64(img);
        })
      );
    } catch (e) {
      console.warn(e);
    }
    const newResult = {
      ...res,
      result: resultJson,
      images: imagesJson,
    };
    await shelter.purge();
    this.prompt();

    return newResult;
  }

  prompt() {
    this.appendToOutEl("> ");
  }

  private appendToOutEl(line: string) {
    this.output.append(line);
    const parent = this.output.parentElement!;
    parent.scrollTo({
      top: parent.scrollHeight,
      behavior: "smooth",
    });
  }
}

customElements.define(WEBR_COMPONENT_TAG, WebRComponent);

window.Shiny.addCustomMessageHandler("eval_r", async function (message) {
  const el = document.getElementById(message.id) as WebRComponent;
  const result = await el.evalInConsole(message.code);
  window.Shiny.shinyapp!.makeRequest(
    message.handler_id,
    [result],
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    (msg) => {},
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    (msg) => {},
    undefined
  );
});

/**
 * Converts an ImageBitmap to a base64 encoded PNG string
 * @param bitmap - The ImageBitmap to convert
 * @returns A Promise that resolves to a base64 encoded PNG string
 */
async function imageBitmapToPngBase64(bitmap: ImageBitmap): Promise<string> {
  // Create a canvas element with the same dimensions as the bitmap
  const canvas = document.createElement("canvas");
  canvas.width = bitmap.width;
  canvas.height = bitmap.height;

  // Get the 2D rendering context
  const ctx = canvas.getContext("2d");

  if (!ctx) {
    throw new Error("Could not get canvas context");
  }

  // Draw the bitmap onto the canvas
  ctx.drawImage(bitmap, 0, 0);

  // Convert the canvas to a PNG data URL
  const dataURL = canvas.toDataURL("image/png");

  // Extract the base64 data (remove the data URL prefix)
  const base64Data = dataURL.split(",")[1];

  return base64Data;
}
