import { LitElement, html } from "lit";
import { unsafeHTML } from "lit-html/directives/unsafe-html.js";
import { property } from "lit/decorators.js";

import {
  LightElement,
  createElement,
  renderDependencies,
  showShinyClientMessage,
} from "../utils/_utils";

import type { HtmlDep } from "../utils/_utils";

type ContentType = "markdown" | "html" | "text";

type Message = {
  content: string;
  role: "user" | "assistant";
  chunk_type: "message_start" | "message_end" | null;
  content_type: ContentType;
  icon?: string;
  operation: "append" | null;
};

type ShinyChatMessage = {
  id: string;
  handler: string;
  // Message keys will create custom element attributes, but html_deps are handled
  // separately
  obj: (Message & { html_deps?: HtmlDep[] }) | null;
};

type UpdateUserInput = {
  value?: string;
  placeholder?: string;
  submit?: false;
  focus?: false;
};

// https://github.com/microsoft/TypeScript/issues/28357#issuecomment-748550734
declare global {
  interface GlobalEventHandlersEventMap {
    "shiny-chat-input-sent": CustomEvent<Message>;
    "shiny-chat-append-message": CustomEvent<Message>;
    "shiny-chat-append-message-chunk": CustomEvent<Message>;
    "shiny-chat-clear-messages": CustomEvent;
    "shiny-chat-update-user-input": CustomEvent<UpdateUserInput>;
    "shiny-chat-remove-loading-message": CustomEvent;
  }
}

const CHAT_MESSAGE_TAG = "shiny-chat-message";
const CHAT_USER_MESSAGE_TAG = "shiny-user-message";
const CHAT_MESSAGES_TAG = "shiny-chat-messages";
const CHAT_INPUT_TAG = "shiny-chat-input";
const CHAT_CONTAINER_TAG = "shiny-chat-container";

const ICONS = {
  robot:
    '<svg fill="currentColor" class="bi bi-robot" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135"/><path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"/></svg>',
  // https://github.com/n3r4zzurr0/svg-spinners/blob/main/svg-css/3-dots-fade.svg
  dots_fade:
    '<svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_S1WN{animation:spinner_MGfb .8s linear infinite;animation-delay:-.8s}.spinner_Km9P{animation-delay:-.65s}.spinner_JApP{animation-delay:-.5s}@keyframes spinner_MGfb{93.75%,100%{opacity:.2}}</style><circle class="spinner_S1WN" cx="4" cy="12" r="3"/><circle class="spinner_S1WN spinner_Km9P" cx="12" cy="12" r="3"/><circle class="spinner_S1WN spinner_JApP" cx="20" cy="12" r="3"/></svg>',
};

class ChatMessage extends LightElement {
  @property() content = "...";
  @property({ attribute: "content-type" }) contentType: ContentType =
    "markdown";
  @property({ type: Boolean, reflect: true }) streaming = false;
  @property() icon = "";

  render() {
    // Show dots until we have content
    const isEmpty = this.content.trim().length === 0;
    const icon = isEmpty ? ICONS.dots_fade : this.icon || ICONS.robot;

    return html`
      <div class="message-icon">${unsafeHTML(icon)}</div>
      <shiny-markdown-stream
        content=${this.content}
        content-type=${this.contentType}
        ?streaming=${this.streaming}
        auto-scroll
        .onContentChange=${this.#onContentChange.bind(this)}
        .onStreamEnd=${this.#makeSuggestionsAccessible.bind(this)}
      ></shiny-markdown-stream>
    `;
  }

  #onContentChange(): void {
    if (!this.streaming) this.#makeSuggestionsAccessible();
  }

  #makeSuggestionsAccessible(): void {
    this.querySelectorAll(".suggestion,[data-suggestion]").forEach((el) => {
      if (!(el instanceof HTMLElement)) return;
      if (el.hasAttribute("tabindex")) return;

      el.setAttribute("tabindex", "0");
      el.setAttribute("role", "button");

      const suggestion = el.dataset.suggestion || el.textContent;
      el.setAttribute("aria-label", `Use chat suggestion: ${suggestion}`);
    });
  }
}

class ChatUserMessage extends LightElement {
  @property() content = "...";

  render() {
    return html`
      <shiny-markdown-stream
        content=${this.content}
        content-type="semi-markdown"
      ></shiny-markdown-stream>
    `;
  }
}

