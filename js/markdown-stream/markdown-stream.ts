import { LitElement, html } from "lit";
import { unsafeHTML } from "lit-html/directives/unsafe-html.js";
import { property } from "lit/decorators.js";

import ClipboardJS from "clipboard";
import { sanitize } from "dompurify";
import hljs from "highlight.js/lib/common";
import { Renderer, parse } from "marked";

import {
  LightElement,
  createElement,
  createSVGIcon,
  showShinyClientMessage,
} from "../utils/_utils";

type ContentType = "markdown" | "semi-markdown" | "html" | "text";

type ContentMessage = {
  id: string;
  content: string;
  operation: "append" | "replace";
};

type IsStreamingMessage = {
  id: string;
  isStreaming: boolean;
};

// Type guard
function isStreamingMessage(
  message: ContentMessage | IsStreamingMessage
): message is IsStreamingMessage {
  return "isStreaming" in message;
}

// SVG dot to indicate content is currently streaming
const SVG_DOT_CLASS = "chat-streaming-dot";
const SVG_DOT = createSVGIcon(
  `<svg width="12" height="12" xmlns="http://www.w3.org/2000/svg" class="${SVG_DOT_CLASS}" style="margin-left:.25em;margin-top:-.25em"><circle cx="6" cy="6" r="6"/></svg>`
);

// For rendering chat output, we use typical Markdown behavior of passing through raw
// HTML (albeit sanitizing afterwards).
//
// For echoing chat input, we escape HTML. This is not for security reasons but just
// because it's confusing if the user is using tag-like syntax to demarcate parts of
// their prompt for other reasons (like <User>/<Assistant> for providing examples to the
// chat model), and those tags simply vanish.
const rendererEscapeHTML = new Renderer();
rendererEscapeHTML.html = (html: string) =>
  html
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
const markedEscapeOpts = { renderer: rendererEscapeHTML };

function contentToHTML(content: string, content_type: ContentType) {
  if (content_type === "markdown") {
    return unsafeHTML(sanitize(parse(content) as string));
  } else if (content_type === "semi-markdown") {
    return unsafeHTML(sanitize(parse(content, markedEscapeOpts) as string));
  } else if (content_type === "html") {
    return unsafeHTML(sanitize(content));
  } else if (content_type === "text") {
    return content;
  } else {
    throw new Error(`Unknown content type: ${content_type}`);
  }
}

class MarkdownElement extends LightElement {
  @property() content = "";
  @property() content_type: ContentType = "markdown";
  @property({ type: Boolean, reflect: true }) streaming = false;

  render(): ReturnType<LitElement["render"]> {
    const content = contentToHTML(this.content, this.content_type);
    return html`${content}`;
  }

  updated(changedProperties: Map<string, unknown>): void {
    if (changedProperties.has("content")) {
      this.#highlightAndCodeCopy();
      if (this.streaming) this.#appendStreamingDot();
      // TODO: throw an event here that content has rendered and catch it in SHINY_CHAT_MESSAGE
      // requestScroll(this, this.streaming);
    }
    if (changedProperties.has("streaming")) {
      this.streaming ? this.#appendStreamingDot() : this.#removeStreamingDot();
    }
  }

  #appendStreamingDot(): void {
    this.lastElementChild?.appendChild(SVG_DOT);
  }

  #removeStreamingDot(): void {
    this.querySelector(`svg.${SVG_DOT_CLASS}`)?.remove();
  }

  // Highlight code blocks after the element is rendered
  #highlightAndCodeCopy(): void {
    const el = this.querySelector("pre code");
    if (!el) return;
    this.querySelectorAll<HTMLElement>("pre code").forEach((el) => {
      // Highlight the code
      hljs.highlightElement(el);
      // Add a button to the code block to copy to clipboard
      const btn = createElement("button", {
        class: "code-copy-button",
        title: "Copy to clipboard",
      });
      btn.innerHTML = '<i class="bi"></i>';
      el.prepend(btn);
      // Add the clipboard functionality
      const clipboard = new ClipboardJS(btn, { target: () => el });
      clipboard.on("success", function (e: ClipboardJS.Event) {
        btn.classList.add("code-copy-button-checked");
        setTimeout(
          () => btn.classList.remove("code-copy-button-checked"),
          2000
        );
        e.clearSelection();
      });
    });
  }
}

// ------- Register custom elements and shiny bindings ---------

if (!customElements.get("shiny-markdown-stream")) {
  customElements.define("shiny-markdown-stream", MarkdownElement);
}

function handleMessage(message: ContentMessage | IsStreamingMessage): void {
  const el = document.getElementById(message.id) as MarkdownElement;

  if (!el) {
    const errMsg = `
      Cannot handle MarkdownStream message: element with id ${message.id} not found.
      Do you need to call .ui() (Express) or fix the id (Core)?
    `;
    console.error(errMsg);
    showShinyClientMessage({ message: errMsg, status: "error" });
    return;
  }

  if (isStreamingMessage(message)) {
    el.streaming = message.isStreaming;
    return;
  }

  if (message.operation === "replace") {
    el.setAttribute("content", message.content);
  } else if (message.operation === "append") {
    const content = el.getAttribute("content");
    el.setAttribute("content", content + message.content);
  } else {
    console.error(`Unknown operation: ${message.operation}`);
  }
}

$(function () {
  Shiny.addCustomMessageHandler("shinyMarkdownStreamMessage", handleMessage);
});

export { MarkdownElement, contentToHTML };
