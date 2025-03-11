import { PropertyValues, html } from "lit";
import { unsafeHTML } from "lit-html/directives/unsafe-html.js";
import { property } from "lit/decorators.js";

import ClipboardJS from "clipboard";
import hljs from "highlight.js/lib/common";
import { Renderer, parse } from "marked";

import {
  LightElement,
  createElement,
  createSVGIcon,
  renderDependencies,
  sanitizeHTML,
  showShinyClientMessage,
  throttle,
} from "../utils/_utils";

import type { HtmlDep } from "../utils/_utils";

type ContentType = "markdown" | "semi-markdown" | "html" | "text";

type ContentMessage = {
  id: string;
  content: string;
  operation: "append" | "replace";
  html_deps?: HtmlDep[];
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
const SVG_DOT_CLASS = "markdown-stream-dot";
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
    return unsafeHTML(sanitizeHTML(parse(content) as string));
  } else if (content_type === "semi-markdown") {
    return unsafeHTML(sanitizeHTML(parse(content, markedEscapeOpts) as string));
  } else if (content_type === "html") {
    return unsafeHTML(sanitizeHTML(content));
  } else if (content_type === "text") {
    return content;
  } else {
    throw new Error(`Unknown content type: ${content_type}`);
  }
}

class MarkdownElement extends LightElement {
  @property() content = "";
  @property({ attribute: "content-type" })
  content_type: ContentType = "markdown";
  @property({ type: Boolean, reflect: true })
  streaming = false;
  @property({ type: Boolean, reflect: true, attribute: "auto-scroll" })
  auto_scroll = false;
  @property({ type: Function }) onContentChange?: () => void;
  @property({ type: Function }) onStreamEnd?: () => void;

  render() {
    return html`${contentToHTML(this.content, this.content_type)}`;
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this.#cleanup();
  }

  protected willUpdate(changedProperties: PropertyValues): void {
    if (changedProperties.has("content")) {
      this.#isContentBeingAdded = true;

      MarkdownElement.#doUnBind(this);
    }
    super.willUpdate(changedProperties);
  }

  protected updated(changedProperties: Map<string, unknown>): void {
    if (changedProperties.has("content")) {
      // Post-process DOM after content has been added
      try {
        this.#highlightAndCodeCopy();
      } catch (error) {
        console.warn("Failed to highlight code:", error);
      }

      // Render Shiny HTML dependencies and bind inputs/outputs
      if (this.streaming) {
        this.#appendStreamingDot();
        MarkdownElement._throttledBind(this);
      } else {
        MarkdownElement.#doBind(this);
      }

      // Update scrollable element after content has been added
      this.#updateScrollableElement();

      // Possibly scroll to bottom after content has been added
      this.#isContentBeingAdded = false;
      this.#maybeScrollToBottom();

      if (this.onContentChange) {
        try {
          this.onContentChange();
        } catch (error) {
          console.warn("Failed to call onContentUpdate callback:", error);
        }
      }
    }

    if (changedProperties.has("streaming")) {
      if (this.streaming) {
        this.#appendStreamingDot();
      } else {
        this.#removeStreamingDot();
        if (this.onStreamEnd) {
          try {
            this.onStreamEnd();
          } catch (error) {
            console.warn("Failed to call onStreamEnd callback:", error);
          }
        }
      }
    }
  }