class ChatMessages extends LightElement {
  render() {
    return html``;
  }
}

interface ChatInputSetInputOptions {
  submit?: boolean;
  focus?: boolean;
}

class ChatInput extends LightElement {
  @property() placeholder = "Enter a message...";
  // disabled is reflected manually because `reflect: true` doesn't work with LightElement
  @property({ type: Boolean })
  get disabled() {
    return this._disabled;
  }

  set disabled(value: boolean) {
    const oldValue = this._disabled;
    if (value === oldValue) {
      return;
    }

    this._disabled = value;
    value
      ? this.setAttribute("disabled", "")
      : this.removeAttribute("disabled");

    this.requestUpdate("disabled", oldValue);
    this.#onInput();
  }

  private _disabled = false;
  inputVisibleObserver?: IntersectionObserver;

  connectedCallback(): void {
    super.connectedCallback();

    this.inputVisibleObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) this.#updateHeight();
      });
    });

    this.inputVisibleObserver.observe(this);
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this.inputVisibleObserver?.disconnect();
    this.inputVisibleObserver = undefined;
  }

  attributeChangedCallback(
    name: string,
    _old: string | null,
    value: string | null
  ) {
    super.attributeChangedCallback(name, _old, value);
    if (name === "disabled") {
      this.disabled = value !== null;
    }
  }

  private get textarea(): HTMLTextAreaElement {
    return this.querySelector("textarea") as HTMLTextAreaElement;
  }

  private get value(): string {
    return this.textarea.value;
  }

  private get valueIsEmpty(): boolean {
    return this.value.trim().length === 0;
  }

  private get button(): HTMLButtonElement {
    return this.querySelector("button") as HTMLButtonElement;
  }

  render() {
    const icon =
      '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-arrow-up-circle-fill" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0m-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707z"/></svg>';

    return html`
      <textarea
        id="${this.id}"
        class="form-control"
        rows="1"
        placeholder="${this.placeholder}"
        @keydown=${this.#onKeyDown}
        @input=${this.#onInput}
        data-shiny-no-bind-input
      ></textarea>
      <button
        type="button"
        title="Send message"
        aria-label="Send message"
        @click=${this.#sendInput}
      >
        ${unsafeHTML(icon)}
      </button>
    `;
  }

  // Pressing enter sends the message (if not empty)
  #onKeyDown(e: KeyboardEvent): void {
    const isEnter = e.code === "Enter" && !e.shiftKey;
    if (isEnter && !this.valueIsEmpty) {
      e.preventDefault();
      this.#sendInput();
    }
  }

  #onInput(): void {
    this.#updateHeight();
    this.button.disabled = this.disabled
      ? true
      : this.value.trim().length === 0;
  }

  // Determine whether the button should be enabled/disabled on first render
  protected firstUpdated(): void {
    this.#onInput();
  }

  #sendInput(focus = true): void {
    if (this.valueIsEmpty) return;
    if (this.disabled) return;

    window.Shiny.setInputValue!(this.id, this.value, { priority: "event" });

    // Emit event so parent element knows to insert the message
    const sentEvent = new CustomEvent("shiny-chat-input-sent", {
      detail: { content: this.value, role: "user" },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(sentEvent);

    this.setInputValue("");
    this.disabled = true;

    if (focus) this.textarea.focus();
  }

  #updateHeight(): void {
    const el = this.textarea;
    if (el.scrollHeight == 0) {
      return;
    }
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }

  setInputValue(
    value: string,
    { submit = false, focus = false }: ChatInputSetInputOptions = {}
  ): void {
    // Store previous value to restore post-submit (if submitting)
    const oldValue = this.textarea.value;

    this.textarea.value = value;

    // Simulate an input event (to trigger the textarea autoresize)
    const inputEvent = new Event("input", { bubbles: true, cancelable: true });
    this.textarea.dispatchEvent(inputEvent);

    if (submit) {
      this.#sendInput(false);
      if (oldValue) this.setInputValue(oldValue);
    }

    if (focus) {
      this.textarea.focus();
    }
  }
}

class ChatContainer extends LightElement {
  @property({ attribute: "icon-assistant" }) iconAssistant = "";
  inputSentinelObserver?: IntersectionObserver;

  private get input(): ChatInput {
    return this.querySelector(CHAT_INPUT_TAG) as ChatInput;
  }

  private get messages(): ChatMessages {
    return this.querySelector(CHAT_MESSAGES_TAG) as ChatMessages;
  }

  private get lastMessage(): ChatMessage | null {
    const last = this.messages.lastElementChild;
    return last ? (last as ChatMessage) : null;
  }

  render() {
    return html``;
  }

  connectedCallback(): void {
    super.connectedCallback();

    // We use a sentinel element that we place just above the shiny-chat-input. When it
    // moves off-screen we know that the text area input is now floating, add shadow.
    let sentinel = this.querySelector<HTMLElement>("div");
    if (!sentinel) {
      sentinel = createElement("div", {
        style: "width: 100%; height: 0;",
      }) as HTMLElement;
      this.input.insertAdjacentElement("afterend", sentinel);
    }

    this.inputSentinelObserver = new IntersectionObserver(
      (entries) => {
        const inputTextarea = this.input.querySelector("textarea");
        if (!inputTextarea) return;
        const addShadow = entries[0]?.intersectionRatio === 0;
        inputTextarea.classList.toggle("shadow", addShadow);
      },
      {
        threshold: [0, 1],
        rootMargin: "0px",
      }
    );

    this.inputSentinelObserver.observe(sentinel);
  }

  firstUpdated(): void {
    // Don't attach event listeners until child elements are rendered
    if (!this.messages) return;

    this.addEventListener("shiny-chat-input-sent", this.#onInputSent);
    this.addEventListener("shiny-chat-append-message", this.#onAppend);
    this.addEventListener(
      "shiny-chat-append-message-chunk",
      this.#onAppendChunk
    );
    this.addEventListener("shiny-chat-clear-messages", this.#onClear);
    this.addEventListener(
      "shiny-chat-update-user-input",
      this.#onUpdateUserInput
    );
    this.addEventListener(
      "shiny-chat-remove-loading-message",
      this.#onRemoveLoadingMessage
    );
    this.addEventListener("click", this.#onInputSuggestionClick);
    this.addEventListener("keydown", this.#onInputSuggestionKeydown);
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();

    this.inputSentinelObserver?.disconnect();
    this.inputSentinelObserver = undefined;

    this.removeEventListener("shiny-chat-input-sent", this.#onInputSent);
    this.removeEventListener("shiny-chat-append-message", this.#onAppend);
    this.removeEventListener(
      "shiny-chat-append-message-chunk",
      this.#onAppendChunk
    );
    this.removeEventListener("shiny-chat-clear-messages", this.#onClear);
    this.removeEventListener(
      "shiny-chat-update-user-input",
      this.#onUpdateUserInput
    );
    this.removeEventListener(
      "shiny-chat-remove-loading-message",
      this.#onRemoveLoadingMessage
    );
    this.removeEventListener("click", this.#onInputSuggestionClick);
    this.removeEventListener("keydown", this.#onInputSuggestionKeydown);
  }

  // When user submits input, append it to the chat, and add a loading message
  #onInputSent(event: CustomEvent<Message>): void {
    this.#appendMessage(event.detail);
    this.#addLoadingMessage();
  }

  // Handle an append message event from server
  #onAppend(event: CustomEvent<Message>): void {
    this.#appendMessage(event.detail);
  }

  #initMessage(): void {
    this.#removeLoadingMessage();
    if (!this.input.disabled) {
      this.input.disabled = true;
    }
  }

  #appendMessage(message: Message, finalize = true): void {
    this.#initMessage();

    const TAG_NAME =
      message.role === "user" ? CHAT_USER_MESSAGE_TAG : CHAT_MESSAGE_TAG;

    if (this.iconAssistant) {
      message.icon = message.icon || this.iconAssistant;
    }

    const msg = createElement(TAG_NAME, message);
    this.messages.appendChild(msg);

    if (finalize) {
      this.#finalizeMessage();
    }
  }

  // Loading message is just an empty message
  #addLoadingMessage(): void {
    const loading_message = {
      content: "",
      role: "assistant",
    };
    const message = createElement(CHAT_MESSAGE_TAG, loading_message);
    this.messages.appendChild(message);
  }

  #removeLoadingMessage(): void {
    const content = this.lastMessage?.content;
    if (!content) this.lastMessage?.remove();
  }

  #onAppendChunk(event: CustomEvent<Message>): void {
    this.#appendMessageChunk(event.detail);
  }

  #appendMessageChunk(message: Message): void {
    if (message.chunk_type === "message_start") {
      this.#appendMessage(message, false);
    }

    const lastMessage = this.lastMessage;
    if (!lastMessage) throw new Error("No messages found in the chat output");

    if (message.chunk_type === "message_start") {
      lastMessage.setAttribute("streaming", "");
      return;
    }

    const content =
      message.operation === "append"
        ? lastMessage.getAttribute("content") + message.content
        : message.content;

    lastMessage.setAttribute("content", content);

    if (message.chunk_type === "message_end") {
      this.lastMessage?.removeAttribute("streaming");
      this.#finalizeMessage();
    }
  }

  #onClear(): void {
    this.messages.innerHTML = "";
  }

  #onUpdateUserInput(event: CustomEvent<UpdateUserInput>): void {
    const { value, placeholder, submit, focus } = event.detail;
    if (value !== undefined) {
      this.input.setInputValue(value, { submit, focus });
    }
    if (placeholder !== undefined) {
      this.input.placeholder = placeholder;
    }
  }