  #appendStreamingDot(): void {
    this.lastElementChild?.appendChild(SVG_DOT);
  }

  #removeStreamingDot(): void {
    this.querySelector(`svg.${SVG_DOT_CLASS}`)?.remove();
  }

  static async #doUnBind(el: HTMLElement): Promise<void> {
    if (!window.Shiny) return;
    if (!Shiny.unbindAll) return;

    try {
      Shiny.unbindAll(el);
    } catch (err) {
      showShinyClientMessage({
        status: "error",
        message: `Failed to unbind Shiny inputs/outputs: ${err}`,
      });
    }
  }

  static async #doBind(el: HTMLElement): Promise<void> {
    if (!window.Shiny) return;
    if (!Shiny.initializeInputs) return;
    if (!Shiny.bindAll) return;

    try {
      Shiny.initializeInputs(el);
    } catch (err) {
      showShinyClientMessage({
        status: "error",
        message: `Failed to initialize Shiny inputs: ${err}`,
      });
    }

    try {
      await Shiny.bindAll(el);
    } catch (err) {
      showShinyClientMessage({
        status: "error",
        message: `Failed to bind Shiny inputs/outputs: ${err}`,
      });
    }
  }

  @throttle(200)
  private static async _throttledBind(el: HTMLElement): Promise<void> {
    await this.#doBind(el);
  }

  #highlightAndCodeCopy(): void {
    const el = this.querySelector("pre code");
    if (!el) return;
    this.querySelectorAll<HTMLElement>("pre code").forEach((el) => {
      if (el.dataset.highlighted === "yes") return;

      hljs.highlightElement(el);

      // Add copy button
      const btn = createElement("button", {
        class: "code-copy-button",
        title: "Copy to clipboard",
      });
      btn.innerHTML = '<i class="bi"></i>';
      el.prepend(btn);

      // Setup clipboard
      const clipboard = new ClipboardJS(btn, { target: () => el });
      clipboard.on("success", (e) => {
        btn.classList.add("code-copy-button-checked");
        setTimeout(
          () => btn.classList.remove("code-copy-button-checked"),
          2000
        );
        e.clearSelection();
      });
    });
  }

  // ------- Scrolling logic -------

  // Nearest scrollable parent element (if any)
  #scrollableElement: HTMLElement | null = null;
  // Whether content is currently being added to the element
  #isContentBeingAdded = false;
  // Whether the user has scrolled away from the bottom
  #isUserScrolled = false;

  #onScroll = (): void => {
    if (!this.#isContentBeingAdded) {
      this.#isUserScrolled = !this.#isNearBottom();
    }
  };

  #isNearBottom(): boolean {
    const el = this.#scrollableElement;
    if (!el) return false;

    return el.scrollHeight - (el.scrollTop + el.clientHeight) < 50;
  }

  #updateScrollableElement(): void {
    const el = this.#findScrollableParent();

    if (el !== this.#scrollableElement) {
      this.#scrollableElement?.removeEventListener("scroll", this.#onScroll);
      this.#scrollableElement = el;
      this.#scrollableElement?.addEventListener("scroll", this.#onScroll);
    }
  }

  #findScrollableParent(): HTMLElement | null {
    if (!this.auto_scroll) return null;

    // eslint-disable-next-line
    let el: HTMLElement | null = this;
    while (el) {
      if (el.scrollHeight > el.clientHeight) return el;
      el = el.parentElement;
    }
    return null;
  }

  #maybeScrollToBottom(): void {
    const el = this.#scrollableElement;
    if (!el || this.#isUserScrolled) return;

    el.scroll({
      top: el.scrollHeight - el.clientHeight,
      behavior: this.streaming ? "instant" : "smooth",
    });
  }

  #cleanup(): void {
    this.#scrollableElement?.removeEventListener("scroll", this.#onScroll);
    this.#scrollableElement = null;
    this.#isUserScrolled = false;
  }
}

// ------- Register custom elements and shiny bindings ---------

if (!customElements.get("shiny-markdown-stream")) {
  customElements.define("shiny-markdown-stream", MarkdownElement);
}

async function handleMessage(
  message: ContentMessage | IsStreamingMessage
): Promise<void> {
  const el = document.getElementById(message.id) as MarkdownElement;

  if (!el) {
    showShinyClientMessage({
      status: "error",
      message: `Unable to handle MarkdownStream() message since element with id
      ${message.id} wasn't found. Do you need to call .ui() (Express) or need a
      output_markdown_stream('${message.id}') in the UI (Core)?`,
    });
    return;
  }

  if (isStreamingMessage(message)) {
    el.streaming = message.isStreaming;
    return;
  }

  if (message.html_deps) {
    await renderDependencies(message.html_deps);
  }

  if (message.operation === "replace") {
    el.setAttribute("content", message.content);
  } else if (message.operation === "append") {
    const content = el.getAttribute("content");
    el.setAttribute("content", content + message.content);
  } else {
    throw new Error(`Unknown operation: ${message.operation}`);
  }
}

window.Shiny.addCustomMessageHandler(
  "shinyMarkdownStreamMessage",
  handleMessage
);

export { MarkdownElement, contentToHTML };