  #onInputSuggestionClick(e: MouseEvent): void {
    this.#onInputSuggestionEvent(e);
  }

  #onInputSuggestionKeydown(e: KeyboardEvent): void {
    const isEnterOrSpace = e.key === "Enter" || e.key === " ";
    if (!isEnterOrSpace) return;

    this.#onInputSuggestionEvent(e);
  }

  #onInputSuggestionEvent(e: MouseEvent | KeyboardEvent): void {
    const { suggestion, submit } = this.#getSuggestion(e.target);
    if (!suggestion) return;

    e.preventDefault();
    // Cmd/Ctrl + (event) = force submitting
    // Alt/Opt  + (event) = force setting without submitting
    const shouldSubmit =
      e.metaKey || e.ctrlKey ? true : e.altKey ? false : submit;

    this.input.setInputValue(suggestion, {
      submit: shouldSubmit,
      focus: !shouldSubmit,
    });
  }

  #getSuggestion(x: EventTarget | null): {
    suggestion?: string;
    submit?: boolean;
  } {
    if (!(x instanceof HTMLElement)) return {};

    const el = x.closest(".suggestion, [data-suggestion]");
    if (!(el instanceof HTMLElement)) return {};

    const isSuggestion =
      el.classList.contains("suggestion") ||
      el.dataset.suggestion !== undefined;
    if (!isSuggestion) return {};

    const suggestion = el.dataset.suggestion || el.textContent;

    return {
      suggestion: suggestion || undefined,
      submit:
        el.classList.contains("submit") ||
        el.dataset.suggestionSubmit === "" ||
        el.dataset.suggestionSubmit === "true",
    };
  }

  #onRemoveLoadingMessage(): void {
    this.#removeLoadingMessage();
    this.#finalizeMessage();
  }

  #finalizeMessage(): void {
    this.input.disabled = false;
  }
}

// ------- Register custom elements and shiny bindings ---------

const chatCustomElements = [
  { tag: CHAT_MESSAGE_TAG, component: ChatMessage },
  { tag: CHAT_USER_MESSAGE_TAG, component: ChatUserMessage },
  { tag: CHAT_MESSAGES_TAG, component: ChatMessages },
  { tag: CHAT_INPUT_TAG, component: ChatInput },
  { tag: CHAT_CONTAINER_TAG, component: ChatContainer }
];

chatCustomElements.forEach(({ tag, component }) => {
  if (!customElements.get(tag)) {
    customElements.define(tag, component);
  }
});

window.Shiny.addCustomMessageHandler(
  "shinyChatMessage",
  async function (message: ShinyChatMessage) {
    if (message.obj?.html_deps) {
      await renderDependencies(message.obj.html_deps);
    }

    const evt = new CustomEvent(message.handler, {
      detail: message.obj,
    });

    const el = document.getElementById(message.id);

    if (!el) {
      showShinyClientMessage({
        status: "error",
        message: `Unable to handle Chat() message since element with id
          ${message.id} wasn't found. Do you need to call .ui() (Express) or need a
          chat_ui('${message.id}') in the UI (Core)?
        `,
      });
      return;
    }

    el.dispatchEvent(evt);
  }
);

export { CHAT_CONTAINER_TAG };
